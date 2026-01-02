"""
Handlers for user-facing conversion flows.
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from bot.database.models import User
from bot.gamification.states.conversion import ConversionStates
from bot.gamification.services.payment_service import PaymentService
from bot.gamification.messages import (
    CONVERSION_VIP_INTRO, CONVERSION_VIP_THE_DIVAN, ARCHETYPE_MESSAGES,
    CONVERSION_VIP_OFFER, CONVERSION_VIP_BENEFITS, CONVERSION_VIP_MANUAL_PAYMENT_INFO,
    CONVERSION_VIP_REQUEST_SCREENSHOT, CONVERSION_VIP_SCREENSHOT_RECEIVED,
    CONVERSION_VIP_DECLINED, LUCIEN_VIP_OFFER_MESSAGES as CONVERSION_LUCIEN_VIP_OFFER_MESSAGES
)
from bot.gamification.config import GamificationConfig

logger = logging.getLogger(__name__)
router = Router()

# NOTE: Price is now fetched from database subscription_plans table
# instead of being hardcoded. See get_vip_pricing() below.

async def get_vip_pricing(session: AsyncSession) -> tuple[float, str]:
    """
    Get VIP pricing from database subscription_plans.
    Falls back to config if not found.
    """
    from bot.database.models import SubscriptionPlan
    from sqlalchemy import select

    # Try to get active VIP plan
    stmt = select(SubscriptionPlan).where(
        SubscriptionPlan.is_active == True
    ).order_by(SubscriptionPlan.duration_days.asc()).limit(1)

    result = await session.execute(stmt)
    plan = result.scalar_one_or_none()

    if plan:
        return plan.price_usd, "USD"

    # Fallback to default if no plan configured
    return 15.0, "USD"


async def get_user_archetype(session: AsyncSession, user_id: int) -> str:
    """Gets the user's archetype from the database."""
    user = await session.get(User, user_id)
    if user and user.archetype:
        return user.archetype.name
    return "DEFAULT"


@router.message(F.text.lower() == "/vip")
async def start_vip_conversion(message: Message, session: AsyncSession):
    """Presents the initial VIP conversion offer."""
    await message.answer(CONVERSION_VIP_INTRO)
    await message.answer(CONVERSION_VIP_THE_DIVAN)

    archetype = await get_user_archetype(session, message.from_user.id)
    archetype_message = ARCHETYPE_MESSAGES.get(archetype, ARCHETYPE_MESSAGES["DEFAULT"])
    await message.answer(archetype_message)

    # Add Lucien's messages based on archetype
    import random
    lucien_messages = CONVERSION_LUCIEN_VIP_OFFER_MESSAGES.get(archetype, CONVERSION_LUCIEN_VIP_OFFER_MESSAGES["DEFAULT"])
    lucien_message = random.choice(lucien_messages)
    await message.answer(lucien_message)

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="🔑 Ver la Llave del Diván", callback_data="show_vip_offer_details"),
        InlineKeyboardButton(text="Necesito pensarlo", callback_data="decline_vip_offer")
    )
    await message.answer(CONVERSION_VIP_OFFER, reply_markup=keyboard.as_markup())


@router.callback_query(F.data == "show_vip_offer_details")
async def show_vip_offer_details(call: CallbackQuery, session: AsyncSession):
    """Shows the detailed VIP offer."""
    # In the future, we can calculate discounts here
    discount_text = ""

    # Get current VIP pricing from database
    vip_price, currency = await get_vip_pricing(session)

    text = CONVERSION_VIP_BENEFITS.format(price=vip_price, currency=currency, discount_text=discount_text)

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="🔑 Obtener mi Llave", callback_data="get_vip_key"),
        InlineKeyboardButton(text="Ahora no", callback_data="decline_vip_offer")
    )
    await call.message.edit_text(text, reply_markup=keyboard.as_markup())
    await call.answer()


@router.callback_query(F.data == "decline_vip_offer")
async def decline_vip_offer(call: CallbackQuery, session: AsyncSession):
    """Handles the user declining the VIP offer."""
    await call.message.edit_text(CONVERSION_VIP_DECLINED)
    await call.answer()


@router.callback_query(F.data == "get_vip_key")
async def get_vip_key(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    """Handles the user's request to get the VIP key, showing payment info."""
    # Get current VIP pricing from database
    vip_price, currency = await get_vip_pricing(session)

    # Check if payment info is configured
    if not GamificationConfig.is_payment_configured():
        await call.answer("La información de pago no está configurada. Contacte al administrador.", show_alert=True)
        return

    payment_info_text = CONVERSION_VIP_MANUAL_PAYMENT_INFO.format(
        price=vip_price, currency=currency, **GamificationConfig.PAYMENT_INFO
    )

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="✅ Ya realicé el pago", callback_data="confirm_payment_done"),
        InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel_payment")
    )

    await call.message.edit_text(payment_info_text, reply_markup=keyboard.as_markup())
    await call.answer()


@router.callback_query(F.data == "confirm_payment_done")
async def confirm_payment_done(call: CallbackQuery, state: FSMContext):
    """Requests the user to send the payment screenshot."""
    await state.set_state(ConversionStates.waiting_for_payment_screenshot)
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Cancelar", callback_data="cancel_payment"))
    
    await call.message.edit_text(CONVERSION_VIP_REQUEST_SCREENSHOT, reply_markup=keyboard.as_markup())
    await call.answer()


@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(call: CallbackQuery, state: FSMContext):
    """Cancels the payment process."""
    await state.clear()
    await call.message.edit_text("El proceso de pago ha sido cancelado.")
    await call.answer()


@router.message(ConversionStates.waiting_for_payment_screenshot, F.photo)
async def payment_screenshot_received(message: Message, session: AsyncSession, state: FSMContext, bot: Bot):
    """Handles the reception of the payment screenshot."""
    photo = message.photo[-1]

    # Get current VIP pricing from database
    vip_price, currency = await get_vip_pricing(session)

    payment_service = PaymentService(session, bot)

    # Create pending payment
    pending_payment = await payment_service.create_pending_payment(
        user_id=message.from_user.id,
        product_type="vip",
        amount=vip_price,
        currency=currency,
        screenshot_file_id=photo.file_id,
        screenshot_message_id=message.message_id
    )

    # Notify admin
    await payment_service.notify_admin_for_approval(pending_payment.id)

    text = CONVERSION_VIP_SCREENSHOT_RECEIVED.format(price=vip_price, currency=currency)
    await message.reply(text)
    await state.clear()


@router.message(ConversionStates.waiting_for_payment_screenshot)
async def handle_non_photo_in_screenshot_state(message: Message, state: FSMContext):
    """Handles any message that is not a photo when waiting for the screenshot."""
    await message.reply("Por favor envíe una captura de pantalla del pago.")
