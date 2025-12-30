"""
Servicio del Gabinete de Lucien (Fase 4).

Responsabilidades:
- Navegacion por categorias del Gabinete
- Verificacion de acceso por nivel
- Procesamiento de compras con descuentos
- Gestion de inventario del Gabinete
- Uso de items consumibles
"""

from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, UTC
from dataclasses import dataclass
import json
import logging

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from bot.shop.database.models import (
    ItemCategory,
    ShopItem,
    UserInventory,
    UserInventoryItem,
    ItemPurchase,
    UserDiscount,
)
from bot.shop.database.enums import (
    GabineteCategory,
    ItemVisibility,
    GabineteItemType,
    DiscountSource,
    PurchaseStatus,
)

logger = logging.getLogger(__name__)


@dataclass
class PurchaseResult:
    """Resultado de una compra en el Gabinete."""
    success: bool
    message: str
    item: Optional[ShopItem] = None
    inventory_item: Optional[UserInventoryItem] = None
    price_paid: int = 0
    discount_applied: float = 0.0


@dataclass
class ItemAccessResult:
    """Resultado de verificacion de acceso a un item."""
    can_view: bool
    can_buy: bool
    reason: Optional[str] = None
    required_level: Optional[int] = None


class GabineteService:
    """Servicio del Gabinete de Lucien."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ========================================
    # CATEGORIAS
    # ========================================

    async def get_gabinete_categories(
        self,
        user_level: int = 1
    ) -> List[ItemCategory]:
        """
        Obtiene las categorias del Gabinete visibles para el usuario.

        Args:
            user_level: Nivel actual del usuario (1-7)

        Returns:
            Lista de categorias que el usuario puede ver
        """
        result = await self.session.execute(
            select(ItemCategory)
            .where(
                and_(
                    ItemCategory.is_gabinete == True,
                    ItemCategory.is_active == True,
                    ItemCategory.min_level_to_view <= user_level
                )
            )
            .order_by(ItemCategory.order)
        )
        return list(result.scalars().all())

    async def get_category_by_slug(
        self,
        slug: str
    ) -> Optional[ItemCategory]:
        """Obtiene una categoria por su slug."""
        result = await self.session.execute(
            select(ItemCategory).where(ItemCategory.slug == slug)
        )
        return result.scalar_one_or_none()

    async def can_user_access_category(
        self,
        category: ItemCategory,
        user_level: int
    ) -> Tuple[bool, bool, str]:
        """
        Verifica si el usuario puede ver/comprar en una categoria.

        Returns:
            (can_view, can_buy, reason)
        """
        can_view = user_level >= category.min_level_to_view
        can_buy = user_level >= category.min_level_to_buy

        if not can_view:
            return False, False, f"Requiere nivel {category.min_level_to_view} para ver"
        if not can_buy:
            return True, False, f"Requiere nivel {category.min_level_to_buy} para comprar"

        return True, True, ""

    # ========================================
    # ITEMS
    # ========================================

    async def get_items_by_category(
        self,
        category_slug: str,
        user_level: int = 1,
        include_hidden: bool = False
    ) -> List[ShopItem]:
        """
        Obtiene items de una categoria filtrados por nivel de usuario.

        Args:
            category_slug: Slug de la categoria
            user_level: Nivel del usuario
            include_hidden: Si incluir items ocultos (para confidentes+)

        Returns:
            Lista de items visibles para el usuario
        """
        # Construir condiciones de visibilidad
        visibility_conditions = [
            ShopItem.visibility == ItemVisibility.PUBLIC.value
        ]

        if user_level >= 6:  # Confidentes
            visibility_conditions.append(
                ShopItem.visibility == ItemVisibility.CONFIDANTS_ONLY.value
            )
        if user_level >= 7:  # Guardianes
            visibility_conditions.append(
                ShopItem.visibility == ItemVisibility.GUARDIANS_ONLY.value
            )

        result = await self.session.execute(
            select(ShopItem)
            .join(ItemCategory)
            .where(
                and_(
                    ItemCategory.slug == category_slug,
                    ShopItem.is_active == True,
                    ShopItem.min_level_to_view <= user_level,
                    or_(*visibility_conditions)
                )
            )
            .order_by(ShopItem.order)
        )
        return list(result.scalars().all())

    async def get_item_by_slug(
        self,
        slug: str
    ) -> Optional[ShopItem]:
        """Obtiene un item por su slug."""
        result = await self.session.execute(
            select(ShopItem)
            .options(selectinload(ShopItem.category))
            .where(ShopItem.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_item_by_id(
        self,
        item_id: int
    ) -> Optional[ShopItem]:
        """Obtiene un item por su ID."""
        result = await self.session.execute(
            select(ShopItem)
            .options(selectinload(ShopItem.category))
            .where(ShopItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def check_item_access(
        self,
        item: ShopItem,
        user_level: int
    ) -> ItemAccessResult:
        """
        Verifica el acceso de un usuario a un item.

        Returns:
            ItemAccessResult con can_view, can_buy y reason
        """
        # Verificar visibilidad
        visibility = ItemVisibility(item.visibility)

        if visibility == ItemVisibility.CONFIDANTS_ONLY and user_level < 6:
            return ItemAccessResult(
                can_view=False,
                can_buy=False,
                reason="Solo visible para Confidentes (nivel 6+)",
                required_level=6
            )

        if visibility == ItemVisibility.GUARDIANS_ONLY and user_level < 7:
            return ItemAccessResult(
                can_view=False,
                can_buy=False,
                reason="Solo visible para Guardianes (nivel 7)",
                required_level=7
            )

        # Verificar nivel para ver
        if user_level < item.min_level_to_view:
            return ItemAccessResult(
                can_view=False,
                can_buy=False,
                reason=f"Requiere nivel {item.min_level_to_view} para ver",
                required_level=item.min_level_to_view
            )

        # Verificar nivel para comprar
        if user_level < item.min_level_to_buy:
            return ItemAccessResult(
                can_view=True,
                can_buy=False,
                reason=f"Requiere nivel {item.min_level_to_buy} para comprar",
                required_level=item.min_level_to_buy
            )

        return ItemAccessResult(can_view=True, can_buy=True)

    async def is_item_available(
        self,
        item: ShopItem
    ) -> Tuple[bool, str]:
        """
        Verifica si un item esta disponible para compra.

        Returns:
            (is_available, reason)
        """
        if not item.is_active:
            return False, "Este item no esta disponible"

        # Verificar stock
        if item.stock is not None and item.stock <= 0:
            return False, "Item agotado"

        # Verificar disponibilidad temporal
        now = datetime.now(UTC)
        if item.available_from and now < item.available_from:
            return False, f"Disponible a partir de {item.available_from.strftime('%d/%m/%Y')}"

        if item.available_until and now > item.available_until:
            return False, "Este item ya no esta disponible"

        return True, ""

    async def check_user_item_limit(
        self,
        user_id: int,
        item: ShopItem
    ) -> Tuple[bool, int]:
        """
        Verifica si el usuario puede comprar mas unidades del item.

        Returns:
            (can_buy, current_count)
        """
        if item.max_per_user is None:
            return True, 0

        # Contar items en inventario
        result = await self.session.execute(
            select(func.sum(UserInventoryItem.quantity))
            .join(UserInventory)
            .where(
                and_(
                    UserInventory.user_id == user_id,
                    UserInventoryItem.item_id == item.id
                )
            )
        )
        current_count = result.scalar() or 0

        can_buy = current_count < item.max_per_user
        return can_buy, current_count

    # ========================================
    # COMPRAS
    # ========================================

    async def purchase_item(
        self,
        user_id: int,
        item_id: int,
        user_level: int,
        user_balance: float,
        discount_percent: float = 0.0
    ) -> PurchaseResult:
        """
        Procesa la compra de un item del Gabinete.

        Args:
            user_id: ID del usuario
            item_id: ID del item a comprar
            user_level: Nivel actual del usuario
            user_balance: Balance de Favores/Besitos del usuario
            discount_percent: Porcentaje de descuento a aplicar

        Returns:
            PurchaseResult con el resultado de la compra
        """
        # 1. Obtener item
        item = await self.get_item_by_id(item_id)
        if not item:
            return PurchaseResult(
                success=False,
                message="Item no encontrado"
            )

        # 2. Verificar acceso
        access = await self.check_item_access(item, user_level)
        if not access.can_buy:
            return PurchaseResult(
                success=False,
                message=access.reason or "No tiene acceso a este item",
                item=item
            )

        # 3. Verificar disponibilidad
        available, reason = await self.is_item_available(item)
        if not available:
            return PurchaseResult(
                success=False,
                message=reason,
                item=item
            )

        # 4. Verificar limite por usuario
        can_buy, current_count = await self.check_user_item_limit(user_id, item)
        if not can_buy:
            return PurchaseResult(
                success=False,
                message=f"Ya tiene el maximo permitido de este item ({item.max_per_user})",
                item=item
            )

        # 5. Calcular precio con descuento
        discount = min(discount_percent, 50.0)  # Max 50%
        price_final = item.price_besitos * (1 - discount / 100)
        price_final = round(price_final, 1)

        # 6. Verificar balance
        if user_balance < price_final:
            return PurchaseResult(
                success=False,
                message=f"Favores insuficientes. Necesita {price_final}, tiene {user_balance}",
                item=item
            )

        # 7. Obtener o crear inventario
        inventory = await self._get_or_create_inventory(user_id)

        # 8. Agregar item al inventario
        inventory_item = UserInventoryItem(
            user_id=inventory.user_id,
            item_id=item.id,
            quantity=1,
            obtained_via="purchase"
        )
        self.session.add(inventory_item)

        # 9. Actualizar stats del inventario
        inventory.total_items += 1
        inventory.total_spent += int(price_final)

        # 10. Reducir stock si es limitado
        if item.stock is not None:
            item.stock -= 1

        # 11. Registrar compra
        purchase = ItemPurchase(
            user_id=user_id,
            item_id=item.id,
            quantity=1,
            price_paid=int(price_final),
            status=PurchaseStatus.COMPLETED.value
        )
        self.session.add(purchase)

        await self.session.commit()
        await self.session.refresh(inventory_item)

        logger.info(
            f"Purchase completed: user={user_id}, item={item.slug}, "
            f"price={price_final}, discount={discount}%"
        )

        return PurchaseResult(
            success=True,
            message=item.purchase_message or "Compra completada",
            item=item,
            inventory_item=inventory_item,
            price_paid=int(price_final),
            discount_applied=discount
        )

    async def _get_or_create_inventory(
        self,
        user_id: int
    ) -> UserInventory:
        """Obtiene o crea el inventario de un usuario."""
        result = await self.session.execute(
            select(UserInventory).where(UserInventory.user_id == user_id)
        )
        inventory = result.scalar_one_or_none()

        if not inventory:
            inventory = UserInventory(user_id=user_id)
            self.session.add(inventory)
            await self.session.flush()

        return inventory

    # ========================================
    # INVENTARIO
    # ========================================

    async def get_user_inventory(
        self,
        user_id: int
    ) -> List[UserInventoryItem]:
        """
        Obtiene todos los items en el inventario del usuario.

        Returns:
            Lista de UserInventoryItem con sus ShopItem asociados
        """
        result = await self.session.execute(
            select(UserInventoryItem)
            .options(selectinload(UserInventoryItem.item))
            .join(UserInventory)
            .where(UserInventory.user_id == user_id)
            .order_by(UserInventoryItem.obtained_at.desc())
        )
        return list(result.scalars().all())

    async def get_user_inventory_by_category(
        self,
        user_id: int,
        category_slug: str
    ) -> List[UserInventoryItem]:
        """
        Obtiene items del inventario filtrados por categoria.
        """
        result = await self.session.execute(
            select(UserInventoryItem)
            .options(selectinload(UserInventoryItem.item))
            .join(UserInventory)
            .join(ShopItem)
            .join(ItemCategory)
            .where(
                and_(
                    UserInventory.user_id == user_id,
                    ItemCategory.slug == category_slug
                )
            )
            .order_by(UserInventoryItem.obtained_at.desc())
        )
        return list(result.scalars().all())

    async def get_inventory_item(
        self,
        user_id: int,
        item_id: int
    ) -> Optional[UserInventoryItem]:
        """
        Obtiene un item especifico del inventario del usuario.
        """
        result = await self.session.execute(
            select(UserInventoryItem)
            .options(selectinload(UserInventoryItem.item))
            .join(UserInventory)
            .where(
                and_(
                    UserInventory.user_id == user_id,
                    UserInventoryItem.item_id == item_id,
                    UserInventoryItem.is_used == False
                )
            )
        )
        return result.scalar_one_or_none()

    async def use_item(
        self,
        user_id: int,
        inventory_item_id: int
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Usa un item consumible del inventario.

        Returns:
            (success, message, content_data)
        """
        # Obtener item del inventario
        result = await self.session.execute(
            select(UserInventoryItem)
            .options(selectinload(UserInventoryItem.item))
            .where(
                and_(
                    UserInventoryItem.id == inventory_item_id,
                    UserInventoryItem.is_used == False
                )
            )
            .join(UserInventory)
            .where(UserInventory.user_id == user_id)
        )
        inv_item = result.scalar_one_or_none()

        if not inv_item:
            return False, "Item no encontrado o ya fue usado", None

        item = inv_item.item

        # Verificar si es consumible
        if item.gabinete_item_type not in [
            GabineteItemType.AUDIO.value,
            GabineteItemType.TEXT.value,
            GabineteItemType.PREVIEW.value,
            GabineteItemType.BADGE_TEMP.value,
            GabineteItemType.NARRATIVE_KEY.value,
            GabineteItemType.ARCHIVE.value,
        ]:
            return False, "Este item no se puede 'usar' de esta forma", None

        # Marcar como usado
        inv_item.is_used = True
        inv_item.used_at = datetime.now(UTC)

        # Decrementar cantidad si tiene mas de 1
        if inv_item.quantity > 1:
            inv_item.quantity -= 1
            inv_item.is_used = False  # Aun tiene mas
            inv_item.used_at = None

        await self.session.commit()

        # Obtener contenido del item
        content_data = None
        if item.item_metadata:
            try:
                content_data = json.loads(item.item_metadata)
            except json.JSONDecodeError:
                pass

        message = item.post_use_message or "Item utilizado"

        logger.info(f"Item used: user={user_id}, item={item.slug}")

        return True, message, content_data

    async def has_item(
        self,
        user_id: int,
        item_slug: str
    ) -> bool:
        """
        Verifica si el usuario tiene un item especifico.
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(UserInventoryItem)
            .join(UserInventory)
            .join(ShopItem)
            .where(
                and_(
                    UserInventory.user_id == user_id,
                    ShopItem.slug == item_slug
                )
            )
        )
        count = result.scalar()
        return count > 0

    # ========================================
    # ESTADISTICAS
    # ========================================

    async def get_gabinete_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadisticas generales del Gabinete.
        """
        # Total items vendidos
        total_sales = await self.session.execute(
            select(func.count())
            .select_from(ItemPurchase)
            .join(ShopItem)
            .join(ItemCategory)
            .where(ItemCategory.is_gabinete == True)
        )

        # Total favores gastados
        total_spent = await self.session.execute(
            select(func.sum(ItemPurchase.price_paid))
            .join(ShopItem)
            .join(ItemCategory)
            .where(ItemCategory.is_gabinete == True)
        )

        # Items mas vendidos
        top_items = await self.session.execute(
            select(
                ShopItem.name,
                ShopItem.slug,
                func.count(ItemPurchase.id).label('sales')
            )
            .join(ItemPurchase)
            .join(ItemCategory)
            .where(ItemCategory.is_gabinete == True)
            .group_by(ShopItem.id)
            .order_by(func.count(ItemPurchase.id).desc())
            .limit(5)
        )

        return {
            "total_sales": total_sales.scalar() or 0,
            "total_spent": total_spent.scalar() or 0,
            "top_items": [
                {"name": row[0], "slug": row[1], "sales": row[2]}
                for row in top_items.all()
            ]
        }

    async def get_user_gabinete_stats(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Obtiene estadisticas del usuario en el Gabinete.
        """
        # Total compras
        total_purchases = await self.session.execute(
            select(func.count())
            .select_from(ItemPurchase)
            .join(ShopItem)
            .join(ItemCategory)
            .where(
                and_(
                    ItemPurchase.user_id == user_id,
                    ItemCategory.is_gabinete == True
                )
            )
        )

        # Total gastado
        total_spent = await self.session.execute(
            select(func.sum(ItemPurchase.price_paid))
            .join(ShopItem)
            .join(ItemCategory)
            .where(
                and_(
                    ItemPurchase.user_id == user_id,
                    ItemCategory.is_gabinete == True
                )
            )
        )

        # Items en inventario
        inventory_count = await self.session.execute(
            select(func.count())
            .select_from(UserInventoryItem)
            .join(UserInventory)
            .join(ShopItem)
            .join(ItemCategory)
            .where(
                and_(
                    UserInventory.user_id == user_id,
                    ItemCategory.is_gabinete == True
                )
            )
        )

        return {
            "total_purchases": total_purchases.scalar() or 0,
            "total_spent": total_spent.scalar() or 0,
            "inventory_count": inventory_count.scalar() or 0
        }
