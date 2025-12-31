"""
Handlers for contextual offers.

Implements triggers for contextual offers based on user behavior.
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import User
from bot.gamification.services.contextual_offer_service import ContextualOfferService
from bot.gamification.services.archetype_conversion import ArchetypeConversionService

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text)  # This will catch all text messages to check for activity
async def check_contextual_offers(
    message: Message,
    session: AsyncSession,
    bot: Bot
):
    """
    Check if we should show a contextual offer based on user activity.
    
    Triggers for F6.2: High activity Free users
    """
    user_id = message.from_user.id
    user = await session.get(User, user_id)
    
    if not user or user.is_vip:
        # Only for free users
        return

    # Check if user meets criteria for contextual offer (high activity, etc.)
    offer_service = ContextualOfferService(session, bot)
    
    # Only show offer if user hasn't seen it recently (to prevent spam)
    if not await offer_service.has_seen_offer_recently(user_id):
        should_show = await offer_service.should_show_contextual_vip_offer(user_id)
        
        if should_show:
            # Use ArchetypeConversionService to determine if this is the right time
            archetype_service = ArchetypeConversionService()
            
            # For this trigger, we'll use a general "high_activity" event
            should_trigger = archetype_service.should_show_offer(
                user.archetype if user.archetype else None,
                "high_activity",
                {"message_text": message.text}
            )
            
            if should_trigger:
                await offer_service.show_contextual_vip_offer(user_id)
                await offer_service.track_offer_shown(user_id, "contextual_vip_offer", {
                    "trigger": "high_activity",
                    "message_text": message.text
                })


@router.callback_query(F.data == "dismiss_content_offer")
async def dismiss_content_offer(call: CallbackQuery):
    """Handle when user dismisses a content offer."""
    await call.answer("Gracias. Puede continuar explorando el contenido gratuito.")
    await call.message.delete()


@router.callback_query(F.data.startswith("show_premium_content:"))
async def show_premium_content_details(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Handle showing premium content details (part of F6.3 flow).
    """
    content_id = call.data.split(":")[1]
    
    # In a real implementation, you would fetch the premium content details
    # For now, we'll just send a placeholder message
    message = f"""
Speaker: LUCIEN

"Este es el contenido Premium '#{content_id}' que seleccionó.

Características:
- Duración: 15 minutos
- Categoría: Premium
- Calidad: Alta definición

¿Desea adquirir este contenido individual?"
    """.strip()
    
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Adquirir ahora", callback_data=f"purchase_premium:{content_id}"),
        InlineKeyboardButton(text="Ver catálogo", callback_data="show_premium_catalog"),
        InlineKeyboardButton(text="Cancelar", callback_data="cancel_premium_view")
    )
    
    await call.message.edit_text(message, reply_markup=keyboard.as_markup())
    await call.answer()


