"""
Handlers de usuario para El Gabinete de Lucien (Fase 4).

Flujos completos con:
- Verificacion de nivel de acceso
- Sistema de descuentos
- Items limitados y temporales
- Inventario y uso de items
"""

import logging
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from bot.shop.services.gabinete import GabineteService
from bot.shop.services.discount import DiscountService
from bot.shop.database.enums import GabineteCategory, ItemVisibility
from bot.utils.keyboards import create_inline_keyboard

logger = logging.getLogger(__name__)

# Router para handlers del Gabinete
gabinete_router = Router(name="gabinete")

# Aplicar middleware de database
from bot.middlewares import DatabaseMiddleware
gabinete_router.message.middleware(DatabaseMiddleware())
gabinete_router.callback_query.middleware(DatabaseMiddleware())


# =============================================================================
# HELPERS
# =============================================================================

async def _get_user_data(session: AsyncSession, user_id: int) -> tuple[float, int]:
    """Obtiene balance y nivel del usuario."""
    balance = 0.0
    level = 1

    try:
        from bot.gamification.database.models import UserGamification
        from bot.gamification.services.level import LevelService

        user_gamif = await session.get(UserGamification, user_id)
        if user_gamif:
            balance = user_gamif.total_besitos

            # Obtener nivel actual
            level_service = LevelService(session)
            current_level = await level_service.get_user_level(user_id)
            if current_level:
                level = current_level.order
    except Exception as e:
        logger.warning(f"Error obteniendo datos del usuario {user_id}: {e}")

    return balance, level


def _build_gabinete_welcome_keyboard(user_level: int) -> InlineKeyboardMarkup:
    """Construye teclado principal del Gabinete segun nivel."""
    buttons = []

    # Categorias basicas (nivel 1+)
    buttons.append([{"text": "⚡ Efimeros", "callback_data": "gab:cat:ephemeral"}])
    buttons.append([{"text": "🎖️ Distintivos", "callback_data": "gab:cat:distinctive"}])

    # Llaves (nivel 2+ para ver)
    if user_level >= 2:
        buttons.append([{"text": "🔑 Llaves", "callback_data": "gab:cat:keys"}])
    else:
        buttons.append([{"text": "🔒 Llaves (Nivel 2)", "callback_data": "gab:locked:2"}])

    # Reliquias (nivel 4+ para ver)
    if user_level >= 4:
        buttons.append([{"text": "💎 Reliquias", "callback_data": "gab:cat:relics"}])
    else:
        buttons.append([{"text": "🔒 Reliquias (Nivel 4)", "callback_data": "gab:locked:4"}])

    # Secretos (nivel 6+ para ver)
    if user_level >= 6:
        buttons.append([{"text": "🤫 Secretos", "callback_data": "gab:cat:secret"}])

    # Inventario y Volver
    buttons.append([{"text": "📦 Mi Inventario", "callback_data": "gab:inventory"}])
    buttons.append([{"text": "🔙 Volver", "callback_data": "start:menu"}])

    return create_inline_keyboard(buttons)


def _build_category_items_keyboard(
    items: list,
    category_slug: str,
    user_level: int,
    page: int = 0,
    items_per_page: int = 5
) -> InlineKeyboardMarkup:
    """Construye teclado de items de una categoria."""
    buttons = []

    # Paginacion
    start = page * items_per_page
    end = start + items_per_page
    page_items = items[start:end]

    for item in page_items:
        # Verificar si puede comprar
        can_buy = user_level >= item.min_level_to_buy
        icon = item.icon

        if not can_buy:
            text = f"🔒 {item.name} (Nivel {item.min_level_to_buy})"
        elif item.is_limited and item.stock is not None and item.stock <= 3:
            text = f"{icon} {item.name} — {item.price_besitos}F (¡{item.stock} left!)"
        else:
            text = f"{icon} {item.name} — {item.price_besitos} Favor(es)"

        buttons.append([{
            "text": text,
            "callback_data": f"gab:item:{item.id}"
        }])

    # Navegacion de paginas
    nav_buttons = []
    if page > 0:
        nav_buttons.append({
            "text": "⬅️ Anterior",
            "callback_data": f"gab:cat:{category_slug}:{page-1}"
        })
    if end < len(items):
        nav_buttons.append({
            "text": "Siguiente ➡️",
            "callback_data": f"gab:cat:{category_slug}:{page+1}"
        })
    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([{"text": "🔙 Volver al Gabinete", "callback_data": "gab:main"}])

    return create_inline_keyboard(buttons)


