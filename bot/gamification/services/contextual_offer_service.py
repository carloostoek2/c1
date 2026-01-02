"""
Service for handling contextual offers to users.

Implements contextual offers for:
- F6.2: Ofertas Contextuales VIP (for FREE users)
- F6.3: VIP to Premium offers
- F6.4: VIP to Mapa del Deseo offers
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from aiogram import Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from bot.database.models import User, UserGamification, UserStreak
from bot.gamification.database.models import UserBehaviorSignals
from bot.gamification.messages import (
    CONVERSION_VIP_INTRO as CONTEXTUAL_VIP_INTRO,
    CONVERSION_VIP_THE_DIVAN as CONTEXTUAL_VIP_THE_DIVAN,
    ARCHETYPE_MESSAGES as ARCHETYPE_CONTEXTUAL_MESSAGES,
    LUCIEN_VIP_OFFER_MESSAGES as LUCIEN_CONTEXTUAL_OFFER_MESSAGES
)
from bot.gamification.services.archetype_conversion import ArchetypeConversionService

logger = logging.getLogger(__name__)


class ContextualOfferService:
    """
    Service for managing contextual offers to users.
    
    Handles F6.2: Ofertas Contextuales VIP for Free users who show high activity.
    """
    
    def __init__(self, session: AsyncSession, bot: Bot):
        self.session = session
        self.bot = bot

    async def should_show_contextual_vip_offer(self, user_id: int) -> bool:
        """
        Determines if a contextual VIP offer should be shown to a Free user.
        
        Conditions from F6.2:
        - User is Free level (not VIP)
        - Level 3+ de Favores (15+ besitos)
        - 7+ días desde registro
        - No ha visto oferta en últimos 3 días
        - No tiene invitation_declined_permanent (not in docs but logical)
        """
        # Get the user
        user = await self.session.get(User, user_id)
        if not user or user.is_vip:
            return False  # Only for Free users
            
        # Check if user has enough besitos (level 3+ = 15+ besitos estimated)
        user_gamification = await self.session.get(UserGamification, user_id)
        if not user_gamification or user_gamification.total_besitos < 15:
            return False
            
        # Check registration date (7+ days old)
        if (datetime.utcnow() - user.created_at).days < 7:
            return False
            
        # Check if user has seen offer in last 3 days
        # We would need to track this in a separate table, for now return True if other conditions met
        # In a real implementation, you'd have an OffersTracking table
        
        # Check if user has declined permanently (if such field exists)
        # For now, assume normal decline tracking
        
        return True

    async def show_contextual_vip_offer(self, user_id: int):
        """
        Shows a contextual VIP offer to a free user based on their activity.
        
        From F6.2:
        "Una observación, si me permite.
        
        Su actividad en Los Kinkys ha sido... notable.
        {reactions_count} reacciones. {days_active} días de presencia.
        
        Diana nota a quienes realmente prestan atención.
        
        Hay contenido en el Diván que creo apreciaría.
        No es una venta. Es una observación."
        """
        # Get user data
        user = await self.session.get(User, user_id)
        if not user:
            return
            
        user_gamification = await self.session.get(UserGamification, user_id)
        user_streak = await self.session.get(UserStreak, user_id)
        user_signals = await self.session.get(UserBehaviorSignals, user_id)
        
        # Calculate metrics for the message
        reactions_count = user_signals.reactions_made if user_signals else 0  # Assuming there's such field
        days_active = (datetime.utcnow() - user.created_at).days
        
        # This is a simplified version - in reality you'd need to track reactions separately
        # For now, using proxy values
        reactions_count = user_signals.total_interactions if user_signals else user_gamification.total_besitos if user_gamification else 50
        days_active = min(days_active, 30)  # Cap for display purposes
        
        # Get user archetype for personalized message
        archetype = user.archetype.name if user.archetype else "DEFAULT"
        archetype_service = ArchetypeConversionService()
        conversion_offer = archetype_service.get_conversion_message(
            user.archetype,
            count=150,  # placeholder for exclusive content count
            price=20,   # placeholder for price
            posts=2000, # placeholder for posts count
            monthly=50, # placeholder for monthly content
            value=150,  # placeholder for estimated value
            returns=3,  # placeholder for return count
            days=15     # placeholder for days active
        )
        
        # Create the contextual message
        message = f"""
 speaker: LUCIEN
