"""
Servicio de Descuentos del Gabinete (Fase 4).

Responsabilidades:
- Calcular descuentos por nivel
- Calcular descuentos por distintivos
- Calcular descuentos por reliquias
- Gestionar promociones temporales
- Aplicar descuento total con limite maximo
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
from dataclasses import dataclass
import logging

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.shop.database.models import (
    ShopItem,
    UserInventoryItem,
    UserInventory,
    UserDiscount,
)
from bot.shop.database.enums import DiscountSource

logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURACION DE DESCUENTOS
# ============================================================

# Descuentos por nivel (nivel -> porcentaje)
LEVEL_DISCOUNTS = {
    1: 0.0,
    2: 0.0,
    3: 0.0,
    4: 5.0,
    5: 10.0,
    6: 15.0,
    7: 20.0,
}

# Items que otorgan descuento (slug -> porcentaje)
BADGE_DISCOUNTS = {
    "dist_004_emblema_reconocido": 5.0,   # Emblema del Reconocido
    "dist_005_marca_confidente": 10.0,    # Marca del Confidente
    "dist_006_corona_guardian": 15.0,     # Corona del Guardian
}

RELIC_DISCOUNTS = {
    "rel_001_primer_secreto": 3.0,        # El Primer Secreto
    "rel_005_llave_maestra": 20.0,        # Llave Maestra
}

# Limite maximo de descuento
MAX_DISCOUNT = 50.0


@dataclass
class DiscountBreakdown:
    """Desglose del descuento total."""
    level_discount: float = 0.0
    badge_discounts: Dict[str, float] = None
    relic_discounts: Dict[str, float] = None
    promo_discount: float = 0.0
    total_discount: float = 0.0
    capped: bool = False  # True si se alcanzo el limite

    def __post_init__(self):
        if self.badge_discounts is None:
            self.badge_discounts = {}
        if self.relic_discounts is None:
            self.relic_discounts = {}


class DiscountService:
    """Servicio de calculo de descuentos del Gabinete."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def calculate_total_discount(
        self,
        user_id: int,
        user_level: int
    ) -> DiscountBreakdown:
        """
        Calcula el descuento total de un usuario.

        Args:
            user_id: ID del usuario
            user_level: Nivel actual del usuario (1-7)

        Returns:
            DiscountBreakdown con desglose completo
        """
        breakdown = DiscountBreakdown()

        # 1. Descuento por nivel
        breakdown.level_discount = self.get_level_discount(user_level)

        # 2. Descuentos por distintivos
        breakdown.badge_discounts = await self._get_badge_discounts(user_id)

        # 3. Descuentos por reliquias
        breakdown.relic_discounts = await self._get_relic_discounts(user_id)

        # 4. Descuentos por promociones
        breakdown.promo_discount = await self._get_promo_discount(user_id)

        # 5. Calcular total
        total = (
            breakdown.level_discount +
            sum(breakdown.badge_discounts.values()) +
            sum(breakdown.relic_discounts.values()) +
            breakdown.promo_discount
        )

        # 6. Aplicar limite
        if total > MAX_DISCOUNT:
            breakdown.total_discount = MAX_DISCOUNT
            breakdown.capped = True
        else:
            breakdown.total_discount = total
            breakdown.capped = False

        return breakdown

    def get_level_discount(self, user_level: int) -> float:
        """
        Obtiene el descuento por nivel.

        Args:
            user_level: Nivel del usuario (1-7)

        Returns:
            Porcentaje de descuento
        """
        return LEVEL_DISCOUNTS.get(user_level, 0.0)

    async def _get_badge_discounts(
        self,
        user_id: int
    ) -> Dict[str, float]:
        """
        Obtiene descuentos por distintivos que posee el usuario.

        Returns:
            Dict de slug -> porcentaje
        """
        discounts = {}

        # Buscar items que otorgan descuento en el inventario
        for slug, discount_pct in BADGE_DISCOUNTS.items():
            has_badge = await self._user_has_item(user_id, slug)
            if has_badge:
                discounts[slug] = discount_pct

        return discounts

    async def _get_relic_discounts(
        self,
        user_id: int
    ) -> Dict[str, float]:
        """
        Obtiene descuentos por reliquias que posee el usuario.

        Returns:
            Dict de slug -> porcentaje
        """
        discounts = {}

        for slug, discount_pct in RELIC_DISCOUNTS.items():
            has_relic = await self._user_has_item(user_id, slug)
            if has_relic:
                discounts[slug] = discount_pct

        return discounts

    async def _get_promo_discount(
        self,
        user_id: int
    ) -> float:
        """
        Obtiene descuento por promocion activa.

        Returns:
            Porcentaje de descuento por promo
        """
        now = datetime.now(UTC)

        result = await self.session.execute(
            select(UserDiscount)
            .where(
                and_(
                    UserDiscount.user_id == user_id,
                    UserDiscount.discount_source == DiscountSource.PROMO.value,
                    UserDiscount.is_active == True,
                    (UserDiscount.expires_at == None) | (UserDiscount.expires_at > now)
                )
            )
            .order_by(UserDiscount.discount_percent.desc())
            .limit(1)
        )
        promo = result.scalar_one_or_none()

        if promo:
            return promo.discount_percent

        return 0.0

    async def _user_has_item(
        self,
        user_id: int,
        item_slug: str
    ) -> bool:
        """Verifica si el usuario tiene un item especifico."""
        result = await self.session.execute(
            select(UserInventoryItem.id)
            .join(UserInventory)
            .join(ShopItem)
            .where(
                and_(
                    UserInventory.user_id == user_id,
                    ShopItem.slug == item_slug
                )
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    def apply_discount(
        self,
        price: int,
        discount_percent: float
    ) -> float:
        """
        Aplica descuento a un precio.

        Args:
            price: Precio original
            discount_percent: Porcentaje de descuento (0-50)

        Returns:
            Precio final redondeado a 1 decimal
        """
        discount = min(discount_percent, MAX_DISCOUNT)
        final_price = price * (1 - discount / 100)
        return round(final_price, 1)

    def get_discount_breakdown_text(
        self,
        breakdown: DiscountBreakdown
    ) -> str:
        """
        Genera texto descriptivo del desglose de descuento.

        Returns:
            Texto formateado para mostrar en UI
        """
        lines = []

        if breakdown.level_discount > 0:
            lines.append(f"Nivel: {breakdown.level_discount}%")

        for slug, pct in breakdown.badge_discounts.items():
            name = self._get_item_display_name(slug)
            lines.append(f"{name}: +{pct}%")

        for slug, pct in breakdown.relic_discounts.items():
            name = self._get_item_display_name(slug)
            lines.append(f"{name}: +{pct}%")

        if breakdown.promo_discount > 0:
            lines.append(f"Promocion: +{breakdown.promo_discount}%")

        if breakdown.capped:
            lines.append(f"(Limitado a {MAX_DISCOUNT}%)")

        if not lines:
            return "Sin descuento"

        return "\n".join(lines)

    def _get_item_display_name(self, slug: str) -> str:
        """Obtiene nombre legible de un item por su slug."""
        names = {
            "dist_004_emblema_reconocido": "Emblema del Reconocido",
            "dist_005_marca_confidente": "Marca del Confidente",
            "dist_006_corona_guardian": "Corona del Guardian",
            "rel_001_primer_secreto": "El Primer Secreto",
            "rel_005_llave_maestra": "Llave Maestra",
        }
        return names.get(slug, slug)

    # ========================================
    # GESTION DE PROMOCIONES
    # ========================================

    async def create_promo_discount(
        self,
        user_id: int,
        discount_percent: float,
        hours: int = 24,
        source_item_id: Optional[int] = None
    ) -> UserDiscount:
        """
        Crea un descuento promocional para un usuario.

        Args:
            user_id: ID del usuario
            discount_percent: Porcentaje de descuento
            hours: Duracion en horas
            source_item_id: ID del item que origino el descuento (opcional)

        Returns:
            UserDiscount creado
        """
        from datetime import timedelta

        expires_at = datetime.now(UTC) + timedelta(hours=hours)

        discount = UserDiscount(
            user_id=user_id,
            discount_source=DiscountSource.PROMO.value,
            source_item_id=source_item_id,
            discount_percent=discount_percent,
            expires_at=expires_at,
            is_active=True
        )
        self.session.add(discount)
        await self.session.commit()
        await self.session.refresh(discount)

        logger.info(
            f"Created promo discount: user={user_id}, pct={discount_percent}, "
            f"expires={expires_at}"
        )

        return discount

    async def deactivate_expired_promos(self) -> int:
        """
        Desactiva promociones expiradas.

        Returns:
            Cantidad de promociones desactivadas
        """
        from sqlalchemy import update

        now = datetime.now(UTC)

        result = await self.session.execute(
            update(UserDiscount)
            .where(
                and_(
                    UserDiscount.is_active == True,
                    UserDiscount.expires_at != None,
                    UserDiscount.expires_at <= now
                )
            )
            .values(is_active=False)
        )
        await self.session.commit()

        count = result.rowcount
        if count > 0:
            logger.info(f"Deactivated {count} expired promo discounts")

        return count

    async def get_user_active_promos(
        self,
        user_id: int
    ) -> List[UserDiscount]:
        """
        Obtiene promociones activas de un usuario.

        Returns:
            Lista de UserDiscount activos
        """
        now = datetime.now(UTC)

        result = await self.session.execute(
            select(UserDiscount)
            .where(
                and_(
                    UserDiscount.user_id == user_id,
                    UserDiscount.is_active == True,
                    (UserDiscount.expires_at == None) | (UserDiscount.expires_at > now)
                )
            )
            .order_by(UserDiscount.created_at.desc())
        )
        return list(result.scalars().all())
