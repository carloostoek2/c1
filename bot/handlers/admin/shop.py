"""
Shop Admin Handlers - Gestión de la tienda del Gabinete.

Este módulo contiene los handlers para los comandos de administración de la tienda.
Permite añadir, editar, deshabilitar items, ajustar stock y ver estadísticas.
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.filters import Command
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
        # Obtener estadísticas del Gabinete
        gabinete_stats = await container.gabinete.get_gabinete_stats()
        user_stats = await container.gabinete.get_user_gabinete_stats(callback.from_user.id)  # Este solo para el usuario admin

        text = (
            "📊 <b>Estadísticas de la Tienda del Gabinete</b>\n\n"
            f"• Total ventas: <b>{gabinete_stats['total_sales']}</b>\n"
            f"• Favores totales gastados: <b>{gabinete_stats['total_spent']}</b>\n\n"
        )

        if gabinete_stats['top_items']:
            text += "• Items más vendidos:\n"
            for item in gabinete_stats['top_items'][:5]:
                text += f"  - {item['name']}: {item['sales']} ventas\n"

        text += f"\n• Tus estadísticas: {user_stats['total_purchases']} compras, {user_stats['total_spent']} Favores gastados"

        await callback.message.edit_text(
            text=text,
            reply_markup=admin_shop_menu_keyboard(),
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


@shop_admin_router.callback_query(F.data == "admin:shop:add")
async def callback_admin_shop_add(callback: CallbackQuery, session: AsyncSession):
    """
    Handler para iniciar el wizard de añadir item.
    """
    logger.debug(f"➕ Usuario {callback.from_user.id} inició wizard de añadir item")

    text = (
        "➕ <b>Agregar Nuevo Ítem al Gabinete</b>\n\n"
        "Vamos a crear un nuevo ítem para el Gabinete.\n\n"
        "Por favor, proporciona la información del ítem:\n"
        "1. Categoría\n"
        "2. Nombre\n"
        "3. Precio\n"
        "4. Descripción\n"
        "5. Nivel requerido\n"
        "6. Tipo (consumible, permanente, etc.)\n"
        "7. Límites (si aplica)\n\n"
        "<i>Este wizard está en desarrollo. Por ahora, usa el script de seed_gabinete.py para añadir items.</i>"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=admin_shop_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("Wizard de añadir ítem en desarrollo")


@shop_admin_router.callback_query(F.data == "admin:shop:edit")
async def callback_admin_shop_edit(callback: CallbackQuery, session: AsyncSession):
    """
    Handler para editar un ítem existente.
    """
    logger.debug(f"✏️ Usuario {callback.from_user.id} inició edición de item")

    # Por ahora, simplemente mostrar un mensaje indicando que es funcionalidad futura
    text = (
        "✏️ <b>Editar Ítem del Gabinete</b>\n\n"
        "Proporciona el ID del ítem a editar:\n"
        "/admin_shop_edit &lt;item_id&gt;\n\n"
        "<i>Este comando está en desarrollo. Por ahora, modifica directamente en la base de datos.</i>"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=admin_shop_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("Edición de ítem en desarrollo")


@shop_admin_router.callback_query(F.data == "admin:shop:disable")
async def callback_admin_shop_disable(callback: CallbackQuery, session: AsyncSession):
    """
    Handler para desactivar un ítem.
    """
    logger.debug(f"🚫 Usuario {callback.from_user.id} inició desactivación de item")

    text = (
        "🚫 <b>Desactivar Ítem del Gabinete</b>\n\n"
        "Proporciona el ID del ítem a desactivar:\n"
        "/admin_shop_disable &lt;item_id&gt;\n\n"
        "<i>Este comando está en desarrollo. Por ahora, modifica directamente en la base de datos.</i>"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=admin_shop_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("Desactivación de ítem en desarrollo")


@shop_admin_router.callback_query(F.data == "admin:shop:stock")
async def callback_admin_shop_stock(callback: CallbackQuery, session: AsyncSession):
    """
    Handler para ajustar stock de ítem limitado.
    """
    logger.debug(f"📦 Usuario {callback.from_user.id} inició ajuste de stock")

    text = (
        "📦 <b>Ajustar Stock de Ítem Limitado</b>\n\n"
        "Proporciona el ID del ítem y nueva cantidad:\n"
        "/admin_shop_stock &lt;item_id&gt; &lt;cantidad&gt;\n\n"
        "<i>Este comando está en desarrollo. Por ahora, modifica directamente en la base de datos.</i>"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=admin_shop_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("Ajuste de stock en desarrollo")


@shop_admin_router.callback_query(F.data == "admin:shop:promo")
async def callback_admin_shop_promo(callback: CallbackQuery, session: AsyncSession):
    """
    Handler para crear promociones.
    """
    logger.debug(f"💰 Usuario {callback.from_user.id} inició creación de promoción")

    text = (
        "💰 <b>Crear Promoción Temporal</b>\n\n"
        "Crea promoción temporal para un ítem:\n"
        "/admin_shop_promo &lt;item_id&gt; &lt;descuento%&gt; &lt;duración_horas&gt;\n\n"
        "<i>Este comando está en desarrollo. Por ahora, se manejan promociones directamente en código.</i>"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=admin_shop_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer("Creación de promoción en desarrollo")


# =============================================================================
# COMANDOS DE ADMINISTRACIÓN
# =============================================================================


@shop_admin_router.message(Command("admin_shop_add"))
async def cmd_admin_shop_add(message: Message, session: AsyncSession):
    """
    Comando para añadir nuevo item al Gabinete.
    """
    logger.debug(f"➕ Usuario {message.from_user.id} usó comando /admin_shop_add")

    text = (
        "➕ <b>Agregar Nuevo Ítem al Gabinete</b>\n\n"
        "Este comando inicia un wizard para crear un nuevo ítem en el Gabinete.\n\n"
        "Por ahora, usa el script de seed_gabinete.py para añadir items:\n"
        "<code>python scripts/seed_gabinete.py</code>"
    )

    await message.answer(text, parse_mode="HTML")


@shop_admin_router.message(Command("admin_shop_edit"))
async def cmd_admin_shop_edit(message: Message, session: AsyncSession):
    """
    Comando para editar un ítem existente en el Gabinete.
    """
    logger.debug(f"✏️ Usuario {message.from_user.id} usó comando /admin_shop_edit")

    # Extraer parámetros
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []

    if not args:
        text = (
            "✏️ <b>Editar Ítem del Gabinete</b>\n\n"
            "Uso: <code>/admin_shop_edit &lt;item_id&gt;</code>\n\n"
            "Proporciona el ID del ítem a editar."
        )
        await message.answer(text, parse_mode="HTML")
        return

    try:
        item_id = int(args[0])
        text = (
            f"✏️ <b>Editando Ítem #{item_id}</b>\n\n"
            "Funcionalidad en desarrollo. Por ahora, edita directamente en la base de datos."
        )
        await message.answer(text, parse_mode="HTML")
    except ValueError:
        text = "❌ ID de ítem inválido. Debe ser un número."
        await message.answer(text)


@shop_admin_router.message(Command("admin_shop_disable"))
async def cmd_admin_shop_disable(message: Message, session: AsyncSession):
    """
    Comando para desactivar un ítem en el Gabinete (no eliminar).
    """
    logger.debug(f"🚫 Usuario {message.from_user.id} usó comando /admin_shop_disable")

    # Extraer parámetros
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []

    if not args:
        text = (
            "🚫 <b>Desactivar Ítem del Gabinete</b>\n\n"
            "Uso: <code>/admin_shop_disable &lt;item_id&gt;</code>\n\n"
            "Proporciona el ID del ítem a desactivar (no eliminar)."
        )
        await message.answer(text, parse_mode="HTML")
        return

    try:
        item_id = int(args[0])
        text = (
            f"🚫 <b>Desactivando Ítem #{item_id}</b>\n\n"
            "Funcionalidad en desarrollo. Por ahora, desactiva directamente en la base de datos."
        )
        await message.answer(text, parse_mode="HTML")
    except ValueError:
        text = "❌ ID de ítem inválido. Debe ser un número."
        await message.answer(text)


@shop_admin_router.message(Command("admin_shop_stock"))
async def cmd_admin_shop_stock(message: Message, session: AsyncSession):
    """
    Comando para ajustar stock de ítem limitado.
    """
    logger.debug(f"📦 Usuario {message.from_user.id} usó comando /admin_shop_stock")

    # Extraer parámetros
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []

    if len(args) < 2:
        text = (
            "📦 <b>Ajustar Stock de Ítem Limitado</b>\n\n"
            "Uso: <code>/admin_shop_stock &lt;item_id&gt; &lt;cantidad&gt;</code>\n\n"
            "Proporciona el ID del ítem y la nueva cantidad."
        )
        await message.answer(text, parse_mode="HTML")
        return

    try:
        item_id = int(args[0])
        quantity = int(args[1])
        text = (
            f"📦 <b>Ajustando Stock del Ítem #{item_id}</b>\n\n"
            f"Nueva cantidad: {quantity}\n\n"
            "Funcionalidad en desarrollo. Por ahora, ajusta directamente en la base de datos."
        )
        await message.answer(text, parse_mode="HTML")
    except ValueError:
        text = "❌ Parámetros inválidos. Deben ser números: /admin_shop_stock &lt;item_id&gt; &lt;cantidad&gt;"
        await message.answer(text)


@shop_admin_router.message(Command("admin_shop_stats"))
async def cmd_admin_shop_stats(message: Message, session: AsyncSession):
    """
    Comando para mostrar estadísticas de la tienda del Gabinete.
    """
    logger.debug(f"📊 Usuario {message.from_user.id} usó comando /admin_shop_stats")

    container = ServiceContainer(session, message.bot)

    try:
        # Obtener estadísticas del Gabinete
        gabinete_stats = await container.gabinete.get_gabinete_stats()
        user_stats = await container.gabinete.get_user_gabinete_stats(message.from_user.id)

        text = (
            "📊 <b>Estadísticas de la Tienda del Gabinete</b>\n\n"
            f"• Total ventas: <b>{gabinete_stats['total_sales']}</b>\n"
            f"• Favores totales gastados: <b>{gabinete_stats['total_spent']}</b>\n\n"
        )

        if gabinete_stats['top_items']:
            text += "• Items más vendidos:\n"
            for item in gabinete_stats['top_items'][:5]:
                text += f"  - {item['name']}: {item['sales']} ventas\n"

        text += f"\n• Tus estadísticas: {user_stats['total_purchases']} compras, {user_stats['total_spent']} Favores gastados"

        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas de tienda: {e}", exc_info=True)
        text = "❌ Hubo un problema al obtener las estadísticas de la tienda."
        await message.answer(text)


@shop_admin_router.message(Command("admin_shop_promo"))
async def cmd_admin_shop_promo(message: Message, session: AsyncSession):
    """
    Comando para crear una promoción temporal para un ítem.
    """
    logger.debug(f"💰 Usuario {message.from_user.id} usó comando /admin_shop_promo")

    # Extraer parámetros
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []

    if len(args) < 3:
        text = (
            "💰 <b>Crear Promoción Temporal</b>\n\n"
            "Uso: <code>/admin_shop_promo &lt;item_id&gt; &lt;descuento%&gt; &lt;duración_horas&gt;</code>\n\n"
            "Crea una promoción temporal para un ítem específico."
        )
        await message.answer(text, parse_mode="HTML")
        return

    try:
        item_id = int(args[0])
        discount_percent = float(args[1])
        duration_hours = int(args[2])
        text = (
            f"💰 <b>Creando Promoción para Ítem #{item_id}</b>\n\n"
            f"Descuento: {discount_percent}%\n"
            f"Duración: {duration_hours} horas\n\n"
            "Funcionalidad en desarrollo. Por ahora, crea promociones directamente en código."
        )
        await message.answer(text, parse_mode="HTML")
    except ValueError:
        text = "❌ Parámetros inválidos. Uso: /admin_shop_promo &lt;item_id&gt; &lt;descuento%&gt; &lt;duración_horas&gt;"
        await message.answer(text)