[Aparece después de interacción normal]

"Una observación, si me permite.

Su actividad en Los Kinkys ha sido... notable.
{int(reactions_count)} reacciones. {days_active} días de presencia.

Diana nota a quienes realmente prestan atención.

{conversion_offer.message}"

        """.strip()

        # Add Lucien's message based on archetype
        import random
        lucien_messages = LUCIEN_CONTEXTUAL_OFFER_MESSAGES.get(archetype, LUCIEN_CONTEXTUAL_OFFER_MESSAGES["DEFAULT"])
        lucien_message = random.choice(lucien_messages)
        
        # Send messages to user
        await self.bot.send_message(user_id, message)
        await self.bot.send_message(user_id, lucien_message)
        
        # Create keyboard with options
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(text="Cuéntame más", callback_data="show_vip_offer_details"),
            InlineKeyboardButton(text="Quizás después", callback_data="decline_vip_offer")
        )
        
        await self.bot.send_message(user_id, "¿Desea conocer más sobre el Diván?", reply_markup=keyboard.as_markup())
        
        # In a real implementation, you would track that this offer was shown to prevent spam

    async def show_blocked_content_offer(self, user_id: int, content_name: str = "este contenido exclusivo"):
        """
        Shows an offer when user tries to access VIP-only content.
        
        From F6.2:
        "Este contenido está reservado para el Diván.
        
        Es uno de los {count} archivos exclusivos que Diana
        guarda para quienes han cruzado el umbral.
        
        Si tiene curiosidad por lo que hay detrás de esta puerta..."
        """
        user = await self.session.get(User, user_id)
        if not user:
            return
            
        # Get exclusive content count (placeholder - would come from database)
        exclusive_content_count = 450  # Placeholder
        
        message = f'''
Speaker: LUCIEN

"Este contenido "{content_name}" está reservado para el Diván.

Es uno de los {exclusive_content_count} archivos exclusivos que Diana
guarda para quienes han cruzado el umbral.

Si tiene curiosidad por lo que hay detrás de esta puerta..."
        '''.strip()
        
        await self.bot.send_message(user_id, message)
        
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(text="Ver cómo acceder", callback_data="show_vip_offer_details"),
            InlineKeyboardButton(text="Entendido", callback_data="dismiss_content_offer")
        )
        
        await self.bot.send_message(user_id, "¿Desea saber cómo acceder al contenido exclusivo?", reply_markup=keyboard.as_markup())

    async def has_seen_offer_recently(self, user_id: int, hours: int = 72) -> bool:
        """
        Check if user has seen a contextual offer recently.
        
        In a complete implementation, this would check an OffersTracking table.
        For now, we'll return False to allow offers to be shown.
        """
        # This would check a table tracking when offers were shown
        # For now, always return False to allow offers
        return False

    async def track_offer_shown(self, user_id: int, offer_type: str, context: Optional[Dict[str, Any]] = None):
        """
        Track that an offer was shown to a user.

        This would be implemented with an OffersTracking table in the future.
        """
        # Implementation would store in database that offer was shown
        logger.info(f"Offer '{offer_type}' shown to user {user_id} with context: {context}")

    # =============================
    # F6.3: PREMIUM OFFERS FOR VIP
    # =============================

    async def should_show_premium_offer(self, user_id: int, trigger: str = None) -> bool:
        """
        Determines if a premium offer should be shown to a VIP user.

        Conditions from F6.3:
        - User is VIP
        - Trigger: new premium content available, or completed Nivel 4
        """
        user = await self.session.get(User, user_id)
        if not user or not user.is_vip:
            return False  # Only for VIP users

        # For now, we'll check if there's new premium content
        # In a real implementation, you'd check for new premium content in the database
        # and if the trigger is "new_content_available"
        return True

    async def show_new_premium_content_offer(self, user_id: int, content_info: Dict[str, Any]):
        """
        Shows an offer for new premium content to VIP users.

        From F6.3:
        "Hay algo nuevo en la colección de Diana.

        '{nombre_contenido}'
        {descripción_breve}

        Duración: {duración}
        Categoría: {categoría}

        Este contenido no está incluido en el Diván estándar.
        Es una producción especial que Diana preparó aparte.

        Precio: {precio}"
        """
        user = await self.session.get(User, user_id)
        if not user:
            return

        message = f'''
Speaker: LUCIEN

"Hay algo nuevo en la colección de Diana.

"{content_info.get('name', 'Contenido Premium')}"
{content_info.get('description', 'Descripción breve del contenido')}

Duración: {content_info.get('duration', '12 min')}
Categoría: {content_info.get('category', 'Premium')}

Este contenido no está incluido en el Diván estándar.
Es una producción especial que Diana preparó aparte.

Precio: {content_info.get('price', '25')} Favores"
        '''.strip()

        await self.bot.send_message(user_id, message)

        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(text="Ver preview", callback_data=f"show_premium_preview:{content_info.get('id', '1')}"),
            InlineKeyboardButton(text="Adquirir ahora", callback_data=f"purchase_premium:{content_info.get('id', '1')}"),
            InlineKeyboardButton(text="No me interesa", callback_data="decline_premium_offer")
        )

        await self.bot.send_message(user_id, "¿Desea explorar este contenido especial?", reply_markup=keyboard.as_markup())

        # Track that the offer was shown
        await self.track_offer_shown(user_id, "premium_new_content", content_info)

    async def show_narrative_level_completion_premium_offer(self, user_id: int):
        """
        Shows premium catalog offer when user completes Nivel 4.

        From F6.3:
        "Ha demostrado comprensión del Diván.

        Hay contenido que Diana reserva para quienes llegan a este punto.
        No es parte del archivo regular. Es... Premium.

        Producciones especiales. Mayor duración. Mayor intensidad.

        Si desea explorar esta categoría, el catálogo está disponible."
        """
        user = await self.session.get(User, user_id)
        if not user:
            return

        message = '''
Speaker: LUCIEN

"Ha demostrado comprensión del Diván.

Hay contenido que Diana reserva para quienes llegan a este punto.
No es parte del archivo regular. Es... Premium.

Producciones especiales. Mayor duración. Mayor intensidad.

Si desea explorar esta categoría, el catálogo está disponible."
        '''.strip()

        await self.bot.send_message(user_id, message)

        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(text="Ver catálogo Premium", callback_data="show_premium_catalog"),
            InlineKeyboardButton(text="Continuar con la historia", callback_data="continue_narrative")
        )

        await self.bot.send_message(user_id, "¿Desea ver el catálogo Premium?", reply_markup=keyboard.as_markup())

        # Track that the offer was shown
        await self.track_offer_shown(user_id, "premium_narrative_completion", {
            "trigger": "narrative_level_4_complete"
        })

    async def show_premium_catalog(self, user_id: int):
        """
        Shows the premium catalog to user.

        From F6.3:
        "El Catálogo Premium de Diana:

        ━━━━━━━━━━━━━━━━━━━━━━━━

        {Para cada item Premium disponible:}

        📹 {nombre}
        {descripción_corta}
        Duración: {duración} | Precio: {precio}
        [Ver detalles]

        ━━━━━━━━━━━━━━━━━━━━━━━━

        Estos contenidos son independientes de su suscripción.
        Una vez adquiridos, son suyos permanentemente."
        """
        # In a real implementation, you'd fetch premium items from the database
        # For now, we'll use placeholder premium items
        premium_items = [
            {
                "id": 1,
                "name": "Sesión Íntima #1",
                "description": "Una sesión especial de 20 minutos con Diana",
                "duration": "20 min",
                "price": 35
            },
            {
                "id": 2,
                "name": "Detrás de Escenas",
                "description": "Contenido exclusivo de cómo se crean las producciones",
                "duration": "15 min",
                "price": 25
            },
            {
                "id": 3,
                "name": "Selección Curada #1",
                "description": "Colección especial de momentos seleccionados por Diana",
                "duration": "25 min",
                "price": 40
            }
        ]

        catalog_message = 'El Catálogo Premium de Diana:\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n'

        for item in premium_items:
            catalog_message += f'📹 {item["name"]}\n'
            catalog_message += f'{item["description"]}\n'
            catalog_message += f'Duración: {item["duration"]} | Precio: {item["price"]} Favores\n'
            catalog_message += f'[Ver detalles]\n\n'

        catalog_message += '━━━━━━━━━━━━━━━━━━━━━━━━\n\n'
        catalog_message += 'Estos contenidos son independientes de su suscripción.\n'
        catalog_message += 'Una vez adquiridos, son suyos permanentemente.'

        await self.bot.send_message(user_id, catalog_message)

        # Create keyboard with options for each item plus a back button
        keyboard = InlineKeyboardBuilder()

        for item in premium_items:
            keyboard.row(
                InlineKeyboardButton(
                    text=f"Detalles - {item['name']}",
                    callback_data=f"show_premium_content:{item['id']}"
                )
            )

        keyboard.row(InlineKeyboardButton(text="🔙 Volver", callback_data="back_to_main_menu"))

        await self.bot.send_message(user_id, "Seleccione un contenido para más detalles:", reply_markup=keyboard.as_markup())


    async def show_premium_content_details(self, user_id: int, content_id: int):
        """
        Shows details for a specific premium content item.
        """
        from bot.gamification.services.premium_catalog_service import PremiumCatalogService

        service = PremiumCatalogService(self.session, self.bot)
        item = await service.get_premium_content_by_id(content_id)

        if not item:
            # If item doesn't exist, send error message
            error_message = f"""
