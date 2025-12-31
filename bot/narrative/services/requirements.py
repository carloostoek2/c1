"""
Servicio de validación de requisitos para fragmentos narrativos.

Valida si un usuario cumple con los requisitos necesarios para
acceder a un fragmento específico.
"""
import logging
from typing import Optional, Tuple, List, TYPE_CHECKING
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.narrative.database import (
    NarrativeFragment,
    FragmentRequirement,
    RequirementType,
    ArchetypeType,
    UserNarrativeProgress,
)

if TYPE_CHECKING:
    from aiogram import Bot

logger = logging.getLogger(__name__)


class RequirementsService:
    """
    Servicio de validación de requisitos narrativos.

    Métodos:
    - can_access_fragment: Verifica si usuario puede acceder a fragmento
    - validate_requirements: Valida lista de requisitos
    - get_rejection_message: Obtiene mensaje de rechazo apropiado
    - get_fragment_requirements: Obtiene requisitos de un fragmento
    """

    def __init__(self, session: AsyncSession, bot: Optional["Bot"] = None):
        """
        Inicializa servicio.

        Args:
            session: Sesión async de SQLAlchemy
            bot: Instancia del bot (opcional, para integraciones futuras)
        """
        self._session = session
        self._bot = bot

    async def can_access_fragment(
        self,
        user_id: int,
        fragment_key: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifica si usuario puede acceder a un fragmento.

        Args:
            user_id: ID del usuario
            fragment_key: Key del fragmento

        Returns:
            Tupla (puede_acceder, mensaje_rechazo)
            - (True, None) si puede acceder
            - (False, mensaje) si no puede acceder
        """
        # Obtener fragmento y sus requisitos
        requirements = await self.get_fragment_requirements(fragment_key)

        if not requirements:
            # Sin requisitos = acceso libre
            return True, None

        # Validar todos los requisitos
        can_access, rejection_msg = await self.validate_requirements(
            user_id=user_id,
            requirements=requirements
        )

        if can_access:
            logger.debug(
                f"✅ Usuario {user_id} cumple requisitos para {fragment_key}"
            )
        else:
            logger.info(
                f"⛔ Usuario {user_id} NO cumple requisitos para {fragment_key}: {rejection_msg}"
            )

        return can_access, rejection_msg

    async def validate_requirements(
        self,
        user_id: int,
        requirements: List[FragmentRequirement]
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida lista de requisitos.

        TODOS los requisitos deben cumplirse (AND lógico).

        Args:
            user_id: ID del usuario
            requirements: Lista de requisitos a validar

        Returns:
            Tupla (cumple_todos, primer_mensaje_rechazo)
        """
        for req in requirements:
            can_pass, rejection_msg = await self._validate_single_requirement(
                user_id=user_id,
                requirement=req
            )

            if not can_pass:
                # Primer requisito no cumplido
                return False, rejection_msg or req.rejection_message

        # Todos los requisitos cumplidos
        return True, None

    async def _validate_single_requirement(
        self,
        user_id: int,
        requirement: FragmentRequirement
    ) -> Tuple[bool, Optional[str]]:
        """
        Valida un requisito individual.

        Args:
            user_id: ID del usuario
            requirement: Requisito a validar

        Returns:
            Tupla (cumple, mensaje_rechazo)
        """
        req_type = requirement.requirement_type
        value = requirement.value

        try:
            # NONE: Sin requisitos
            if req_type == RequirementType.NONE:
                return True, None

            # VIP_STATUS: Usuario debe ser VIP activo
            elif req_type == RequirementType.VIP_STATUS:
                is_vip = await self._check_vip_status(user_id)
                if not is_vip:
                    return False, (
                        requirement.rejection_message or
                        "🔒 Este contenido es exclusivo para suscriptores VIP"
                    )
                return True, None

            # MIN_BESITOS: Besitos mínimos requeridos
            elif req_type == RequirementType.MIN_BESITOS:
                min_required = int(value)
                has_enough, current_balance = await self._check_besitos(
                    user_id,
                    min_required
                )
                if not has_enough:
                    return False, (
                        requirement.rejection_message or
                        f"💰 Necesitas {min_required} besitos (tienes {current_balance})"
                    )
                return True, None

            # ARCHETYPE: Arquetipo específico requerido
            elif req_type == RequirementType.ARCHETYPE:
                required_archetype = value  # "impulsive", "contemplative", "silent"
                has_archetype = await self._check_archetype(
                    user_id,
                    required_archetype
                )
                if not has_archetype:
                    return False, (
                        requirement.rejection_message or
                        f"🎭 Este camino es para almas {required_archetype}"
                    )
                return True, None

            # DECISION: Decisión previa tomada
            elif req_type == RequirementType.DECISION:
                decision_key = value  # fragment_key de la decisión
                has_taken = await self._check_decision(user_id, decision_key)
                if not has_taken:
                    return False, (
                        requirement.rejection_message or
                        "🚪 Debes tomar otra decisión primero"
                    )
                return True, None

            # ITEM: Posee item de la tienda
            elif req_type == RequirementType.ITEM:
                item_slug = value  # slug del item requerido
                has_item, item_name = await self._check_item_ownership(
                    user_id,
                    item_slug
                )
                if not has_item:
                    return False, (
                        requirement.rejection_message or
                        f"🎒 Necesitas el artefacto '{item_name or item_slug}' para continuar.\n\n"
                        f"Visita la tienda para obtenerlo."
                    )
                return True, None

            # PREMIUM_ACCESS: Compró contenido Premium individual
            elif req_type == RequirementType.PREMIUM_ACCESS:
                item_slug = value  # slug del item premium requerido
                has_premium_access, item_name = await self._check_premium_access(
                    user_id,
                    item_slug
                )
                if not has_premium_access:
                    return False, (
                        requirement.rejection_message or
                        f"📹 Este contenido Premium '{item_name or item_slug}' debe ser adquirido individualmente.\n\n"
                        f"Visita el catálogo Premium para adquirirlo."
                    )
                return True, None

            else:
                logger.warning(f"⚠️ Tipo de requisito desconocido: {req_type}")
                return False, "Requisito no válido"

        except Exception as e:
            logger.error(
                f"❌ Error validando requisito {req_type}: {e}",
                exc_info=True
            )
            return False, "Error al validar requisito"

    async def get_fragment_requirements(
        self,
        fragment_key: str
    ) -> List[FragmentRequirement]:
        """
        Obtiene requisitos de un fragmento.

        Args:
            fragment_key: Key del fragmento

        Returns:
            Lista de requisitos
        """
        from bot.narrative.services.fragment import FragmentService

        fragment_service = FragmentService(self._session)
        fragment = await fragment_service.get_fragment(
            fragment_key,
            load_requirements=True
        )

        if not fragment:
            logger.warning(f"⚠️ Fragmento no encontrado: {fragment_key}")
            return []

        return fragment.requirements or []

    async def get_rejection_message(
        self,
        user_id: int,
        fragment_key: str
    ) -> Optional[str]:
        """
        Obtiene mensaje de rechazo personalizado.

        Args:
            user_id: ID del usuario
            fragment_key: Key del fragmento

        Returns:
            Mensaje de rechazo o None si puede acceder
        """
        can_access, rejection_msg = await self.can_access_fragment(
            user_id,
            fragment_key
        )

        return rejection_msg if not can_access else None

    # ========================================
    # VALIDACIONES ESPECÍFICAS
    # ========================================

    async def _check_vip_status(self, user_id: int) -> bool:
        """
        Verifica si usuario es VIP activo.

        Args:
            user_id: ID del usuario

        Returns:
            True si es VIP activo
        """
        try:
            from bot.database.models import VIPSubscriber

            stmt = select(VIPSubscriber).where(
                VIPSubscriber.user_id == user_id,
                VIPSubscriber.status == "active"
            )
            result = await self._session.execute(stmt)
            vip = result.scalar_one_or_none()

            # Verificar que no haya expirado
            if vip:
                from datetime import datetime
                if vip.expiry_date > datetime.utcnow():
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ Error verificando VIP status: {e}")
            return False

    async def _check_besitos(
        self,
        user_id: int,
        min_required: int
    ) -> Tuple[bool, int]:
        """
        Verifica besitos del usuario.

        Args:
            user_id: ID del usuario
            min_required: Besitos mínimos requeridos

        Returns:
            Tupla (tiene_suficientes, balance_actual)
        """
        try:
            from bot.gamification.services.container import get_container

            gamification = get_container()
            user_gamif = await gamification.user_gamification.get_or_create(user_id)
            current_balance = user_gamif.total_besitos

            return current_balance >= min_required, current_balance

        except Exception as e:
            logger.error(f"❌ Error verificando besitos: {e}")
            return False, 0

    async def _check_archetype(
        self,
        user_id: int,
        required_archetype: str
    ) -> bool:
        """
        Verifica arquetipo del usuario.

        Args:
            user_id: ID del usuario
            required_archetype: Arquetipo requerido ("impulsive", "contemplative", "silent")

        Returns:
            True si tiene el arquetipo requerido
        """
        try:
            stmt = select(UserNarrativeProgress).where(
                UserNarrativeProgress.user_id == user_id
            )
            result = await self._session.execute(stmt)
            progress = result.scalar_one_or_none()

            if not progress:
                # Sin progreso = UNKNOWN
                return required_archetype == "unknown"

            # Comparar arquetipo
            user_archetype = progress.detected_archetype.value
            return user_archetype == required_archetype

        except Exception as e:
            logger.error(f"❌ Error verificando arquetipo: {e}")
            return False

    async def _check_decision(
        self,
        user_id: int,
        decision_key: str
    ) -> bool:
        """
        Verifica si usuario tomó decisión específica.

        Args:
            user_id: ID del usuario
            decision_key: Key del fragmento destino de la decisión

        Returns:
            True si tomó la decisión
        """
        try:
            from bot.narrative.services.progress import ProgressService

            progress_service = ProgressService(self._session)
            return await progress_service.has_taken_decision(user_id, decision_key)

        except Exception as e:
            logger.error(f"❌ Error verificando decisión: {e}")
            return False

    async def _check_item_ownership(
        self,
        user_id: int,
        item_slug: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifica si usuario posee un item de la tienda.

        Args:
            user_id: ID del usuario
            item_slug: Slug del item requerido

        Returns:
            Tupla (tiene_item, nombre_item)
        """
        try:
            from bot.shop.services.container import get_shop_container

            shop = get_shop_container(self._session)

            # Verificar posesión por slug
            has_item = await shop.inventory.has_item_by_slug(user_id, item_slug)

            # Obtener nombre del item para el mensaje
            item = await shop.shop.get_item_by_slug(item_slug)
            item_name = item.name if item else None

            return has_item, item_name

        except Exception as e:
            logger.error(f"❌ Error verificando posesión de item: {e}")
            return False, None

    async def _check_premium_access(
        self,
        user_id: int,
        item_slug: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Verifica si usuario tiene acceso a contenido Premium.

        Args:
            user_id: ID del usuario
            item_slug: Slug del item premium requerido

        Returns:
            Tupla (tiene_acceso, nombre_item)
        """
        try:
            from bot.gamification.services.premium_catalog_service import PremiumCatalogService

            # We need to create a bot instance or pass the existing one
            # For now we'll create a dummy bot, but in real implementation,
            # the bot should be passed from the service initialization
            service = PremiumCatalogService(self._session, self._bot)

            # Get the premium item by slug
            # We might need to adapt this since the premium catalog service uses IDs
            # Let's fetch the item from the database directly
            from bot.shop.database.models import ShopItem
            from sqlalchemy import select

            stmt = select(ShopItem).where(ShopItem.slug == item_slug)
            result = await self._session.execute(stmt)
            item = result.scalar_one_or_none()

            if not item:
                return False, None

            # Check if user has purchased this item
            has_purchased = await service.has_purchased_content(user_id, item.id)

            item_name = item.name if item else None
            return has_purchased, item_name

        except Exception as e:
            logger.error(f"❌ Error verificando acceso a contenido premium: {e}")
            return False, None

    async def get_accessible_fragments(
        self,
        user_id: int,
        chapter_id: int
    ) -> List[str]:
        """
        Obtiene lista de fragmentos accesibles en un capítulo.

        Args:
            user_id: ID del usuario
            chapter_id: ID del capítulo

        Returns:
            Lista de fragment_keys accesibles
        """
        from bot.narrative.database import NarrativeChapter

        # Obtener todos los fragmentos del capítulo
        stmt = (
            select(NarrativeFragment)
            .where(
                NarrativeFragment.chapter_id == chapter_id,
                NarrativeFragment.is_active == True
            )
            .order_by(NarrativeFragment.order)
        )
        result = await self._session.execute(stmt)
        fragments = result.scalars().all()

        accessible = []
        for fragment in fragments:
            can_access, _ = await self.can_access_fragment(
                user_id,
                fragment.fragment_key
            )
            if can_access:
                accessible.append(fragment.fragment_key)

        logger.debug(
            f"📊 Usuario {user_id}: {len(accessible)}/{len(fragments)} "
            f"fragmentos accesibles en capítulo {chapter_id}"
        )

        return accessible
