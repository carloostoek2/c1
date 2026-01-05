"""
Servicio de gestión de conversión y triggers de ofertas.

Gestiona flujos de conversión orgánica basados en:
- Progreso narrativo del usuario
- Nivel de engagement
- Arquetipos detectados
- Milestones de participación
- Expiración de VIP
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from bot.database.models import ConversionEvent
from bot.services.lucien_voice import LucienVoiceService
from bot.services.discount import DiscountService

logger = logging.getLogger(__name__)


class ConversionService:
    """
    Servicio de conversión con monetización orgánica y digna.

    Implementa triggers inteligentes que:
    - Respetan al usuario (no spam)
    - Se sienten ganados (por progreso)
    - Son personalizados (por arquetipo)
    - Tienen rate limiting (máximo 1 por semana)
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio de conversión.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session
        self.lucien = LucienVoiceService()
        self.discount_service = DiscountService(session)

    async def check_conversion_triggers(
        self,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Verifica qué triggers de conversión aplican para el usuario.

        Args:
            user_id: ID del usuario

        Returns:
            List[Dict]: Lista de triggers activos con sus detalles
        """
        triggers = []

        # Trigger 1: Nivel narrativo 3 completado (Free → VIP)
        if await self._check_narrative_level_3_trigger(user_id):
            triggers.append({
                "type": "narrative_level_3_complete",
                "priority": 1,
                "offer_type": "free_to_vip",
                "message_key": "free_to_vip",
            })

        # Trigger 2: High engagement (5+ días activo, 20+ decisiones)
        if await self._check_high_engagement_trigger(user_id):
            triggers.append({
                "type": "high_engagement",
                "priority": 2,
                "offer_type": "free_to_vip_discount",
                "message_key": "free_to_vip",
                "discount": 0.15,
            })

        # Trigger 3: Arquetipo ROMANTIC (Llaves narrativas)
        if await self._check_romantic_archetype_trigger(user_id):
            triggers.append({
                "type": "archetype_romantic",
                "priority": 3,
                "offer_type": "narrative_keys",
                "message_key": "shop_recommendation",
                "recommended_items": ["Fragmento I", "Fragmento II", "Llave de la Primera Vez"],
            })

        # Trigger 4: Arquetipo EXPLORER (Reliquias)
        if await self._check_explorer_archetype_trigger(user_id):
            triggers.append({
                "type": "archetype_explorer",
                "priority": 3,
                "offer_type": "narrative_relics",
                "message_key": "shop_recommendation",
                "recommended_items": ["El Primer Secreto", "Fragmento del Espejo", "Llave Maestra"],
            })

        # Trigger 5: Streak milestone (14+ días)
        if await self._check_streak_milestone_trigger(user_id):
            triggers.append({
                "type": "streak_milestone",
                "priority": 4,
                "offer_type": "exclusive_badge",
                "message_key": "shop_recommendation",
                "recommended_items": ["Emblema del Iniciado", "Sigilo del Confidente"],
            })

        # Trigger 6: VIP por expirar (3 días antes)
        if await self._check_vip_expiring_trigger(user_id):
            triggers.append({
                "type": "vip_expiring",
                "priority": 1,
                "offer_type": "vip_renewal",
                "message_key": "vip_renewal",
            })

        # Ordenar por prioridad (menor = más importante)
        triggers.sort(key=lambda t: t["priority"])

        return triggers

    async def get_offer_for_user(
        self,
        user_id: int,
        offer_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene la oferta específica para el usuario.

        Args:
            user_id: ID del usuario
            offer_type: Tipo de oferta

        Returns:
            Dict: Oferta con mensaje, descuento, items recomendados, etc.
                  None si no debe mostrarse (rate limiting)
        """
        # Verificar rate limiting
        if not await self.should_show_offer(user_id, offer_type):
            logger.debug(f"Rate limit activo para user {user_id}, offer {offer_type}")
            return None

        offer = {
            "offer_type": offer_type,
            "user_id": user_id,
            "discount": 0.0,
            "message": "",
            "details": {},
        }

        # Free → VIP
        if offer_type == "free_to_vip":
            archetype = await self._get_user_archetype(user_id)
            message = await self.lucien.get_conversion_message("free_to_vip", archetype)

            offer["message"] = message
            offer["details"]["archetype"] = archetype

        # Free → VIP con descuento
        elif offer_type == "free_to_vip_discount":
            offer["discount"] = 0.15
            offer["message"] = await self.lucien.get_conversion_message("free_to_vip")
            offer["details"]["discount_reason"] = "Alto engagement"

        # VIP Renewal
        elif offer_type == "vip_renewal":
            days_remaining, discount = await self._get_vip_renewal_info(user_id)
            message = await self.lucien.get_conversion_message(
                "vip_renewal",
                data={"days_remaining": days_remaining, "discount_percent": discount}
            )

            offer["discount"] = discount / 100.0
            offer["message"] = message
            offer["details"]["days_remaining"] = days_remaining

        # Shop recommendations (llaves, reliquias, badges)
        elif offer_type in ["narrative_keys", "narrative_relics", "exclusive_badge"]:
            # Obtener items recomendados según tipo
            recommended_items = await self._get_recommended_shop_items(user_id, offer_type)
            offer["details"]["recommended_items"] = recommended_items
            offer["message"] = "Diana ha preparado algo especial para ti."

        return offer

    async def record_conversion_event(
        self,
        user_id: int,
        event_type: str,
        offer_type: str,
        details: Optional[Dict[str, Any]] = None,
        discount_applied: float = 0.0
    ) -> None:
        """
        Registra un evento de conversión para análisis y rate limiting.

        Args:
            user_id: ID del usuario
            event_type: "offer_shown", "offer_accepted", "offer_declined"
            offer_type: Tipo de oferta
            details: Detalles adicionales (JSON)
            discount_applied: Descuento aplicado
        """
        try:
            event = ConversionEvent(
                user_id=user_id,
                event_type=event_type,
                offer_type=offer_type,
                offer_details=details or {},
                discount_applied=discount_applied,
            )

            self.session.add(event)
            await self.session.commit()

            logger.info(
                f"Conversion event registrado: user={user_id}, "
                f"type={event_type}, offer={offer_type}"
            )

        except Exception as e:
            logger.error(f"Error registrando conversion event: {e}", exc_info=True)
            await self.session.rollback()

    async def get_conversion_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de conversión del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Dict: Estadísticas de ofertas mostradas, aceptadas, rechazadas
        """
        try:
            # Ofertas mostradas
            stmt_shown = select(ConversionEvent).where(
                and_(
                    ConversionEvent.user_id == user_id,
                    ConversionEvent.event_type == "offer_shown"
                )
            )
            result_shown = await self.session.execute(stmt_shown)
            shown_count = len(result_shown.scalars().all())

            # Ofertas aceptadas
            stmt_accepted = select(ConversionEvent).where(
                and_(
                    ConversionEvent.user_id == user_id,
                    ConversionEvent.event_type == "offer_accepted"
                )
            )
            result_accepted = await self.session.execute(stmt_accepted)
            accepted_count = len(result_accepted.scalars().all())

            # Ofertas rechazadas
            stmt_declined = select(ConversionEvent).where(
                and_(
                    ConversionEvent.user_id == user_id,
                    ConversionEvent.event_type == "offer_declined"
                )
            )
            result_declined = await self.session.execute(stmt_declined)
            declined_count = len(result_declined.scalars().all())

            return {
                "offers_shown": shown_count,
                "offers_accepted": accepted_count,
                "offers_declined": declined_count,
                "conversion_rate": accepted_count / shown_count if shown_count > 0 else 0.0,
            }

        except Exception as e:
            logger.error(f"Error obteniendo conversion stats: {e}", exc_info=True)
            return {
                "offers_shown": 0,
                "offers_accepted": 0,
                "offers_declined": 0,
                "conversion_rate": 0.0,
            }

    async def should_show_offer(
        self,
        user_id: int,
        offer_type: str
    ) -> bool:
        """
        Determina si se debe mostrar una oferta (rate limiting + dignidad).

        Reglas:
        - Máximo 1 oferta del mismo tipo por semana
        - Si rechazó una oferta, esperar 7 días
        - Si aceptó, no mostrar otra por 30 días

        Args:
            user_id: ID del usuario
            offer_type: Tipo de oferta

        Returns:
            bool: True si se puede mostrar
        """
        try:
            seven_days_ago = datetime.utcnow() - timedelta(days=7)

            stmt = select(ConversionEvent).where(
                and_(
                    ConversionEvent.user_id == user_id,
                    ConversionEvent.offer_type == offer_type,
                    ConversionEvent.created_at >= seven_days_ago
                )
            )

            result = await self.session.execute(stmt)
            recent_event = result.scalar_one_or_none()

            if recent_event:
                # Si aceptó, no mostrar otra por 30 días
                if recent_event.event_type == "offer_accepted":
                    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                    return recent_event.created_at < thirty_days_ago

                # Si rechazó, esperar 7 días
                return False

            # Sin eventos recientes, mostrar
            return True

        except Exception as e:
            logger.error(f"Error verificando rate limit: {e}", exc_info=True)
            return True  # Ser permisivos en caso de error

    # ========================================
    # MÉTODOS PRIVADOS - TRIGGERS
    # ========================================

    async def _check_narrative_level_3_trigger(self, user_id: int) -> bool:
        """Verifica si el usuario completó nivel narrativo 3."""
        try:
            from bot.narrative.services.progress import ProgressService
            from bot.services.subscription import SubscriptionService

            progress_service = ProgressService(self.session)
            subscription_service = SubscriptionService(self.session, None)

            progress = await progress_service.get_or_create_progress(user_id)
            is_vip = await subscription_service.is_vip_active(user_id)

            # Trigger: Completó nivel 3 y NO es VIP
            return progress.chapters_completed >= 3 and not is_vip

        except Exception as e:
            logger.error(f"Error checking narrative level 3 trigger: {e}")
            return False

    async def _check_high_engagement_trigger(self, user_id: int) -> bool:
        """Verifica si el usuario tiene alto engagement (5+ días activo, 20+ decisiones)."""
        try:
            from bot.narrative.services.progress import ProgressService
            from bot.gamification.database.models import UserStreak

            progress_service = ProgressService(self.session)

            progress = await progress_service.get_or_create_progress(user_id)

            # Obtener streak actual
            from sqlalchemy import select
            stmt = select(UserStreak).where(UserStreak.user_id == user_id)
            result = await self.session.execute(stmt)
            user_streak = result.scalar_one_or_none()

            current_streak = user_streak.current_streak if user_streak else 0

            # Alto engagement: 5+ días activo y 20+ decisiones
            return current_streak >= 5 and progress.total_decisions >= 20

        except Exception as e:
            logger.error(f"Error checking high engagement trigger: {e}")
            return False

    async def _check_romantic_archetype_trigger(self, user_id: int) -> bool:
        """Verifica si el usuario es ROMANTIC con confianza alta."""
        try:
            from bot.services.archetype_advanced import AdvancedArchetypeService
            from bot.narrative.database.enums import ArchetypeType

            archetype_service = AdvancedArchetypeService(self.session)
            archetype, confidence = await archetype_service.get_dominant_archetype(user_id)

            return archetype == ArchetypeType.ROMANTIC and confidence >= 0.7

        except Exception as e:
            logger.error(f"Error checking romantic archetype trigger: {e}")
            return False

    async def _check_explorer_archetype_trigger(self, user_id: int) -> bool:
        """Verifica si el usuario es EXPLORER con confianza alta."""
        try:
            from bot.services.archetype_advanced import AdvancedArchetypeService
            from bot.narrative.database.enums import ArchetypeType

            archetype_service = AdvancedArchetypeService(self.session)
            archetype, confidence = await archetype_service.get_dominant_archetype(user_id)

            return archetype == ArchetypeType.EXPLORER and confidence >= 0.7

        except Exception as e:
            logger.error(f"Error checking explorer archetype trigger: {e}")
            return False

    async def _check_streak_milestone_trigger(self, user_id: int) -> bool:
        """Verifica si el usuario alcanzó milestone de streak (14+ días)."""
        try:
            from bot.gamification.database.models import UserStreak
            from sqlalchemy import select

            stmt = select(UserStreak).where(UserStreak.user_id == user_id)
            result = await self.session.execute(stmt)
            user_streak = result.scalar_one_or_none()

            if not user_streak:
                return False

            return user_streak.current_streak >= 14

        except Exception as e:
            logger.error(f"Error checking streak milestone trigger: {e}")
            return False

    async def _check_vip_expiring_trigger(self, user_id: int) -> bool:
        """Verifica si la suscripción VIP expira en 3 días."""
        try:
            from bot.services.subscription import SubscriptionService

            subscription_service = SubscriptionService(self.session, None)
            vip_subscriber = await subscription_service.get_vip_subscriber(user_id)

            if not vip_subscriber:
                return False

            days_remaining = (vip_subscriber.expiry_date - datetime.utcnow()).days
            return 0 < days_remaining <= 3

        except Exception as e:
            logger.error(f"Error checking VIP expiring trigger: {e}")
            return False

    # ========================================
    # HELPERS
    # ========================================

    async def _get_user_archetype(self, user_id: int) -> str:
        """Obtiene el arquetipo dominante del usuario."""
        try:
            from bot.services.archetype_advanced import AdvancedArchetypeService

            archetype_service = AdvancedArchetypeService(self.session)
            archetype, confidence = await archetype_service.get_dominant_archetype(user_id)

            if confidence >= 0.6:
                return archetype.value
            else:
                return "unknown"

        except Exception as e:
            logger.error(f"Error getting user archetype: {e}")
            return "unknown"

    async def _get_vip_renewal_info(self, user_id: int) -> tuple:
        """Obtiene días restantes y descuento de renovación."""
        try:
            from bot.services.subscription import SubscriptionService
            from bot.services.personalization import PersonalizationService

            subscription_service = SubscriptionService(self.session, None)
            personalization_service = PersonalizationService(self.session)

            vip_subscriber = await subscription_service.get_vip_subscriber(user_id)

            if not vip_subscriber:
                return 0, 0

            days_remaining = (vip_subscriber.expiry_date - datetime.utcnow()).days
            discount = await personalization_service._calculate_loyalty_discount(user_id)

            return days_remaining, discount

        except Exception as e:
            logger.error(f"Error getting VIP renewal info: {e}")
            return 0, 0

    async def _get_recommended_shop_items(
        self,
        user_id: int,
        offer_type: str
    ) -> List[str]:
        """Obtiene items recomendados según tipo de oferta."""
        # Mapeo de offer_type a categorías
        offer_to_items = {
            "narrative_keys": ["Fragmento I", "Fragmento II", "Fragmento III", "Archivo Oculto", "Llave de la Primera Vez"],
            "narrative_relics": ["El Primer Secreto", "Fragmento del Espejo", "La Carta No Enviada", "Cristal de Medianoche", "Llave Maestra"],
            "exclusive_badge": ["Emblema del Iniciado", "Sigilo del Confidente", "Insignia del Devoto", "Corona del Guardián"],
        }

        return offer_to_items.get(offer_type, [])
