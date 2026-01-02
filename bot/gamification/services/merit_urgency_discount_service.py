"""
Merchandising and Urgency Discount Service for F6.5.

Implements discounts by merit and urgency as per F6.5 requirements.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, UTC
from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from bot.shop.services.discount import DiscountService
from bot.shop.database.models import UserDiscount
from bot.shop.database.enums import DiscountSource
from bot.database.models import User
from bot.gamification.database.models import UserGamification, UserStreak

logger = logging.getLogger(__name__)


class MeritUrgencyDiscountService:
    """
    Service for managing merit-based and urgency-based discounts.
    
    Implements F6.5: Sistema de Descuentos por mérito y urgencia
    """
    
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot
        self.discount_service = DiscountService(session)

    async def calculate_merit_discounts(self, user_id: int) -> Dict[str, float]:
        """
        Calculate merit-based discounts for a user.

        Based on F6.5 documentation:
        | Condición | Descuento | Aplicable a |
        |-----------|-----------|-------------|
        | Nivel 5+ de Favores | 5% | VIP, Premium |
        | Nivel 6+ de Favores | 10% | VIP, Premium, Mapa |
        | Racha 30+ días | 5% adicional | Todo |
        | Primera compra | 10% | Solo VIP |
        | Referido activo | 15% | VIP |
        | Badge "Guardián de Secretos" | 15% | Todo |
        """
        discounts = {}

        # Get user data
        user = await self.session.get(User, user_id)
        if not user:
            return discounts

        user_gamification = await self.session.get(UserGamification, user_id)
        user_streak = await self.session.get(UserStreak, user_id)

        # Check for high besitos level (5+ = 5%, 6+ = 10%)
        if user_gamification:
            if user_gamification.current_level_id and user_gamification.current_level_id >= 5:
                discounts["besitos_level_5"] = 5.0
            if user_gamification.current_level_id and user_gamification.current_level_id >= 6:
                discounts["besitos_level_6"] = 10.0

        # Check for 30+ day streak
        if user_streak and user_streak.current_streak >= 30:
            discounts["long_streak"] = 5.0

        # Check for first-time VIP purchase (would require checking purchase history)
        # This would check if user hasn't previously purchased a VIP-related product
        await self._check_first_time_vip(user_id, discounts)

        # Check for active referral (would require checking referral system)
        await self._check_active_referral(user_id, discounts)

        # Check for "Guardián de Secretos" badge - checking in inventory
        await self._check_guardian_badge(user_id, discounts)

        return discounts

    async def _check_first_time_vip(self, user_id: int, discounts: Dict[str, float]):
        """
        Check if user is making their first VIP-related purchase.
        """
        # This would require checking if user has ever purchased a VIP-related product
        # For now, we'll implement a simplified check based on VIP status
        from bot.database.models import User
        user = await self.session.get(User, user_id)

        # If user has never been VIP, they might qualify for first-time discount
        # However, this is a complex check that would require purchase history
        # For now, we'll skip it as it needs more detailed implementation
        pass

    async def _check_active_referral(self, user_id: int, discounts: Dict[str, float]):
        """
        Check if user has an active referral that grants discount.
        """
        # This would require checking the referral system
        # For now, we'll implement a simplified check
        # This might involve checking if the user was referred by someone
        # and if that referral relationship is still active
        pass

    async def _check_guardian_badge(self, user_id: int, discounts: Dict[str, float]):
        """
        Check if user has "Guardián de Secretos" badge in their inventory.
        """
        from bot.shop.database.models import ShopItem, UserInventoryItem, UserInventory
        from sqlalchemy import and_

        # Check if user has the "Guardian del Secreto" badge
        # This assumes the badge has a specific slug
        stmt = (
            select(ShopItem)
            .join(UserInventoryItem, ShopItem.id == UserInventoryItem.item_id)
            .join(UserInventory, UserInventoryItem.user_id == UserInventory.user_id)
            .where(
                and_(
                    UserInventory.user_id == user_id,
                    # Look for items with "guardian" or "secreto" in the name/slug
                    (ShopItem.slug.ilike("%guardian%")) |
                    (ShopItem.slug.ilike("%secreto%")) |
                    (ShopItem.name.ilike("%Guardián%")) |
                    (ShopItem.name.ilike("%Secret%"))
                )
            )
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        # If we find a matching item, apply the discount
        for item in items:
            if "guardian" in item.slug.lower() or "guardian" in item.name.lower() or "secreto" in item.name.lower():
                discounts["guardian_badge"] = 15.0
                break

    async def create_urgency_discount(
        self,
        user_id: int,
        product_type: str,
        discount_percent: float,
        hours_duration: int = 24
    ) -> Optional[UserDiscount]:
        """
        Create an urgency-based discount for a specific product.
        
        From F6.5:
        "Una oportunidad limitada.
        Por las próximas {horas} horas, Diana ha autorizado
        un descuento especial en {producto}."
        """
        expires_at = datetime.now(UTC) + timedelta(hours=hours_duration)

        discount = UserDiscount(
            user_id=user_id,
            discount_source=DiscountSource.PROMO.value,
            discount_percent=discount_percent,
            expires_at=expires_at,
            is_active=True,
            admin_notes=f"Urgency discount for {product_type} - {hours_duration}h duration"
        )

        self.session.add(discount)
        await self.session.commit()
        await self.session.refresh(discount)

        logger.info(
            f"Created urgency discount: user={user_id}, "
            f"product={product_type}, discount={discount_percent}%, "
            f"expires={expires_at}"
        )

        return discount

    async def show_urgency_discount_offer(
        self,
        user_id: int,
        product_type: str,
        regular_price: float,
        special_price: float,
        hours_remaining: int = 24
    ):
        """
        Show an urgency discount offer to a user.
        
        From F6.5:
        "Speaker: LUCIEN

        'Una oportunidad limitada.

        Por las próximas {horas} horas, Diana ha autorizado
        un descuento especial en {producto}.

        Precio regular: {precio_regular}
        Precio especial: {precio_descuento}
        Ahorro: {ahorro}

        ⏰ Expira en: {countdown}

        Esta oferta no se repetirá pronto.'"
        """
        import math
        
        ahorro = regular_price - special_price
        
        message = f'''
Speaker: LUCIEN

"Una oportunidad limitada.

Por las próximas {hours_remaining} horas, Diana ha autorizado
un descuento especial en {product_type}.

Precio regular: {regular_price} Favores
Precio especial: {special_price} Favores  
Ahorro: {ahorro} Favores

⏰ Expira en: {hours_remaining}h

Esta oferta no se repetirá pronto."
        '''.strip()

        await self.bot.send_message(user_id, message)

        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(text="Adquirir ahora", callback_data=f"purchase_urgent:{product_type}"),
            InlineKeyboardButton(text="No, gracias", callback_data="decline_urgent_offer")
        )

        await self.bot.send_message(user_id, "¿Desea aprovechar esta oportunidad especial?", reply_markup=keyboard.as_markup())

    async def get_total_discount_with_merit(
        self,
        user_id: int,
        user_level: int
    ) -> Dict[str, Any]:
        """
        Get total discount including merit-based discounts.
        """
        # Get basic discount
        basic_breakdown = await self.discount_service.calculate_total_discount(user_id, user_level)
        
        # Get merit discounts
        merit_discounts = await self.calculate_merit_discounts(user_id)
        
        # Calculate additional merit discount total
        merit_total = sum(merit_discounts.values())
        
        # Add to total with cap
        total_with_merit = min(
            basic_breakdown.total_discount + merit_total,
            50.0  # Apply same cap as basic discount service
        )
        
        return {
            "basic_discount": basic_breakdown.total_discount,
            "merit_discount": merit_total,
            "total_discount": total_with_merit,
            "breakdown": {
                "level": basic_breakdown.level_discount,
                "badges": basic_breakdown.badge_discounts,
                "relics": basic_breakdown.relic_discounts,
                "promo": basic_breakdown.promo_discount,
                "merit": merit_discounts
            }
        }

    async def apply_dynamic_discounts(
        self,
        user_id: int,
        base_price: float,
        product_type: str
    ) -> Dict[str, Any]:
        """
        Apply dynamic discounts based on user's merit profile and urgency.
        """
        user = await self.session.get(User, user_id)
        user_gamification = await self.session.get(UserGamification, user_id)

        # Start with base price
        final_price = base_price
        applied_discounts = []

        user_level = user_gamification.current_level_id if user_gamification else 1

        # Get total discount percentage
        total_discount_info = await self.get_total_discount_with_merit(user_id, user_level)
        total_discount_pct = total_discount_info["total_discount"]

        if total_discount_pct > 0:
            discount_amount = base_price * (total_discount_pct / 100)
            final_price = base_price - discount_amount
            applied_discounts.append({
                "type": "merit_loyalty",
                "percentage": total_discount_pct,
                "amount": discount_amount,
                "description": f"Descuento acumulado por mérito y lealtad ({total_discount_pct}%)"
            })

        # Apply additional product-specific discount based on user tier
        # Higher Mapa del Deseo tiers could get additional percentage off certain products
        from bot.gamification.services.mapa_del_deseo_service import MapaDelDeseoService
        mapa_service = MapaDelDeseoService(self.session, self.bot)
        mapa_status = await mapa_service.get_user_mapa_status(user_id)

        if mapa_status["highest_tier"] >= 3:  # El Secreto tier
            # 5% additional for El Secreto tier holders
            additional_discount_pct = 5.0
            additional_discount_amount = final_price * (additional_discount_pct / 100)
            final_price = final_price - additional_discount_amount

            applied_discounts.append({
                "type": "mapa_del_deseo_tier",
                "percentage": additional_discount_pct,
                "amount": additional_discount_amount,
                "description": f"Beneficio por pertenecer al Nivel 3 del Mapa del Deseo ({additional_discount_pct}%)"
            })
        elif mapa_status["highest_tier"] == 2:  # Círculo Íntimo tier
            # 3% additional for Círculo Íntimo tier holders
            additional_discount_pct = 3.0
            additional_discount_amount = final_price * (additional_discount_pct / 100)
            final_price = final_price - additional_discount_amount

            applied_discounts.append({
                "type": "mapa_del_deseo_tier",
                "percentage": additional_discount_pct,
                "amount": additional_discount_amount,
                "description": f"Beneficio por pertenecer al Nivel 2 del Mapa del Deseo ({additional_discount_pct}%)"
            })

        # Calculate total discount percentage after all adjustments
        total_final_discount_pct = ((base_price - final_price) / base_price) * 100

        return {
            "original_price": base_price,
            "final_price": round(final_price, 2),
            "total_discount_pct": round(total_final_discount_pct, 2),
            "applied_discounts": applied_discounts,
            "savings": round(base_price - final_price, 2)
        }

    async def get_product_specific_discount(
        self,
        user_id: int,
        product_type: str  # vip, premium, mapa_del_deseo
    ) -> Dict[str, Any]:
        """
        Get product-specific discount based on user profile and product type.
        """
        user = await self.session.get(User, user_id)
        user_gamification = await self.session.get(UserGamification, user_id)

        user_level = user_gamification.current_level_id if user_gamification else 1

        # Get merit discounts
        merit_discounts = await self.calculate_merit_discounts(user_id)

        # Determine applicable discounts based on product type
        applicable_discounts = {}

        for condition, discount_pct in merit_discounts.items():
            if product_type == "vip":
                # All conditions apply to VIP
                applicable_discounts[condition] = discount_pct
            elif product_type == "premium":
                # All except first-time VIP purchase
                if condition != "first_time_vip":
                    applicable_discounts[condition] = discount_pct
            elif product_type == "mapa_del_deseo":
                # All conditions apply to Mapa del Deseo
                applicable_discounts[condition] = discount_pct

        total_discount_pct = min(sum(applicable_discounts.values()), 50.0)  # Cap at 50%

        return {
            "base_discounts": applicable_discounts,
            "total_discount_pct": total_discount_pct,
            "product_type": product_type
        }

    async def check_and_trigger_urgency_offers(self, user_id: int):
        """
        Check if user qualifies for any urgency offers.
        This can be called when appropriate to check for special promotions.
        """
        # This would check various conditions to trigger urgency offers
        # For example, if user has been inactive for a while, or if there's a special event
        # Implementation would depend on business logic and timing requirements
        pass