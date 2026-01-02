"""
Handlers for admin-facing payment management.
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from bot.gamification.services.payment_service import PaymentService
from bot.gamification.messages import ADMIN_PAYMENT_APPROVED, ADMIN_PAYMENT_REJECTED

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data.startswith("admin_approve_payment:"))
async def approve_payment_handler(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Handles the admin's approval of a payment.
    """
    payment_id = int(call.data.split(":")[1])
    admin_id = call.from_user.id
    logger.info(f"Admin {admin_id} approved payment {payment_id}")

    payment_service = PaymentService(session, bot)
    success, message = await payment_service.approve_payment(payment_id, admin_id)

    if success:
        await call.message.edit_text(message)
        await call.answer("Pago aprobado con éxito.", show_alert=True)
    else:
        await call.answer(message, show_alert=True)


@router.callback_query(F.data.startswith("admin_reject_payment:"))
async def reject_payment_handler(call: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Handles the admin's rejection of a payment.
    """
    payment_id = int(call.data.split(":")[1])
    admin_id = call.from_user.id
    logger.info(f"Admin {admin_id} rejected payment {payment_id}")
    
    # For now, we don't have a reason mechanism, so we pass a default one.
    reason = "No se pudo verificar el pago."
    
    payment_service = PaymentService(session, bot)
    success, message = await payment_service.reject_payment(payment_id, admin_id, reason)
    
    if success:
        await call.message.edit_text(message)
        await call.answer("Pago rechazado.", show_alert=True)
    else:
        await call.answer(message, show_alert=True)
