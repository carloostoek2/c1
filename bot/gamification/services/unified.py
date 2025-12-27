"""
Servicio unificado de recompensas cross-module.

Orquesta RewardService, InventoryService y otros servicios
para otorgar cualquier tipo de recompensa de manera unificada.

Este servicio es el punto de entrada para:
- Otorgar items de tienda como recompensa de misiones
- Futuras integraciones (VIP days, narrative unlocks, etc.)
"""

from typing import Optional, Tuple, Dict, Any
from datetime import datetime, UTC
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from bot.gamification.database.enums import (
    RewardType,
    ObtainedVia,
    TransactionType,
    ShopItemMetadata,
)

logger = logging.getLogger(__name__)


class UnifiedRewardService:
    """
    Servicio unificado para otorgar recompensas cross-module.

    Coordina entre gamificación, tienda y otros módulos para
    entregar recompensas de cualquier tipo de manera consistente.

    Métodos principales:
        - grant_shop_item: Otorga item de tienda como recompensa
        - grant_unified_reward: Otorga cualquier tipo de recompensa
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio.

        Args:
            session: Sesión async de SQLAlchemy
        """
        self.session = session
        self._reward_service = None
        self._inventory_service = None
        self._shop_service = None

    @property
    def reward_service(self):
        """Lazy loading de RewardService."""
        if self._reward_service is None:
            from bot.gamification.services.reward import RewardService
            self._reward_service = RewardService(self.session)
        return self._reward_service

    @property
    def inventory_service(self):
        """Lazy loading de InventoryService."""
        if self._inventory_service is None:
            from bot.shop.services.inventory import InventoryService
            self._inventory_service = InventoryService(self.session)
        return self._inventory_service

    @property
    def shop_service(self):
        """Lazy loading de ShopService."""
        if self._shop_service is None:
            from bot.shop.services.shop import ShopService
            self._shop_service = ShopService(self.session)
        return self._shop_service

    # ========================================
    # SHOP ITEM REWARDS
    # ========================================

    async def grant_shop_item(
        self,
        user_id: int,
        item_id: int,
        quantity: int = 1,
        source: str = "mission_reward",
        reference_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Otorga un item de tienda como recompensa.

        Este método permite dar items de la tienda sin que el usuario
        tenga que comprarlos. Útil para recompensas de misiones,
        eventos o regalos de admin.

        Args:
            user_id: ID del usuario que recibe el item
            item_id: ID del ShopItem a otorgar
            quantity: Cantidad a otorgar (default: 1)
            source: Origen de la recompensa (mission_reward, admin, event)
            reference_id: ID de referencia (mission_id, event_id, etc.)

        Returns:
            (success, message, reward_data)
            reward_data contiene información del item otorgado

        Example:
            >>> unified = UnifiedRewardService(session)
            >>> success, msg, data = await unified.grant_shop_item(
            ...     user_id=123456,
            ...     item_id=5,
            ...     quantity=1,
            ...     source="mission_reward",
            ...     reference_id=42  # mission_id
            ... )
        """
        try:
            # Validar que el item existe
            item = await self.shop_service.get_item(item_id)
            if not item:
                return False, f"Item con ID {item_id} no encontrado", None

            if not item.is_active:
                return False, f"Item '{item.name}' no está disponible", None

            # Verificar límite por usuario
            if item.max_per_user is not None:
                current_qty = await self.inventory_service.get_item_quantity(
                    user_id, item_id
                )
                if current_qty + quantity > item.max_per_user:
                    return (
                        False,
                        f"Límite alcanzado: máximo {item.max_per_user} por usuario",
                        None
                    )

            # Otorgar el item usando InventoryService
            success, msg = await self.inventory_service.grant_item(
                user_id=user_id,
                item_id=item_id,
                quantity=quantity,
                obtained_via=source
            )

            if not success:
                return False, msg, None

            # Construir datos de la recompensa
            reward_data = {
                "type": "shop_item",
                "item_id": item.id,
                "item_slug": item.slug,
                "item_name": item.name,
                "item_icon": item.icon,
                "quantity": quantity,
                "source": source,
                "reference_id": reference_id,
                "granted_at": datetime.now(UTC).isoformat()
            }

            logger.info(
                f"Granted shop item '{item.name}' x{quantity} to user {user_id} "
                f"(source: {source}, ref: {reference_id})"
            )

            return True, f"¡Recibiste {item.icon} {item.name}!", reward_data

        except Exception as e:
            logger.error(f"Error granting shop item: {e}", exc_info=True)
            return False, f"Error al otorgar item: {str(e)}", None

    async def grant_shop_item_by_slug(
        self,
        user_id: int,
        item_slug: str,
        quantity: int = 1,
        source: str = "mission_reward",
        reference_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Otorga un item de tienda por su slug.

        Similar a grant_shop_item pero usando el slug en lugar del ID.

        Args:
            user_id: ID del usuario
            item_slug: Slug del item
            quantity: Cantidad a otorgar
            source: Origen de la recompensa
            reference_id: ID de referencia

        Returns:
            (success, message, reward_data)
        """
        item = await self.shop_service.get_item_by_slug(item_slug)
        if not item:
            return False, f"Item '{item_slug}' no encontrado", None

        return await self.grant_shop_item(
            user_id=user_id,
            item_id=item.id,
            quantity=quantity,
            source=source,
            reference_id=reference_id
        )

    # ========================================
    # UNIFIED REWARD DISPATCHER
    # ========================================

    async def grant_unified_reward(
        self,
        user_id: int,
        reward_type: RewardType,
        reward_config: Dict[str, Any],
        source: str = "mission_reward",
        reference_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Otorga cualquier tipo de recompensa de manera unificada.

        Este es el método principal que debe usarse cuando se quiere
        otorgar una recompensa sin importar su tipo. Delega al
        método apropiado según el tipo de recompensa.

        Args:
            user_id: ID del usuario
            reward_type: Tipo de recompensa (RewardType enum)
            reward_config: Configuración específica del tipo:
                - SHOP_ITEM: {"item_id": int, "quantity": int}
                - BESITOS: {"amount": int}
                - BADGE: {"reward_id": int}
                - (otros tipos se agregarán en futuras fases)
            source: Origen de la recompensa
            reference_id: ID de referencia

        Returns:
            (success, message, reward_data)

        Example:
            >>> # Otorgar item de tienda
            >>> await unified.grant_unified_reward(
            ...     user_id=123,
            ...     reward_type=RewardType.SHOP_ITEM,
            ...     reward_config={"item_id": 5, "quantity": 1},
            ...     source="mission_reward",
            ...     reference_id=42
            ... )

            >>> # Otorgar besitos
            >>> await unified.grant_unified_reward(
            ...     user_id=123,
            ...     reward_type=RewardType.BESITOS,
            ...     reward_config={"amount": 100},
            ...     source="event"
            ... )
        """
        try:
            if reward_type == RewardType.SHOP_ITEM:
                return await self._grant_shop_item_reward(
                    user_id, reward_config, source, reference_id
                )

            elif reward_type == RewardType.BESITOS:
                return await self._grant_besitos_reward(
                    user_id, reward_config, source, reference_id
                )

            elif reward_type == RewardType.BADGE:
                return await self._grant_badge_reward(
                    user_id, reward_config, source, reference_id
                )

            elif reward_type == RewardType.ITEM:
                # ITEM genérico usa el mismo flujo que SHOP_ITEM
                return await self._grant_shop_item_reward(
                    user_id, reward_config, source, reference_id
                )

            else:
                # Para otros tipos, delegar a RewardService si hay reward_id
                if "reward_id" in reward_config:
                    obtained_via = self._source_to_obtained_via(source)
                    return await self._grant_existing_reward(
                        user_id,
                        reward_config["reward_id"],
                        obtained_via,
                        reference_id
                    )

                return (
                    False,
                    f"Tipo de recompensa '{reward_type}' no soportado aún",
                    None
                )

        except Exception as e:
            logger.error(
                f"Error in grant_unified_reward: {e}",
                exc_info=True
            )
            return False, f"Error al otorgar recompensa: {str(e)}", None

    # ========================================
    # PRIVATE GRANT METHODS
    # ========================================

    async def _grant_shop_item_reward(
        self,
        user_id: int,
        config: Dict[str, Any],
        source: str,
        reference_id: Optional[int]
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Procesa recompensa tipo SHOP_ITEM."""
        item_id = config.get("item_id")
        item_slug = config.get("item_slug")
        quantity = config.get("quantity", 1)

        if item_id:
            return await self.grant_shop_item(
                user_id=user_id,
                item_id=item_id,
                quantity=quantity,
                source=source,
                reference_id=reference_id
            )
        elif item_slug:
            return await self.grant_shop_item_by_slug(
                user_id=user_id,
                item_slug=item_slug,
                quantity=quantity,
                source=source,
                reference_id=reference_id
            )
        else:
            return False, "Falta item_id o item_slug en config", None

    async def _grant_besitos_reward(
        self,
        user_id: int,
        config: Dict[str, Any],
        source: str,
        reference_id: Optional[int]
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Procesa recompensa tipo BESITOS."""
        from bot.gamification.services.besito import BesitoService

        amount = config.get("amount", 0)
        if amount <= 0:
            return False, "Cantidad de besitos debe ser positiva", None

        transaction_type = self._source_to_transaction_type(source)

        besito_service = BesitoService(self.session)
        success, msg, transaction = await besito_service.grant_besitos(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type,
            description=f"Recompensa ({source})",
            reference_id=reference_id
        )

        if not success:
            return False, msg, None

        reward_data = {
            "type": "besitos",
            "amount": amount,
            "source": source,
            "reference_id": reference_id,
            "transaction_id": transaction.id if transaction else None
        }

        return True, f"¡Recibiste {amount} besitos!", reward_data

    async def _grant_badge_reward(
        self,
        user_id: int,
        config: Dict[str, Any],
        source: str,
        reference_id: Optional[int]
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Procesa recompensa tipo BADGE."""
        reward_id = config.get("reward_id")
        if not reward_id:
            return False, "Falta reward_id para badge", None

        obtained_via = self._source_to_obtained_via(source)
        return await self._grant_existing_reward(
            user_id, reward_id, obtained_via, reference_id
        )

    async def _grant_existing_reward(
        self,
        user_id: int,
        reward_id: int,
        obtained_via: ObtainedVia,
        reference_id: Optional[int]
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Otorga una recompensa existente del catálogo."""
        success, msg, user_reward = await self.reward_service.grant_reward(
            user_id=user_id,
            reward_id=reward_id,
            obtained_via=obtained_via,
            reference_id=reference_id
        )

        if not success:
            return False, msg, None

        reward_data = {
            "type": "reward",
            "reward_id": reward_id,
            "user_reward_id": user_reward.id if user_reward else None,
            "obtained_via": obtained_via.value
        }

        return True, msg, reward_data

    # ========================================
    # HELPERS
    # ========================================

    def _source_to_obtained_via(self, source: str) -> ObtainedVia:
        """Convierte source string a ObtainedVia enum."""
        mapping = {
            "mission_reward": ObtainedVia.MISSION,
            "mission": ObtainedVia.MISSION,
            "admin": ObtainedVia.ADMIN_GRANT,
            "admin_grant": ObtainedVia.ADMIN_GRANT,
            "event": ObtainedVia.EVENT,
            "level_up": ObtainedVia.LEVEL_UP,
            "purchase": ObtainedVia.PURCHASE,
            "auto_unlock": ObtainedVia.AUTO_UNLOCK,
        }
        return mapping.get(source, ObtainedVia.MISSION)

    def _source_to_transaction_type(self, source: str) -> TransactionType:
        """Convierte source string a TransactionType enum."""
        mapping = {
            "mission_reward": TransactionType.MISSION_REWARD,
            "mission": TransactionType.MISSION_REWARD,
            "admin": TransactionType.ADMIN_GRANT,
            "admin_grant": TransactionType.ADMIN_GRANT,
            "streak_bonus": TransactionType.STREAK_BONUS,
            "level_up": TransactionType.LEVEL_UP_BONUS,
            "daily_gift": TransactionType.DAILY_GIFT,
        }
        return mapping.get(source, TransactionType.MISSION_REWARD)

    # ========================================
    # VALIDATION HELPERS
    # ========================================

    async def validate_shop_item_reward_config(
        self,
        config: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Valida configuración de recompensa tipo SHOP_ITEM.

        Args:
            config: Configuración a validar

        Returns:
            (is_valid, error_message)
        """
        item_id = config.get("item_id")
        item_slug = config.get("item_slug")

        if not item_id and not item_slug:
            return False, "Debe especificar item_id o item_slug"

        # Verificar que el item existe
        if item_id:
            item = await self.shop_service.get_item(item_id)
        else:
            item = await self.shop_service.get_item_by_slug(item_slug)

        if not item:
            return False, f"Item no encontrado: {item_id or item_slug}"

        if not item.is_active:
            return False, f"Item '{item.name}' no está activo"

        quantity = config.get("quantity", 1)
        if quantity < 1:
            return False, "Cantidad debe ser al menos 1"

        return True, "OK"

    async def get_shop_item_for_display(
        self,
        item_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos de item de tienda formateados para mostrar.

        Args:
            item_id: ID del item

        Returns:
            Dict con datos del item o None
        """
        item = await self.shop_service.get_item(item_id)
        if not item:
            return None

        return {
            "id": item.id,
            "slug": item.slug,
            "name": item.name,
            "description": item.description,
            "icon": item.icon,
            "price_besitos": item.price_besitos,
            "rarity": item.rarity,
            "is_active": item.is_active,
            "requires_vip": item.requires_vip
        }
