"""
Conversion Commands Handler - Comandos de conversión y venta.

Flujo para que usuarios interactúen con productos de conversión:
- /vip (La Llave del Diván)
- /premium (Contenido individual)
- /mapa (Mapa del Deseo - 3 tiers)
"""

import logging
from datetime import datetime
from typing import Dict, Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.container import ServiceContainer
from bot.gamification.services.container import gamification_container
from bot.gamification.enums import ConversionEventType
from bot.gamification.services.lucien_objection_service import ObjectionType
from bot.utils.keyboards import create_inline_keyboard

logger = logging.getLogger(__name__)
conversion_router = Router()


@conversion_router.message(Command("vip", "premium", "mapa"))
async def handle_conversion_command(message: Message, session: AsyncSession):
    """
    Handle conversion commands: /vip, /premium, /mapa
    
    Args:
        message: Telegram message
        session: DB session
    """
    user_id = message.from_user.id
    command = message.text.split()[0][1:]  # Remove '/' from command
    
    logger.info(f"🎯 User {user_id} triggered conversion command: /{command}")
    
    # Track conversion view event
    await gamification_container.conversion_tracking.track_conversion_event(
        user_id=user_id,
        event_type=ConversionEventType.CONVERSION_VIEW,
        product_type=command,
        source=f"command_{command}",
        referrer=getattr(message, 'chat_id', None)
    )
    
    # Get user context for personalized response
    user_context = await get_user_context(user_id, session)
    
    if command == "vip":
        await show_vip_conversion_message(message, user_context)
    elif command == "premium":
        await show_premium_conversion_message(message, user_context)
    elif command == "mapa":
        await show_mapa_conversion_message(message, user_context)
    else:
        await message.answer("❌ Comando de conversión no reconocido.")


async def get_user_context(user_id: int, session: AsyncSession) -> Dict:
    """Get user context for personalized conversion responses."""
    container = ServiceContainer(session)
    
    # Get user data
    user = await container.user.get_user(user_id)
    
    # Get behavior signals
    behavior_signals = await gamification_container.behavior_tracking.get_behavior_signals(user_id)
    
    # Get archetype if available
    archetype = None
    if user and user.has_archetype:
        archetype = user.archetype
    
    # Get lead qualification
    lead_qual = await gamification_container.conversion_tracking.get_lead_qualification(user_id)
    
    return {
        "user": user,
        "archetype": archetype,
        "behavior_signals": behavior_signals,
        "lead_qualification": lead_qual
    }


async def show_vip_conversion_message(message: Message, user_context: Dict):
    """Show VIP conversion message (La Llave del Diván)."""
    await message.answer(
        "🔑 <b>La Llave del Diván</b>\n\n"
        "¿Listo/a para traspasar el umbral del Diván?\n\n"
        "<b>✨ Beneficios VIP:</b>\n"
        "• Acceso exclusivo a contenido premium\n"
        "• Interacción directa con Diana\n"
        "• Contenido personalizado según tu arquetipo\n"
        "• Prioridad en eventos y lanzamientos\n\n"
        "<b>💰 Inversión:</b>\n"
        "• Precio especial: $47 (1 mes)\n"
        "• Opción de descuento por mérito\n\n"
        "¿Te gustaría obtener tu <b>La Llave del Diván</b> hoy?",
        reply_markup=create_inline_keyboard([
            [{"text": "🔐 Obtener mi Llave", "callback_data": "conversion:vip:get_key"}],
            [{"text": "🤔 Tengo preguntas", "callback_data": "conversion:vip:questions"}],
            [{"text": "❌ No estoy interesado/a", "callback_data": "conversion:vip:objection:not_interested"}]
        ]),
        parse_mode="HTML"
    )


async def show_premium_conversion_message(message: Message, user_context: Dict):
    """Show Premium conversion message (Contenido individual)."""
    await message.answer(
        "💎 <b>Contenido Premium Individual</b>\n\n"
        "¿Buscas una experiencia única y personalizada?\n\n"
        "<b>🎯 Beneficios Premium:</b>\n"
        "• Sesión individual con Diana\n"
        "• Contenido adaptado a tus necesidades\n"
        "• Acceso a módulos exclusivos\n"
        "• Soporte personalizado\n\n"
        "<b>💰 Inversión:</b>\n"
        "• Desde $97 (sesión individual)\n"
        "• Paquetes disponibles con descuentos\n\n"
        "¿Te interesa una <b>experiencia Premium</b>?",
        reply_markup=create_inline_keyboard([
            [{"text": "💎 Ver opciones Premium", "callback_data": "conversion:premium:view_options"}],
            [{"text": "🤔 Tengo preguntas", "callback_data": "conversion:premium:questions"}],
            [{"text": "❌ No estoy interesado/a", "callback_data": "conversion:premium:objection:not_interested"}]
        ]),
        parse_mode="HTML"
    )


