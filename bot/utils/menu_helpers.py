"""
Menu Helpers - Funciones auxiliares para construcción de menús.

Reduce duplicación de código entre handlers.
"""
import logging
from datetime import datetime, timezone
from typing import Tuple

from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.enums import UserRole
from bot.services.container import ServiceContainer
from bot.utils.keyboards import create_inline_keyboard

logger = logging.getLogger(__name__)


async def build_start_menu(
    session: AsyncSession,
    bot,
    user_id: int,
    user_name: str,
    container: ServiceContainer = None
) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Construye el menú principal de /start para un usuario.

    Menú simplificado único para todos los usuarios.

    Args:
        session: Sesión de BD
        bot: Bot de Telegram
        user_id: ID del usuario de Telegram
        user_name: Nombre del usuario
        container: ServiceContainer opcional (no usado)

    Returns:
        Tuple de (welcome_message, keyboard)
    """
    # Mensaje de bienvenida simple
    welcome_message = (
        f"¡Hola <b>{user_name}</b>! 👋\n\n"
        f"Bienvenido/a al bot. Selecciona una opción del menú:"
    )

    # Keyboard simple y directo con botones principales
    keyboard = create_inline_keyboard([
        [{"text": "📺 Acceder al Canal VIP", "callback_data": "user:vip_access"}],
        [{"text": "📢 Unirse al Canal Free", "callback_data": "user:free_access"}],
        [{"text": "🎟️ Canjear Token VIP", "callback_data": "user:redeem_token"}],
        [{"text": "🏪 Tienda", "callback_data": "shop:main"}],
        [{"text": "📖 Historia", "callback_data": "narr:start"}],
        [{"text": "🎮 Juego Kinky", "callback_data": "user:profile"}],
    ])

    return welcome_message, keyboard
