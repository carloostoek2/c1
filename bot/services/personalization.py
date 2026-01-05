"""
Servicio de personalización de contenido.

Integra detección de arquetipos con la voz de Lucien para
ofrecer experiencias personalizadas según la personalidad del usuario.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.archetype_advanced import AdvancedArchetypeService
from bot.services.lucien_voice import LucienVoiceService
from bot.narrative.database.enums import ArchetypeType

logger = logging.getLogger(__name__)


class PersonalizationService:
    """Servicio de personalización basada en arquetipos."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session
        self.archetype_service = AdvancedArchetypeService(session)
        self.lucien_voice = LucienVoiceService()

    async def get_personalized_content(
        self, user_id: int, content_key: str
    ) -> str:
        """
        Obtiene contenido personalizado basado en el arquetipo del usuario.

        Args:
            user_id: ID del usuario
            content_key: Clave del contenido a personalizar

        Returns:
            str: Contenido personalizado
        """
        # Obtener arquetipo del usuario
        archetype, confidence = await self.archetype_service.get_dominant_archetype(
            user_id
        )

        # Si la confianza es baja, usar contenido genérico
        if confidence < 0.6:
            archetype = ArchetypeType.UNKNOWN

        # Obtener contenido base
        base_content = await self._get_base_content(content_key)

        # Personalizar según arquetipo
        if archetype == ArchetypeType.UNKNOWN:
            return base_content

        personalized = await self.lucien_voice.personalize_by_archetype(
            base_content, archetype.value
        )

        return personalized

    async def get_conversion_trigger(
        self, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene el trigger de conversión apropiado para el usuario.

        Evalúa el contexto del usuario y decide si debe mostrarse
        una oferta de conversión (Free→VIP, VIP→Premium, etc.)

        Args:
            user_id: ID del usuario

        Returns:
            dict: Trigger de conversión o None si no aplica
                - type: Tipo de conversión
                - message: Mensaje personalizado
                - offer_data: Datos de la oferta
        """
        from bot.narrative.services.progress import ProgressService
        from bot.services.subscription import SubscriptionService

        progress_service = ProgressService(self.session)
        subscription_service = SubscriptionService(self.session, None)

        # Obtener estado del usuario
        progress = await progress_service.get_or_create_progress(user_id)
        is_vip = await subscription_service.is_vip_active(user_id)

        # Obtener arquetipo
        archetype, confidence = await self.archetype_service.get_dominant_archetype(
            user_id
        )

        # ========================================
        # TRIGGER: Free → VIP
        # ========================================
        if not is_vip:
            # Condiciones: completó capítulo 3 (nivel narrativo 3)
            if progress.chapters_completed and progress.chapters_completed >= 3:
                message = await self.lucien_voice.get_conversion_message(
                    "free_to_vip",
                    archetype=archetype.value if confidence >= 0.6 else None,
                )

                return {
                    "type": "free_to_vip",
                    "message": message,
                    "offer_data": {
                        "archetype": archetype.value,
                        "confidence": confidence,
                    },
                }

        # ========================================
        # TRIGGER: VIP Renewal
        # ========================================
        if is_vip:
            vip_subscriber = await subscription_service.get_vip_subscriber(
                user_id
            )
            if vip_subscriber:
                days_remaining = (
                    vip_subscriber.expiry_date - datetime.utcnow()
                ).days

                # Si expira en 3 días o menos
                if 0 < days_remaining <= 3:
                    # Calcular descuento por lealtad
                    discount = await self._calculate_loyalty_discount(
                        user_id
                    )

                    message = await self.lucien_voice.get_conversion_message(
                        "vip_renewal",
                        data={
                            "days_remaining": days_remaining,
                            "discount_percent": discount,
                        },
                    )

                    return {
                        "type": "vip_renewal",
                        "message": message,
                        "offer_data": {
                            "days_remaining": days_remaining,
                            "discount_percent": discount,
                        },
                    }

        return None

    async def get_recommended_items(
        self, user_id: int, limit: int = 5
    ) -> List[Dict]:
        """
        Obtiene items recomendados del shop basados en el arquetipo.

        Args:
            user_id: ID del usuario
            limit: Número máximo de items

        Returns:
            List[dict]: Items recomendados con scores de relevancia
        """
        # Obtener arquetipo
        archetype, confidence = await self.archetype_service.get_dominant_archetype(
            user_id
        )

        # Mapeo de arquetipos a categorías de items
        archetype_preferences = {
            ArchetypeType.EXPLORER: ["llaves", "reliquias", "fragmentos"],
            ArchetypeType.ROMANTIC: ["distintivos", "llaves", "confesiones"],
            ArchetypeType.ANALYTICAL: ["archivos", "fragmentos", "mapas"],
            ArchetypeType.PERSISTENT: ["distintivos", "sellos", "emblemas"],
            ArchetypeType.DIRECT: ["pases", "accesos", "prioridades"],
            ArchetypeType.PATIENT: ["reliquias", "archivos", "cristales"],
        }

        preferred_categories = archetype_preferences.get(
            archetype, ["distintivos"]
        )

        # TODO: Consultar shop_items filtrados por categorías
        # Por ahora retornar estructura placeholder
        recommendations = []

        logger.debug(
            f"Recomendaciones para user {user_id} (arquetipo {archetype.value}): {preferred_categories}"
        )

        return recommendations

    async def should_show_offer(
        self, user_id: int, offer_type: str
    ) -> bool:
        """
        Determina si se debe mostrar una oferta específica al usuario.

        Implementa rate limiting y lógica de dignidad (no spam).

        Args:
            user_id: ID del usuario
            offer_type: Tipo de oferta

        Returns:
            bool: True si se debe mostrar
        """
        # TODO: Implementar rate limiting basado en tabla de conversion_events
        # Por ahora, simple lógica: máximo 1 oferta por semana

        # Regla básica: si rechazó una oferta, no mostrar otra en 7 días
        from bot.database.models import ConversionEvent

        from sqlalchemy import select, and_

        # Verificar si hay oferta reciente (últimos 7 días)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        stmt = select(ConversionEvent).where(
            and_(
                ConversionEvent.user_id == user_id,
                ConversionEvent.offer_type == offer_type,
                ConversionEvent.created_at >= seven_days_ago,
            )
        )

        try:
            result = await self.session.execute(stmt)
            recent_offer = result.scalar_one_or_none()

            if recent_offer:
                # Si aceptó, no mostrar otra igual por 30 días
                if recent_offer.event_type == "offer_accepted":
                    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                    return recent_offer.created_at < thirty_days_ago

                # Si rechazó, esperar 7 días
                return False

        except Exception as e:
            logger.error(f"Error checking offer history: {e}", exc_info=True)

        # Sin historial, mostrar
        return True

    async def get_user_personality_summary(self, user_id: int) -> Dict:
        """
        Obtiene un resumen de la personalidad detectada del usuario.

        Args:
            user_id: ID del usuario

        Returns:
            dict: Resumen de personalidad
                - dominant_archetype: Arquetipo dominante
                - confidence: Confianza
                - traits: Rasgos detectados
                - recommendations: Recomendaciones de contenido
        """
        profile = await self.archetype_service.get_archetype_profile(user_id)

        # Mapear arquetipos a rasgos
        archetype_traits = {
            "explorer": [
                "Curiosidad insaciable",
                "Busca detalles ocultos",
                "Valora el descubrimiento",
            ],
            "direct": [
                "Eficiente con su tiempo",
                "Prefiere claridad",
                "Va al punto",
            ],
            "romantic": [
                "Busca conexión emocional",
                "Valora la vulnerabilidad",
                "Sensible a la intimidad",
            ],
            "analytical": [
                "Lógico y reflexivo",
                "Busca comprensión profunda",
                "Valora la estructura",
            ],
            "persistent": [
                "Determinado",
                "No se rinde fácilmente",
                "Completa lo que empieza",
            ],
            "patient": [
                "Toma su tiempo",
                "Procesamiento profundo",
                "Valora la pausa",
            ],
        }

        dominant = profile["dominant"]
        traits = archetype_traits.get(dominant, [])

        return {
            "dominant_archetype": dominant,
            "confidence": profile["confidence"],
            "traits": traits,
            "scores": profile["scores"],
            "recommendations": await self.get_recommended_items(user_id),
        }

    # ========================================
    # MÉTODOS PRIVADOS
    # ========================================

    async def _get_base_content(self, content_key: str) -> str:
        """Obtiene contenido base sin personalizar."""
        # TODO: Consultar de una tabla de contenido
        # Por ahora, retornar placeholder
        return f"Contenido base para {content_key}"

    async def _calculate_loyalty_discount(self, user_id: int) -> int:
        """
        Calcula descuento por lealtad.

        Args:
            user_id: ID del usuario

        Returns:
            int: Porcentaje de descuento (0-15%)
        """
        from bot.services.subscription import SubscriptionService

        subscription_service = SubscriptionService(self.session, None)
        vip_subscriber = await subscription_service.get_vip_subscriber(user_id)

        if not vip_subscriber:
            return 0

        # Calcular días totales como VIP
        days_as_vip = (
            datetime.utcnow() - vip_subscriber.subscribed_at
        ).days

        # Descuento escalonado por días
        if days_as_vip >= 90:
            return 15
        elif days_as_vip >= 60:
            return 10
        elif days_as_vip >= 30:
            return 5
        else:
            return 0
