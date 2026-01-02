"""
Handlers for Mapa del Deseo and Discount flows.

Implements F6.4 (Mapa del Deseo) and F6.5 (Discounts) handlers.
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from bot.gamification.services.mapa_del_deseo_service import MapaDelDeseoService
from bot.gamification.services.merit_urgency_discount_service import MeritUrgencyDiscountService

logger = logging.getLogger(__name__)
router = Router()


# ========================
# F6.4: MAPA DEL DESEO
# ========================

@router.callback_query(F.data == "mapa:start")
async def start_mapa_del_deseo_flow(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Start the Mapa del Deseo flow.
    """
    service = MapaDelDeseoService(session, bot)
    await service.show_mapa_del_deseo_introduction(call.from_user.id)
    await call.answer()


@router.callback_query(F.data.startswith("mapa_tier:"))
async def show_mapa_tier_details(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Show details of a specific Mapa del Deseo tier.
    """
    tier = int(call.data.split(":")[1])
    service = MapaDelDeseoService(session, bot)
    await service.show_tier_details(call.from_user.id, tier)
    await call.answer()


@router.callback_query(F.data == "mapa_compare")
async def show_mapa_comparison(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Show comparison of all Mapa del Deseo tiers.
    """
    service = MapaDelDeseoService(session, bot)
    await service.show_mapa_comparison(call.from_user.id)
    await call.answer()


@router.callback_query(F.data == "mapa_defer")
async def defer_mapa_decision(call: CallbackQuery):
    """
    Handle deferral of Mapa del Deseo decision.
    """
    message = "Entendido. Puede retornar al Mapa del Deseo en cualquier momento cuando esté listo."
    await call.message.edit_text(message)
    await call.answer()


@router.callback_query(F.data.startswith("purchase_mapa_tier:"))
async def purchase_mapa_tier(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Handle purchase of a Mapa del Deseo tier.
    """
    tier = int(call.data.split(":")[1])
    service = MapaDelDeseoService(session, bot)
    
    success = await service.purchase_mapa_tier(call.from_user.id, tier)
    
    if success:
        await call.answer("¡Compra exitosa! Se han aplicado sus beneficios.", show_alert=True)
    else:
        await call.answer("No se pudo completar la compra. Verifique que es VIP y tiene suficientes Favores.", show_alert=True)


# ========================
# F6.5: DISCOUNT SYSTEM
# ========================

@router.callback_query(F.data.startswith("show_urgency_discount:"))
async def show_urgency_discount(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Show urgency discount offer.
    """
    # Format: show_urgency_discount:product_type:regular_price:special_price:hours
    parts = call.data.split(":")
    if len(parts) >= 5:
        product_type = parts[1]
        regular_price = float(parts[2])
        special_price = float(parts[3])
        hours = int(parts[4])
        
        service = MeritUrgencyDiscountService(session, bot)
        await service.show_urgency_discount_offer(
            call.from_user.id,
            product_type,
            regular_price,
            special_price,
            hours
        )
    await call.answer()


@router.callback_query(F.data.startswith("purchase_urgent:"))
async def purchase_urgent_discount(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Handle purchase with urgent discount.
    """
    product_type = call.data.split(":")[1]
    # This would handle the actual purchase with discount
    await call.answer(f"Procesando compra urgente de {product_type}...")
    # Implementation would depend on specific product type


@router.callback_query(F.data == "decline_urgent_offer")
async def decline_urgent_offer(call: CallbackQuery):
    """
    Handle declining an urgent discount offer.
    """
    await call.message.edit_text("Entendido. Esta oferta especial está disponible por tiempo limitado.")
    await call.answer()


# ========================
# INTEGRATION WITH EXISTING FLOWS
# ========================

@router.callback_query(F.data == "show_discount_breakdown")
async def show_discount_breakdown(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Show user's current discount breakdown.
    """
    from bot.shop.services.discount import DiscountService
    
    user_id = call.from_user.id
    discount_service = DiscountService(session)
    
    # Get user level (simplified - in real app this would come from context)
    from bot.gamification.database.models import UserGamification
    from sqlalchemy import select
    
    result = await session.execute(select(UserGamification).where(UserGamification.user_id == user_id))
    user_gamification = result.scalar_one_or_none()
    user_level = user_gamification.current_level_id if user_gamification else 1
    
    breakdown = await discount_service.calculate_total_discount(user_id, user_level)
    
    # Include merit-based discounts
    merit_service = MeritUrgencyDiscountService(session, bot)
    total_info = await merit_service.get_total_discount_with_merit(user_id, user_level)
    
    message = f"""
📊 Su Desglose de Descuentos:

Descuento Básico: {breakdown.total_discount:.1f}%
Descuento por Mérito: {total_info['merit_discount']:.1f}%
Total Disponible: {total_info['total_discount']:.1f}%

Detalles:
{discount_service.get_discount_breakdown_text(breakdown)}
"""
    if total_info['merit_discount'] > 0:
        message += f"\nMérito y Lealtad: +{total_info['merit_discount']:.1f}%"

    await call.message.edit_text(message)
    await call.answer()


# ========================
# INITIALIZATION
# ========================

async def initialize_mapa_del_deseo(session: AsyncSession, bot: Bot):
    """
    Initialize Mapa del Deseo packages in the system.
    """
    service = MapaDelDeseoService(session, bot)
    await service.create_mapa_del_deseo_packages()
    
    logger.info("Mapa del Deseo packages initialized")