Speaker: LUCIEN

"Lo siento, el contenido Premium #{content_id} ya no está disponible.
Es posible que haya sido removido del catálogo."
            """.strip()
            await self.bot.send_message(user_id, error_message)
            return

        # Check if user already purchased this content
        has_purchased = await service.has_purchased_content(user_id, item.id)

        if has_purchased:
            message = f'''
Speaker: LUCIEN

"Usted ya ha adquirido este contenido Premium:

📹 {item.name}
{item.description}
Duración: {item.duration_hours or "N/A"} horas

Puede acceder a él en cualquier momento desde su inventario.'
            '''.strip()

            keyboard = InlineKeyboardBuilder()
            keyboard.row(
                InlineKeyboardButton(text="Ver en inventario", callback_data="show_inventory"),
                InlineKeyboardButton(text="Volver al catálogo", callback_data="show_premium_catalog")
            )
        else:
            message = f'''
Speaker: LUCIEN

"Detalles del contenido Premium:

📹 {item.name}
{item.description}
Duración: {item.duration_hours or "N/A"} horas
Precio: {item.price_besitos} Favores

¿Desea adquirir este contenido ahora?"
            '''.strip()

            keyboard = InlineKeyboardBuilder()
            keyboard.row(
                InlineKeyboardButton(text="Ver preview", callback_data=f"show_premium_preview:{content_id}"),
                InlineKeyboardButton(text="Adquirir ahora", callback_data=f"purchase_premium:{content_id}"),
                InlineKeyboardButton(text="Cancelar", callback_data="cancel_premium_view")
            )

        await self.bot.send_message(user_id, message, reply_markup=keyboard.as_markup())