async def show_mapa_conversion_message(message: Message, user_context: Dict):
    """Show Mapa del Deseo conversion message (3 tiers)."""
    await message.answer(
        "🗺️ <b>Mapa del Deseo</b>\n\n"
        "Un viaje de autoconocimiento y manifestación.\n\n"
        "<b>🎁 Tiers disponibles:</b>\n"
        "<b>Bronce:</b> Acceso básico + 3 sesiones ($29)\n"
        "<b>Plata:</b> Contenido completo + 7 sesiones + comunidad ($79)\n"
        "<b>Oro:</b> Todo + sesiones individuales + soporte exclusivo ($147)\n\n"
        "¿Cuál tier te llama más?",
        reply_markup=create_inline_keyboard([
            [{"text": "🥉 Bronce", "callback_data": "conversion:mapa:bronze"}],
            [{"text": "🥈 Plata", "callback_data": "conversion:mapa:silver"}],
            [{"text": "🥇 Oro", "callback_data": "conversion:mapa:gold"}],
            [{"text": "🤔 Tengo preguntas", "callback_data": "conversion:mapa:questions"}],
            [{"text": "❌ No estoy interesado/a", "callback_data": "conversion:mapa:objection:not_interested"}]
        ]),
        parse_mode="HTML"
    )


@conversion_router.callback_query(F.data.startswith("conversion:vip:"))
async def handle_vip_conversion_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle VIP conversion callbacks."""
    user_id = callback.from_user.id
    callback_data = callback.data
    
    if callback_data == "conversion:vip:get_key":
        await callback.message.edit_text(
            "🔐 <b>Obtener mi Llave del Diván</b>\n\n"
            "Estás a punto de adquirir <b>La Llave del Diván</b>.\n\n"
            "<b>💳 Método de pago:</b>\n"
            "• Transferencia bancaria\n"
            "• Pago manual (aprobado por admin)\n\n"
            "<b>💰 Precio:</b> $47\n"
            "<b>🕐 Tiempo de activación:</b> 24 horas hábiles\n\n"
            "¿Deseas proceder con la compra?",
            reply_markup=create_inline_keyboard([
                [{"text": "💳 Proceder al pago", "callback_data": "conversion:vip:proceed_payment"}],
                [{"text": "📋 Ver datos bancarios", "callback_data": "conversion:vip:bank_info"}],
                [{"text": "❌ Cancelar", "callback_data": "conversion:vip:cancel"}]
            ]),
            parse_mode="HTML"
        )
    elif callback_data == "conversion:vip:questions":
        await callback.message.edit_text(
            "🤔 <b>Preguntas sobre La Llave del Diván</b>\n\n"
            "¿Qué te preocupa o te gustaría saber?\n"
            "Selecciona tu pregunta o escribe tu duda:",
            reply_markup=create_inline_keyboard([
                [{"text": "💰 ¿Por qué es tan caro?", "callback_data": "objection:too_expensive"}],
                [{"text": "📚 ¿Qué contenido hay?", "callback_data": "conversion:vip:content_info"}],
                [{"text": "⏰ ¿Tengo tiempo suficiente?", "callback_data": "objection:too_busy"}],
                [{"text": "🔄 ¿Hay garantía?", "callback_data": "objection:no_proof"}],
                [{"text": "💬 Hablar con Lucien", "callback_data": "conversion:vip:talk_to_lucien"}],
                [{"text": "🔙 Volver", "callback_data": "conversion:vip:back_to_main"}]
            ]),
            parse_mode="HTML"
        )
    elif callback_data.startswith("conversion:vip:objection:"):
        objection_type = callback_data.split(":")[-1]
        await handle_conversion_objection(callback, session, objection_type, "vip")
    
    await callback.answer()


@conversion_router.callback_query(F.data.startswith("conversion:premium:"))
async def handle_premium_conversion_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle Premium conversion callbacks."""
    user_id = callback.from_user.id
    callback_data = callback.data
    
    if callback_data == "conversion:premium:view_options":
        await callback.message.edit_text(
            "💎 <b>Opciones Premium Disponibles</b>\n\n"
            "<b>🎯 Sesión Individual:</b>\n"
            "• 1 hora de sesión personalizada\n"
            "• Contenido adaptado a ti\n"
            "• Precio: $97\n\n"
            "<b>📦 Paquete Básico:</b>\n"
            "• 3 sesiones\n"
            "• Grabaciones incluidas\n"
            "• Precio: $247 ($82 por sesión)\n\n"
            "<b>🌟 Paquete Premium:</b>\n"
            "• 5 sesiones\n"
            "• Grabaciones + guías\n"
            "• Soporte 1 mes\n"
            "• Precio: $397 ($79 por sesión)\n\n"
            "¿Cuál opción te interesa?",
            reply_markup=create_inline_keyboard([
                [{"text": "🎯 Individual", "callback_data": "conversion:premium:individual"}],
                [{"text": "📦 Básico", "callback_data": "conversion:premium:basic"}],
                [{"text": "🌟 Premium", "callback_data": "conversion:premium:premium"}],
                [{"text": "❌ Cancelar", "callback_data": "conversion:premium:cancel"}]
            ]),
            parse_mode="HTML"
        )
    elif callback_data == "conversion:premium:questions":
        await callback.message.edit_text(
            "🤔 <b>Preguntas sobre Premium</b>\n\n"
            "¿Qué te gustaría saber sobre nuestras opciones Premium?",
            reply_markup=create_inline_keyboard([
                [{"text": "💰 ¿Por qué es tan caro?", "callback_data": "objection:too_expensive"}],
                [{"text": "📚 ¿Qué incluye cada opción?", "callback_data": "conversion:premium:options_info"}],
                [{"text": "⏰ ¿Cuánto tiempo dura cada sesión?", "callback_data": "objection:too_busy"}],
                [{"text": "🔄 ¿Hay posibilidad de reintegro?", "callback_data": "objection:trust_issues"}],
                [{"text": "💬 Hablar con Lucien", "callback_data": "conversion:premium:talk_to_lucien"}],
                [{"text": "🔙 Volver", "callback_data": "conversion:premium:back_to_main"}]
            ]),
            parse_mode="HTML"
        )
    elif callback_data.startswith("conversion:premium:objection:"):
        objection_type = callback_data.split(":")[-1]
        await handle_conversion_objection(callback, session, objection_type, "premium")
    
    await callback.answer()