# =============================================================================
# HANDLER PRINCIPAL
# =============================================================================

@gabinete_router.message(Command("gabinete"))
async def cmd_gabinete(message: Message, session: AsyncSession):
    """Handler para /gabinete - Muestra el Gabinete de Lucien."""
    user_id = message.from_user.id
    balance, level = await _get_user_data(session, user_id)

    # Obtener descuento
    discount_service = DiscountService(session)
    discount = await discount_service.calculate_total_discount(user_id, level)

    text = (
        "<b>El Gabinete de Lucien</b>\n\n"
        "<i>\"Bienvenido a mi espacio personal. Aqui guardo objetos que Diana ha "
        "autorizado para intercambio. Algunos valiosos. Otros... menos.\n\n"
        "Cada categoria tiene su proposito. Explore. Pero no espere "
        "que le venda cualquier cosa. Algunos items requieren... merito.\"</i>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Sus Favores: <b>{balance:.1f}</b>\n"
        f"📊 Su nivel: <b>{level}</b>\n"
    )

    if discount.total_discount > 0:
        text += f"🏷️ Su descuento: <b>{discount.total_discount:.0f}%</b>\n"

    text += f"━━━━━━━━━━━━━━━━━━━━━━━"

    await message.answer(
        text,
        reply_markup=_build_gabinete_welcome_keyboard(level),
        parse_mode="HTML"
    )


@gabinete_router.callback_query(F.data == "gab:main")
async def callback_gabinete_main(callback: CallbackQuery, session: AsyncSession):
    """Callback para volver al menu principal del Gabinete."""
    user_id = callback.from_user.id
    balance, level = await _get_user_data(session, user_id)

    discount_service = DiscountService(session)
    discount = await discount_service.calculate_total_discount(user_id, level)

    text = (
        "<b>El Gabinete de Lucien</b>\n\n"
        f"💰 Sus Favores: <b>{balance:.1f}</b>\n"
        f"📊 Su nivel: <b>{level}</b>\n"
    )

    if discount.total_discount > 0:
        text += f"🏷️ Su descuento: <b>{discount.total_discount:.0f}%</b>\n"

    text += (
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        "<i>\"¿Que busca hoy?\"</i>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=_build_gabinete_welcome_keyboard(level),
        parse_mode="HTML"
    )
    await callback.answer()


@gabinete_router.callback_query(F.data.startswith("gab:locked:"))
async def callback_gabinete_locked(callback: CallbackQuery):
    """Callback cuando el usuario intenta acceder a categoria bloqueada."""
    required_level = callback.data.split(":")[2]
    await callback.answer(
        f"Requiere nivel {required_level} para acceder a esta seccion.",
        show_alert=True
    )


# =============================================================================
# CATEGORIAS
# =============================================================================

CATEGORY_DESCRIPTIONS = {
    "ephemeral": "⚡ <b>Efimeros</b>\n\n<i>\"Placeres de un solo uso. Intensos pero fugaces. Como ciertos momentos con Diana.\"</i>",
    "distinctive": "🎖️ <b>Distintivos</b>\n\n<i>\"Marcas visibles de su posicion en este universo. Para quienes valoran el reconocimiento publico.\"</i>",
    "keys": "🔑 <b>Llaves</b>\n\n<i>\"Abren puertas a contenido que otros no pueden ver. El conocimiento tiene precio.\"</i>",
    "relics": "💎 <b>Reliquias</b>\n\n<i>\"Los objetos mas valiosos del Gabinete. Requieren Favores considerables... y dignidad demostrada.\"</i>",
    "secret": "🤫 <b>Secretos</b>\n\n<i>\"Algunos secretos solo se revelan a quienes han demostrado... discrecion.\"</i>",
}


