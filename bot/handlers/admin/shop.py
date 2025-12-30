"""
Shop Admin Handlers - Gestión de la tienda del Gabinete.

Este módulo contiene los handlers para los comandos de administración de la tienda.
Permite añadir, editar, deshabilitar items, ajustar stock y ver estadísticas.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares import AdminAuthMiddleware, DatabaseMiddleware
from bot.services.container import ServiceContainer
from bot.utils.keyboards import create_inline_keyboard, back_to_main_menu_keyboard

logger = logging.getLogger(__name__)

# Router para handlers de administración de la tienda
shop_admin_router = Router(name="shop_admin")

# Aplicar middlewares (ya aplicados en admin_router principal, pero buena práctica)
shop_admin_router.message.middleware(DatabaseMiddleware())
shop_admin_router.message.middleware(AdminAuthMiddleware())
shop_admin_router.callback_query.middleware(DatabaseMiddleware())
shop_admin_router.callback_query.middleware(AdminAuthMiddleware())


def admin_shop_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard del menú principal de administración de la tienda.
    """
    return create_inline_keyboard([
        [{"text": "➕ Añadir Item", "callback_data": "admin:shop:add"}],
        [{"text": "✏️ Editar Item", "callback_data": "admin:shop:edit"}],
        [{"text": "🚫 Desactivar Item", "callback_data": "admin:shop:disable"}],
        [{"text": "📦 Ajustar Stock", "callback_data": "admin:shop:stock"}],
        [{"text": "📊 Estadísticas de Tienda", "callback_data": "admin:shop:stats"}],
        [{"text": "💰 Promociones", "callback_data": "admin:shop:promo"}],
        [{"text": "🔙 Volver al Menú Principal", "callback_data": "admin:main"}]
    ])


@shop_admin_router.callback_query(F.data == "admin:shop")
async def callback_admin_shop_main(callback: CallbackQuery, session: AsyncSession):
    """
    Handler para el menú principal de administración de la tienda.
    """
    logger.debug(f"🏪 Usuario {callback.from_user.id} abrió menú de administración de tienda")

    text = (
        "🏪 <b>Gestión de la Tienda del Gabinete</b>\n\n"
        "Desde aquí puedes administrar los ítems disponibles en la tienda, "
        "gestionar stock, crear promociones y ver estadísticas."
    )

    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=admin_shop_menu_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        if "message is not modified" not in str(e):
            logger.error(f"❌ Error editando mensaje del menú de tienda: {e}")
        else:
            logger.debug("ℹ️ Mensaje del menú de tienda sin cambios, ignorando")

    await callback.answer()


@shop_admin_router.callback_query(F.data == "admin:shop:stats")
async def callback_admin_shop_stats(callback: CallbackQuery, session: AsyncSession):
    """
    Handler para mostrar estadísticas de la tienda.
    """
    logger.debug(f"📊 Usuario {callback.from_user.id} solicitó estadísticas de tienda")

    await callback.answer("Calculando estadísticas de la tienda...", show_alert=False)

    container = ServiceContainer(session, callback.bot)

    try:
        # TODO: Implementar get_shop_stats en ShopService
        # stats = await container.shop.get_shop_stats()

        text = (
            "📊 <b>Estadísticas de la Tienda (WIP)</b>\n\n"
            "Aquí se mostrarán las estadísticas de la tienda:\n"
            "- Items más vendidos\n"
            "- Ingresos totales en Favores\n"
            "- Categoría más popular\n"
            "- Items sin ventas\n"
            "- Usuarios con más compras\n\n"
            "<i>(Funcionalidad en desarrollo)</i>"
        )

        await callback.message.edit_text(
            text=text,
            reply_markup=admin_shop_menu_keyboard(),  # Volver al menú de tienda
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas de tienda: {e}", exc_info=True)
        await callback.message.edit_text(
            "❌ <b>Error al obtener estadísticas de tienda</b>\n\n"
            "Hubo un problema al procesar la solicitud.",
            reply_markup=admin_shop_menu_keyboard(),
            parse_mode="HTML"
        )
    await callback.answer()