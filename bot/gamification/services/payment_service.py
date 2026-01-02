"""
Service layer for handling manual payments.
"""
import logging
from datetime import datetime
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from bot.database.models import PendingPayment, User, VIPSubscriber
from bot.gamification.services.besito import BesitoService
from config import Config
from bot.gamification.messages import ADMIN_NEW_PENDING_PAYMENT, USER_PAYMENT_APPROVED, USER_PAYMENT_REJECTED

logger = logging.getLogger(__name__)

class PaymentService:
    """
    Manages the logic for manual payment processing.
    """
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot

    async def create_pending_payment(
        self,
        user_id: int,
        product_type: str,
        amount: float,
        currency: str,
        screenshot_file_id: str,
        screenshot_message_id: int,
        product_id: int = None
    ) -> PendingPayment:
        """
        Creates a new pending payment record in the database.
        """
        logger.info(f"Creating pending payment for user {user_id}, product {product_type}")
        
        new_payment = PendingPayment(
            user_id=user_id,
            product_type=product_type,
            product_id=product_id,
            amount=amount,
            currency=currency,
            screenshot_file_id=screenshot_file_id,
            screenshot_message_id=screenshot_message_id,
            status='pending',
            created_at=datetime.utcnow()
        )
        self.session.add(new_payment)
        await self.session.commit()
        await self.session.refresh(new_payment)
        return new_payment

    async def notify_admin_for_approval(self, pending_payment_id: int):
        """
        Sends a notification to the admin group about a new pending payment.
        """
        logger.info(f"Notifying admins for pending payment {pending_payment_id}")
        
        stmt = select(PendingPayment).where(PendingPayment.id == pending_payment_id)
        result = await self.session.execute(stmt)
        payment = result.scalar_one_or_none()

        if not payment:
            logger.error(f"Pending payment with id {pending_payment_id} not found.")
            return

        user = await self.session.get(User, payment.user_id)
        if not user:
            logger.error(f"User with id {payment.user_id} not found for pending payment.")
            return
            
        text = ADMIN_NEW_PENDING_PAYMENT.format(
            full_name=user.full_name,
            username=user.username,
            user_id=user.user_id,
            amount=payment.amount,
            currency=payment.currency
        )
        
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(text="✅ Aprobar Pago", callback_data=f"admin_approve_payment:{payment.id}"),
            InlineKeyboardButton(text="❌ Rechazar", callback_data=f"admin_reject_payment:{payment.id}")
        )
        
        for admin_id in Config.ADMIN_USER_IDS:
            try:
                await self.bot.send_message(admin_id, text)
                await self.bot.send_photo(
                    admin_id, 
                    photo=payment.screenshot_file_id, 
                    reply_markup=keyboard.as_markup()
                )
            except Exception as e:
                logger.error(f"Failed to send payment notification to admin {admin_id}: {e}")

    async def approve_payment(self, pending_payment_id: int, admin_id: int):
        """
        Approves a pending payment, activates the product, and notifies the user.
        """
        from datetime import timedelta
        stmt = select(PendingPayment).where(PendingPayment.id == pending_payment_id)
        result = await self.session.execute(stmt)
        payment = result.scalar_one_or_none()

        if not payment:
            return False, "Pago pendiente no encontrado."
        if payment.status != 'pending':
            return False, f"El pago ya ha sido procesado (estado: {payment.status})."

        payment.status = 'approved'
        payment.processed_at = datetime.utcnow()
        payment.processed_by = admin_id
        
        expiry_date = await self.activate_product(payment.user_id, payment.product_type, payment.product_id)
        
        await self.session.commit()

        await self.bot.send_message(payment.user_id, USER_PAYMENT_APPROVED)

        from bot.gamification.messages import ADMIN_PAYMENT_APPROVED
        approval_message = ADMIN_PAYMENT_APPROVED.format(expiry_date=expiry_date.strftime("%Y-%m-%d"))
        return True, approval_message


    async def reject_payment(self, pending_payment_id: int, admin_id: int, reason: str):
        """
        Rejects a pending payment and notifies the user.
        """
        stmt = select(PendingPayment).where(PendingPayment.id == pending_payment_id)
        result = await self.session.execute(stmt)
        payment = result.scalar_one_or_none()

        if not payment:
            return False, "Pago pendiente no encontrado."
        if payment.status != 'pending':
            return False, f"El pago ya ha sido procesado (estado: {payment.status})."

        payment.status = 'rejected'
        payment.processed_at = datetime.utcnow()
        payment.processed_by = admin_id
        payment.admin_notes = reason
        await self.session.commit()

        # In a real scenario, we'd get the admin username from config
        admin_username = "diana_username" # Placeholder
        await self.bot.send_message(payment.user_id, USER_PAYMENT_REJECTED.format(admin_username=admin_username))

        from bot.gamification.messages import ADMIN_PAYMENT_REJECTED
        return True, ADMIN_PAYMENT_REJECTED


    async def activate_product(self, user_id: int, product_type: str, product_id: int = None) -> datetime:
        """
        Activates the purchased product for the user.
        Returns the expiry date of the subscription.
        """
        from datetime import timedelta
        from bot.narrative.services.narrative_service import NarrativeService
        from config import Config

        logger.info(f"Activating product {product_type} for user {user_id}")
        user = await self.session.get(User, user_id)
        if not user:
            logger.error(f"User {user_id} not found for product activation.")
            return

        expiry_date = None
        if product_type == "vip":
            user.role = 'VIP'

            # Create subscription record - for VIP, we make it indefinite
            # In the real system, VIP might be indefinite or have a specific duration
            duration_days = 365 * 2  # 2 years for VIP as an example
            expiry_date = datetime.utcnow() + timedelta(days=duration_days)

            # Check if user already has a subscription
            subscription = await self.session.get(VIPSubscriber, user_id)
            if subscription:
                subscription.expiry_date = expiry_date
                subscription.status = 'active'
            else:
                subscription = VIPSubscriber(
                    user_id=user_id,
                    expiry_date=expiry_date,
                    status='active'
                )
                self.session.add(subscription)

            # Grant welcome favors
            besito_service = BesitoService(self.session)
            await besito_service.grant_besitos(
                user_id=user_id,
                amount=15,
                description="Bienvenida al Diván"
            )

            # Activate narrative level 4 (the Diván content)
            narrative_service = NarrativeService(self.session)
            try:
                await narrative_service.unlock_narrative_level(user_id, 4)
                logger.info(f"Narrative level 4 activated for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to activate narrative level 4 for user {user_id}: {e}")

            # Add user to VIP channel - send bot command to add user
            # This would typically require bot to have admin rights in the channel
            if hasattr(Config, 'VIP_CHANNEL_ID') and Config.VIP_CHANNEL_ID:
                try:
                    # In a real implementation, we would invite the user to the VIP channel
                    # This requires the bot to have admin rights in the channel
                    # await self.bot.send_message(Config.VIP_CHANNEL_ID, f"Welcome {user.full_name} to the VIP channel!")
                    logger.info(f"User {user_id} should be added to VIP channel {Config.VIP_CHANNEL_ID}")
                except Exception as e:
                    logger.error(f"Failed to add user to VIP channel: {e}")

            logger.info(f"User {user_id} role updated to VIP. Subscription expires on {expiry_date}.")

        elif product_type == "premium":
            # For premium product - could be additional content, features, etc.
            duration_days = 30  # 1 month for premium as example
            expiry_date = datetime.utcnow() + timedelta(days=duration_days)

            # Similar process but for premium content/privileges
            user.role = 'VIP'  # Premium might also be VIP with additional privileges
            # Add premium-specific privileges here

        elif product_type == "mapa_del_deseo":
            # For Mapa del Deseo package
            duration_days = 180  # 6 months for Mapa del Deseo as example
            expiry_date = datetime.utcnow() + timedelta(days=duration_days)

            # Add Mapa del Deseo-specific privileges here

        await self.session.commit()
        return expiry_date