@gabinete_router.callback_query(F.data.startswith("gab:cat:"))
async def callback_gabinete_category(callback: CallbackQuery, session: AsyncSession):
    """Callback para ver items de una categoria."""
    user_id = callback.from_user.id
    balance, level = await _get_user_data(session, user_id)

    parts = callback.data.split(":")
    category_slug = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    gabinete_service = GabineteService(session)

    # Obtener categoria
    category = await gabinete_service.get_category_by_slug(category_slug)
    if not category:
        await callback.answer("Categoria no encontrada", show_alert=True)
        return

    # Verificar acceso
    can_view, can_buy, reason = await gabinete_service.can_user_access_category(
        category, level
    )

    if not can_view:
        await callback.answer(reason, show_alert=True)
        return

    # Obtener items
    items = await gabinete_service.get_items_by_category(
        category_slug, level, include_hidden=(level >= 6)
    )

    # Construir texto
    desc = CATEGORY_DESCRIPTIONS.get(category_slug, f"<b>{category.name}</b>")
    text = f"{desc}\n\n💰 Sus Favores: <b>{balance:.1f}</b>"

    if not items:
        text += "\n\n<i>No hay articulos disponibles en esta seccion.</i>"
        keyboard = create_inline_keyboard([
            [{"text": "🔙 Volver al Gabinete", "callback_data": "gab:main"}]
        ])
    else:
        keyboard = _build_category_items_keyboard(items, category_slug, level, page)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


# =============================================================================
# DETALLE DE ITEM
# =============================================================================