@conversion_router.callback_query(F.data.startswith("conversion:mapa:"))
async def handle_mapa_conversion_callback(callback: CallbackQuery, session: AsyncSession):
    """Handle Mapa del Deseo conversion callbacks."""
    user_id = callback.from_user.id
    callback_data = callback.data
    
    if callback_data == "conversion:mapa:bronze":
        await callback.message.edit_text(
            "🥉 <b>Tier Bronce - Mapa del Deseo</b>\n\n"
            "<b>✅ Incluye:</b>\n"
            "• Acceso al Mapa del Deseo\n"
            "• 3 sesiones guiadas\n"
            "• Material descargable\n"
            "• Comunidad básica\n\n"
            "<b>💰 Precio:</b> $29\n\n"
            "¿Quieres adquirir el tier Bronce?",
            reply_markup=create_inline_keyboard([
                [{"text": "💳 Comprar Bronce", "callback_data": "conversion:mapa:bronze_pay"}],
                [{"text": "❌ Cancelar", "callback_data": "conversion:mapa:cancel"}]
            ]),
            parse_mode="HTML"
        )
    elif callback_data == "conversion:mapa:silver":
        await callback.message.edit_text(
            "🥈 <b>Tier Plata - Mapa del Deseo</b>\n\n"
            "<b>✅ Incluye:</b>\n"
            "• Todo del tier Bronce\n"
            "• 7 sesiones guiadas\n"
            "• Material exclusivo\n"
            "• Comunidad VIP\n"
            "• Seguimiento personalizado\n\n"
            "<b>💰 Precio:</b> $79\n\n"
            "¿Quieres adquirir el tier Plata?",
            reply_markup=create_inline_keyboard([
                [{"text": "💳 Comprar Plata", "callback_data": "conversion:mapa:silver_pay"}],
                [{"text": "❌ Cancelar", "callback_data": "conversion:mapa:cancel"}]
            ]),
            parse_mode="HTML"
        )
    elif callback_data == "conversion:mapa:gold":
        await callback.message.edit_text(
            "🥇 <b>Tier Oro - Mapa del Deseo</b>\n\n"
            "<b>✅ Incluye:</b>\n"
            "• Todo de los otros tiers\n"
            "• Sesiones individuales con Diana\n"
            "• Soporte personalizado\n"
            "• Acceso exclusivo a contenido\n"
            "• Mentoría 1:1\n\n"
            "<b>💰 Precio:</b> $147\n\n"
            "¿Quieres adquirir el tier Oro?",
            reply_markup=create_inline_keyboard([
                [{"text": "💳 Comprar Oro", "callback_data": "conversion:mapa:gold_pay"}],
                [{"text": "❌ Cancelar", "callback_data": "conversion:mapa:cancel"}]
            ]),
            parse_mode="HTML"
        )
    elif callback_data == "conversion:mapa:questions":
        await callback.message.edit_text(
            "🤔 <b>Preguntas sobre el Mapa del Deseo</b>\n\n"
            "¿Qué te gustaría saber sobre el Mapa del Deseo?",
            reply_markup=create_inline_keyboard([
                [{"text": "💰 ¿Por qué tanto precio por tier?", "callback_data": "objection:too_expensive"}],
                [{"text": "📚 ¿Qué es exactamente el Mapa?", "callback_data": "conversion:mapa:what_is"}],
                [{"text": "⏰ ¿Cuánto tiempo debo dedicar?", "callback_data": "objection:too_busy"}],
                [{"text": "🔄 ¿Puedo probar antes de comprar?", "callback_data": "objection:no_proof"}],
                [{"text": "💬 Hablar con Lucien", "callback_data": "conversion:mapa:talk_to_lucien"}],
                [{"text": "🔙 Volver", "callback_data": "conversion:mapa:back_to_main"}]
            ]),
            parse_mode="HTML"
        )
    elif callback_data.startswith("conversion:mapa:objection:"):
        objection_type = callback_data.split(":")[-1]
        await handle_conversion_objection(callback, session, objection_type, "mapa")
    
    await callback.answer()