@router.callback_query(F.data.startswith("show_vip_for_content:"))
async def show_vip_requirement_for_content(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Handle showing VIP requirement when user tries to access blocked content.
    """
    content_name = call.data.split(":", 1)[1] if ":" in call.data else "contenido exclusivo"
    
    user_id = call.from_user.id
    offer_service = ContextualOfferService(session, bot)
    
    await offer_service.show_blocked_content_offer(user_id, content_name)
    await call.answer()


# Additional handler to be called from other parts of the system when content is blocked
async def trigger_blocked_content_offer(user_id: int, content_name: str, session: AsyncSession, bot: Bot):
    """
    Public function to trigger blocked content offer from other handlers/services.
    """
    offer_service = ContextualOfferService(session, bot)
    await offer_service.show_blocked_content_offer(user_id, content_name)


async def trigger_premium_content_offer(user_id: int, content_slug: str, session: AsyncSession, bot: Bot):
    """
    Public function to trigger premium content access offer from other handlers/services.
    This would be called when user tries to access premium content they don't have access to.
    """
    from bot.gamification.services.contextual_offer_service import ContextualOfferService
    from bot.gamification.services.premium_catalog_service import PremiumCatalogService

    offer_service = ContextualOfferService(session, bot)
    premium_service = PremiumCatalogService(session, bot)

    # Get the premium item details
    from bot.shop.database.models import ShopItem
    from sqlalchemy import select

    stmt = select(ShopItem).where(ShopItem.slug == content_slug)
    result = await session.execute(stmt)
    item = result.scalar_one_or_none()

    if item:
        content_name = item.name
    else:
        content_name = content_slug

    # Show premium content offer - similar to the blocked content offer but specific to premium
    user = await session.get(User, user_id)
    if not user or not user.is_vip:
        # User isn't VIP, so suggest VIP first
        await offer_service.show_contextual_vip_offer(user_id)
        return

    # User is VIP, show premium content offer
    message = f'''
Speaker: LUCIEN

"El contenido "{content_name}" requiere acceso Premium especial.

Este contenido fue producido exclusivamente para miembros VIP
que adquieran acceso individual.

Precio: {item.price_besitos if item else "25"} Favores"
    '''.strip()

    await bot.send_message(user_id, message)

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Ver catálogo Premium", callback_data="show_premium_catalog"),
        InlineKeyboardButton(text="Cancelar", callback_data="cancel_premium_view")
    )

    await bot.send_message(user_id, "¿Desea adquirir acceso a este contenido?", reply_markup=keyboard.as_markup())


# =============================
# F6.3: PREMIUM OFFERS FOR VIP
# =============================

@router.callback_query(F.data == "show_premium_catalog")
async def show_premium_catalog_handler(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Handle showing the premium catalog.
    """
    user_id = call.from_user.id

    offer_service = ContextualOfferService(session, bot)
    await offer_service.show_premium_catalog(user_id)
    await call.answer()


@router.callback_query(F.data.startswith("purchase_premium:"))
async def purchase_premium_handler(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Handle purchasing premium content.
    """
    from bot.gamification.services.premium_catalog_service import PremiumCatalogService

    content_id = int(call.data.split(":")[1])
    user_id = call.from_user.id

    service = PremiumCatalogService(session, bot)

    # Check if user already has this content
    if await service.has_purchased_content(user_id, content_id):
        await call.answer("Ya ha adquirido este contenido previamente.", show_alert=True)
        return

    # Process the purchase
    success = await service.purchase_premium_content(user_id, content_id)

    if success:
        await call.answer("¡Contenido adquirido exitosamente!", show_alert=True)
    else:
        await call.answer("Error en la compra. Verifique que tiene suficientes Favores.", show_alert=True)


@router.callback_query(F.data.startswith("show_premium_preview:"))
async def show_premium_preview_handler(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Handle showing premium content preview.
    """
    content_id = call.data.split(":")[1]

    # In a real implementation, you would show a preview of the content
    # For now, we'll just send a placeholder message

    message = f"""
Speaker: LUCIEN

"Preview del contenido Premium #{content_id}:

En este contenido especial, Diana explora temas íntimos
en una producción de alta calidad, exclusiva para
suscripciones Premium.

¿Desea adquirir este contenido ahora?"
    """.strip()

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Adquirir ahora", callback_data=f"purchase_premium:{content_id}"),
        InlineKeyboardButton(text="Cancelar", callback_data="cancel_premium_view")
    )

    await call.message.edit_text(message, reply_markup=keyboard.as_markup())
    await call.answer()


@router.callback_query(F.data == "decline_premium_offer")
async def decline_premium_offer_handler(call: CallbackQuery):
    """
    Handle declining a premium offer.
    """
    await call.message.edit_text("Entendido. Puede acceder al catálogo Premium en cualquier momento desde el menú.")
    await call.answer()


@router.callback_query(F.data == "cancel_premium_view")
async def cancel_premium_view_handler(call: CallbackQuery):
    """
    Handle canceling premium view.
    """
    await call.message.edit_text("Usted ha decidido no explorar este contenido en este momento.")
    await call.answer()


@router.callback_query(F.data.startswith("show_premium_content:"))
async def show_premium_content_details_handler(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Handle showing premium content details.
    """
    content_id = int(call.data.split(":")[1])

    from bot.gamification.services.contextual_offer_service import ContextualOfferService
    offer_service = ContextualOfferService(session, bot)
    await offer_service.show_premium_content_details(call.from_user.id, content_id)
    await call.answer()