@gabinete_router.callback_query(F.data.startswith("gab:item:"))
async def callback_gabinete_item_detail(callback: CallbackQuery, session: AsyncSession):
    """Callback para ver detalle de un item."""
    user_id = callback.from_user.id
    balance, level = await _get_user_data(session, user_id)

    item_id = int(callback.data.split(":")[2])

    gabinete_service = GabineteService(session)
    discount_service = DiscountService(session)

    item = await gabinete_service.get_item_by_id(item_id)
    if not item:
        await callback.answer("Item no encontrado", show_alert=True)
        return

    # Verificar acceso
    access = await gabinete_service.check_item_access(item, level)

    # Calcular precio con descuento
    discount = await discount_service.calculate_total_discount(user_id, level)
    final_price = discount_service.apply_discount(item.price_besitos, discount.total_discount)

    # Construir texto
    text = (
        f"{item.icon} <b>{item.name}</b>\n\n"
        f"<i>\"{item.lucien_description or item.description}\"</i>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
    )

    # Precio con/sin descuento
    if discount.total_discount > 0:
        text += f"Precio: <s>{item.price_besitos}</s> → <b>{final_price:.1f}</b> Favores\n"
        text += f"Descuento: {discount.total_discount:.0f}%\n"
    else:
        text += f"Precio: <b>{item.price_besitos}</b> Favor(es)\n"

    text += f"Sus Favores: <b>{balance:.1f}</b>\n"

    # Stock limitado
    if item.is_limited and item.stock is not None:
        text += f"⚠️ Disponibles: {item.stock_display}\n"

    # Tiempo limitado
    if item.available_until:
        from datetime import datetime, UTC
        remaining = item.available_until - datetime.now(UTC)
        if remaining.total_seconds() > 0:
            hours = int(remaining.total_seconds() // 3600)
            text += f"⏰ Termina en: {hours}h\n"

    text += f"━━━━━━━━━━━━━━━━━━━━━━━"

    # Botones
    buttons = []

    if not access.can_view:
        text += f"\n\n🔒 {access.reason}"
        buttons.append([{"text": "🔒 Bloqueado", "callback_data": "gab:noop"}])
    elif not access.can_buy:
        text += f"\n\n🔒 {access.reason}"
        buttons.append([{"text": "🔒 Requiere nivel superior", "callback_data": "gab:noop"}])
    else:
        # Verificar si ya tiene el item (para items de compra unica)
        can_buy_more, current_count = await gabinete_service.check_user_item_limit(
            user_id, item
        )

        if not can_buy_more:
            text += f"\n\n<i>Ya posee este articulo.</i>"
            buttons.append([{"text": "✓ Ya lo posee", "callback_data": "gab:noop"}])
        elif balance < final_price:
            missing = final_price - balance
            text += f"\n\n<i>Le faltan {missing:.1f} Favores.</i>"
            buttons.append([{"text": "💰 Favores insuficientes", "callback_data": "gab:noop"}])
        else:
            buttons.append([{"text": "✅ Adquirir", "callback_data": f"gab:confirm:{item_id}"}])

    # Volver
    category_slug = item.category.slug if item.category else "ephemeral"
    buttons.append([{"text": "🔙 Volver", "callback_data": f"gab:cat:{category_slug}"}])

    await callback.message.edit_text(
        text,
        reply_markup=create_inline_keyboard(buttons),
        parse_mode="HTML"
    )
    await callback.answer()


# =============================================================================
# FLUJO DE COMPRA
# =============================================================================

@gabinete_router.callback_query(F.data.startswith("gab:confirm:"))
async def callback_gabinete_confirm(callback: CallbackQuery, session: AsyncSession):
    """Paso 1: Confirmacion de compra."""
    user_id = callback.from_user.id
    balance, level = await _get_user_data(session, user_id)

    item_id = int(callback.data.split(":")[2])

    gabinete_service = GabineteService(session)
    discount_service = DiscountService(session)

    item = await gabinete_service.get_item_by_id(item_id)
    if not item:
        await callback.answer("Item no encontrado", show_alert=True)
        return

    discount = await discount_service.calculate_total_discount(user_id, level)
    final_price = discount_service.apply_discount(item.price_besitos, discount.total_discount)

    text = (
        f"<b>Confirmar adquisicion</b>\n\n"
        f"Item: {item.icon} <b>{item.name}</b>\n"
        f"Precio: <b>{final_price:.1f}</b> Favor(es)\n"
    )

    if discount.total_discount > 0:
        text += f"Descuento aplicado: {discount.total_discount:.0f}%\n"

    text += (
        f"\nDespues de esta transaccion:\n"
        f"Favores restantes: <b>{balance - final_price:.1f}</b>\n\n"
        f"<i>\"¿Confirma la adquisicion?\"</i>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=create_inline_keyboard([
            [{"text": "✅ Confirmar", "callback_data": f"gab:buy:{item_id}"}],
            [{"text": "❌ Cancelar", "callback_data": f"gab:item:{item_id}"}]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@gabinete_router.callback_query(F.data.startswith("gab:buy:"))
async def callback_gabinete_buy(callback: CallbackQuery, session: AsyncSession):
    """Paso 2: Ejecutar compra."""
    user_id = callback.from_user.id
    balance, level = await _get_user_data(session, user_id)

    item_id = int(callback.data.split(":")[2])

    gabinete_service = GabineteService(session)
    discount_service = DiscountService(session)

    # Calcular descuento
    discount = await discount_service.calculate_total_discount(user_id, level)

    # Intentar comprar
    result = await gabinete_service.purchase_item(
        user_id=user_id,
        item_id=item_id,
        user_level=level,
        user_balance=balance,
        discount_percent=discount.total_discount
    )

    if result.success:
        # Descontar favores del usuario
        try:
            from bot.gamification.database.models import UserGamification
            user_gamif = await session.get(UserGamification, user_id)
            if user_gamif:
                user_gamif.total_besitos -= result.price_paid
                user_gamif.besitos_spent += result.price_paid
                await session.commit()
        except Exception as e:
            logger.error(f"Error descontando favores: {e}")

        new_balance = balance - result.price_paid

        text = (
            f"<b>Transaccion completada</b>\n\n"
            f"{result.item.icon} <b>{result.item.name}</b> ha sido agregado a su inventario.\n\n"
            f"<i>\"{result.message}\"</i>\n\n"
            f"Favores restantes: <b>{new_balance:.1f}</b>"
        )

        buttons = [
            [{"text": "🎁 Usar ahora", "callback_data": f"gab:use:{result.inventory_item.id}"}],
            [{"text": "📦 Ver inventario", "callback_data": "gab:inventory"}],
            [{"text": "🔄 Seguir explorando", "callback_data": "gab:main"}]
        ]
    else:
        text = (
            f"<b>Transaccion fallida</b>\n\n"
            f"<i>\"{result.message}\"</i>"
        )
        buttons = [[{"text": "🔙 Volver", "callback_data": "gab:main"}]]

    await callback.message.edit_text(
        text,
        reply_markup=create_inline_keyboard(buttons),
        parse_mode="HTML"
    )
    await callback.answer()


@gabinete_router.callback_query(F.data == "gab:noop")
async def callback_gabinete_noop(callback: CallbackQuery):
    """Callback para botones deshabilitados."""
    await callback.answer()


# =============================================================================
# INVENTARIO
# =============================================================================

@gabinete_router.callback_query(F.data == "gab:inventory")
async def callback_gabinete_inventory(callback: CallbackQuery, session: AsyncSession):
    """Muestra el inventario del usuario."""
    user_id = callback.from_user.id

    gabinete_service = GabineteService(session)
    inventory = await gabinete_service.get_user_inventory(user_id)

    if not inventory:
        text = (
            "<b>📦 Su Inventario</b>\n\n"
            "<i>\"Su inventario esta vacio. Quizas deberia explorar el Gabinete.\"</i>"
        )
        buttons = [[{"text": "🔙 Volver al Gabinete", "callback_data": "gab:main"}]]
    else:
        text = "<b>📦 Su Inventario</b>\n\n"

        # Agrupar por tipo
        usable = []
        badges = []
        collectibles = []

        for inv_item in inventory:
            item = inv_item.item
            if inv_item.is_used:
                continue

            if item.gabinete_item_type in ['badge_perm', 'badge_temp']:
                badges.append(inv_item)
            elif item.gabinete_item_type in ['collectible', 'master_key']:
                collectibles.append(inv_item)
            else:
                usable.append(inv_item)

        if usable:
            text += "━━━ <b>Items Activos</b> ━━━\n"
            for inv_item in usable[:5]:
                text += f"{inv_item.item.icon} {inv_item.item.name}\n"

        if badges:
            text += "\n━━━ <b>Distintivos</b> ━━━\n"
            for inv_item in badges[:5]:
                text += f"{inv_item.item.icon} {inv_item.item.name}\n"

        if collectibles:
            text += "\n━━━ <b>Coleccionables</b> ━━━\n"
            for inv_item in collectibles[:5]:
                text += f"{inv_item.item.icon} {inv_item.item.name}\n"

        buttons = []
        if usable:
            buttons.append([{"text": "🎁 Ver items usables", "callback_data": "gab:inv:usable"}])
        buttons.append([{"text": "🔙 Volver al Gabinete", "callback_data": "gab:main"}])

    await callback.message.edit_text(
        text,
        reply_markup=create_inline_keyboard(buttons),
        parse_mode="HTML"
    )
    await callback.answer()


@gabinete_router.callback_query(F.data.startswith("gab:use:"))
async def callback_gabinete_use_item(callback: CallbackQuery, session: AsyncSession):
    """Usa un item del inventario."""
    user_id = callback.from_user.id
    inventory_item_id = int(callback.data.split(":")[2])

    gabinete_service = GabineteService(session)
    success, message, content = await gabinete_service.use_item(user_id, inventory_item_id)

    if success:
        text = (
            f"<b>Item utilizado</b>\n\n"
            f"<i>\"{message}\"</i>"
        )

        # Si hay contenido, mostrarlo
        if content:
            if content.get("content_text"):
                text += f"\n\n━━━━━━━━━━━━━━━━━━━━━━━\n{content['content_text']}"
    else:
        text = f"<b>Error</b>\n\n{message}"

    await callback.message.edit_text(
        text,
        reply_markup=create_inline_keyboard([
            [{"text": "📦 Ver inventario", "callback_data": "gab:inventory"}],
            [{"text": "🔙 Volver al Gabinete", "callback_data": "gab:main"}]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()