async def handle_conversion_objection(
    callback: CallbackQuery, 
    session: AsyncSession, 
    objection_type: str, 
    product_type: str
):
    """Handle conversion objection with Lucien's response."""
    user_id = callback.from_user.id
    
    # Map string objection to enum
    objection_enum_map = {
        "too_expensive": ObjectionType.TOO_EXPENSIVE,
        "not_interested": ObjectionType.NOT_INTERESTED,
        "too_busy": ObjectionType.TOO_BUSY,
        "no_proof": ObjectionType.NO_VALUE,
        "trust_issues": ObjectionType.TRUST_ISSUES,
        "not_now": ObjectionType.NOT_NOW,
        "personal_circumstances": ObjectionType.PERSONAL_CIRCUMSTANCES,
        "alternative_choice": ObjectionType.ALTERNATIVE_CHOICE,
    }
    
    objection_enum = objection_enum_map.get(objection_type, ObjectionType.NOT_INTERESTED)
    
    # Get user context
    user_context = await get_user_context(user_id, session)
    
    # Get Lucien's response
    lucien_response = await gamification_container.lucien_objection.handle_objection(
        user_id=user_id,
        objection_type=objection_enum,
        user_context=user_context
    )
    
    # Show Lucien's response
    await callback.message.edit_text(
        f"🎩 <b>Lucien responde:</b>\n\n{lucien_response}\n\n"
        f"¿Te gustaría reconsiderar tu interés en {product_type.upper()}?",
        reply_markup=create_inline_keyboard([
            [{"text": "💡 Me convenciste", "callback_data": f"conversion:{product_type}:reconsider"}],
            [{"text": "❌ Sigo sin interés", "callback_data": f"conversion:{product_type}:final_no"}],
            [{"text": "💬 Otro comentario", "callback_data": f"conversion:{product_type}:more_questions"}]
        ]),
        parse_mode="HTML"
    )


@conversion_router.callback_query(F.data.startswith("objection:"))
async def handle_general_objection(callback: CallbackQuery, session: AsyncSession):
    """Handle general objection callbacks."""
    user_id = callback.from_user.id
    objection_key = callback.data.split(":")[1]
    
    # Track original event type
    original_event = callback.data
    
    # Map objection key to enum
    objection_enum_map = {
        "too_expensive": ObjectionType.TOO_EXPENSIVE,
        "no_proof": ObjectionType.NO_VALUE,
        "too_busy": ObjectionType.TOO_BUSY,
        "trust_issues": ObjectionType.TRUST_ISSUES,
        "not_now": ObjectionType.NOT_NOW,
    }
    
    objection_type = objection_enum_map.get(objection_key, ObjectionType.NO_VALUE)
    
    # Get user context
    user_context = await get_user_context(user_id, session)
    
    # Get Lucien's response
    lucien_response = await gamification_container.lucien_objection.handle_objection(
        user_id=user_id,
        objection_type=objection_type,
        user_context=user_context
    )
    
    # Show response
    await callback.message.edit_text(
        f"🎩 <b>Lucien responde:</b>\n\n{lucien_response}",
        reply_markup=create_inline_keyboard([
            [{"text": "🔙 Volver", "callback_data": "conversion:back_to_main"}]
        ]),
        parse_mode="HTML"
    )
    
    await callback.answer()
