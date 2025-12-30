"""
Handlers de usuario para el Gabinete (Tienda) con la voz de Lucien.

Permite a los usuarios:
- Ver catálogo de productos por categoría
- Ver detalles de productos
- Comprar productos con confirmación
"""

import logging
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from bot.shop.services.container import ShopContainer
from bot.shop.database.enums import ItemType, ItemRarity
from bot.utils.lucien_messages import Lucien
from bot.utils.keyboards import create_inline_keyboard

logger = logging.getLogger(__name__)

# Router para handlers de tienda de usuario
shop_user_router = Router(name="shop_user")

# Aplicar middleware de database
from bot.middlewares import DatabaseMiddleware
shop_user_router.message.middleware(DatabaseMiddleware())
shop_user_router.callback_query.middleware(DatabaseMiddleware())


# =============================================================================
# HELPERS
# =============================================================================

async def _get_user_favors(session: AsyncSession, user_id: int) -> int:
    """Obtiene los favores (besitos) del usuario."""
    try:
        from bot.gamification.database.models import UserGamification
        user_gamif = await session.get(UserGamification, user_id)
        return user_gamif.total_besitos if user_gamif else 0
    except Exception:
        return 0


def _build_cabinet_main_keyboard() -> InlineKeyboardMarkup:
    """Construye teclado principal del Gabinete con categorías de Lucien."""
    return create_inline_keyboard([
        [{"text": "Efímeros", "callback_data": "cabinet:cat:efimeros"}],
        [{"text": "Distintivos", "callback_data": "cabinet:cat:distintivos"}],
        [{"text": "Llaves", "callback_data": "cabinet:cat:llaves"}],
        [{"text": "Reliquias", "callback_data": "cabinet:cat:reliquias"}],
        [{"text": "Volver", "callback_data": "start:menu"}],
    ])


def _build_category_keyboard(
    items: list,
    category_slug: str,
    page: int = 0,
    items_per_page: int = 5
) -> InlineKeyboardMarkup:
    """Construye teclado de productos de una categoría."""
    buttons = []

    # Paginación
    start = page * items_per_page
    end = start + items_per_page
    page_items = items[start:end]

    for item in page_items:
        text = f"{item.icon} {item.name} — {item.price_besitos} Favor(es)"
        buttons.append([{
            "text": text,
            "callback_data": f"cabinet:item:{item.id}"
        }])

    # Navegación de páginas
    nav_buttons = []
    if page > 0:
        nav_buttons.append({
            "text": "Anterior",
            "callback_data": f"cabinet:cat:{category_slug}:{page-1}"
        })
    if end < len(items):
        nav_buttons.append({
            "text": "Siguiente",
            "callback_data": f"cabinet:cat:{category_slug}:{page+1}"
        })
    if nav_buttons:
        buttons.append(nav_buttons)

    # Volver
    buttons.append([{"text": "Volver al Gabinete", "callback_data": "cabinet:main"}])

    return create_inline_keyboard(buttons)


# =============================================================================
# HANDLER PRINCIPAL
# =============================================================================

@shop_user_router.message(Command("gabinete", "tienda", "shop", "store"))
async def cmd_cabinet(message: Message, session: AsyncSession):
    """Handler para /gabinete - Muestra el Gabinete principal."""
    user_id = message.from_user.id
    favors = await _get_user_favors(session, user_id)

    text = Lucien.CABINET_WELCOME.format(favors=favors)

    await message.answer(
        text,
        reply_markup=_build_cabinet_main_keyboard(),
        parse_mode="HTML"
    )


@shop_user_router.callback_query(F.data.in_({"cabinet:main", "cabinet:browse", "shop:main"}))
async def callback_cabinet_main(callback: CallbackQuery, session: AsyncSession):
    """Callback para mostrar/volver al Gabinete principal."""
    user_id = callback.from_user.id
    favors = await _get_user_favors(session, user_id)

    text = Lucien.CABINET_WELCOME.format(favors=favors)

    await callback.message.edit_text(
        text,
        reply_markup=_build_cabinet_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# =============================================================================
# CATEGORÍAS
# =============================================================================

CATEGORY_MESSAGES = {
    "efimeros": Lucien.CABINET_CATEGORY_EPHEMERAL,
    "distintivos": Lucien.CABINET_CATEGORY_DISTINCTIVE,
    "llaves": Lucien.CABINET_CATEGORY_KEYS,
    "reliquias": Lucien.CABINET_CATEGORY_RELICS,
}

CATEGORY_SLUGS = {
    "efimeros": "consumibles",
    "distintivos": "cosmeticos",
    "llaves": "artefactos-narrativos",
    "reliquias": "contenido-digital",
}


@shop_user_router.callback_query(F.data.startswith("cabinet:cat:"))
async def callback_cabinet_category(callback: CallbackQuery, session: AsyncSession):
    """Callback para ver productos de una categoría."""
    container = ShopContainer(session)
    user_id = callback.from_user.id
    favors = await _get_user_favors(session, user_id)

    parts = callback.data.split(":")
    lucien_category = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0

    # Mapear categoría de Lucien a slug real
    category_slug = CATEGORY_SLUGS.get(lucien_category, lucien_category)

    # Obtener categoría
    category = await container.shop.get_category_by_slug(category_slug)

    if not category:
        # Intentar buscar por el slug de Lucien directamente
        category = await container.shop.get_category_by_slug(lucien_category)

    if not category:
        await callback.answer("Esta sección está vacía por ahora.", show_alert=True)
        return

    # Obtener items
    items = await container.shop.get_items_by_category(category.id)

    if not items:
        text = (
            f"{CATEGORY_MESSAGES.get(lucien_category, 'Esta categoría.').format(favors=favors)}\n\n"
            "No hay artículos disponibles en esta sección."
        )
        await callback.message.edit_text(
            text,
            reply_markup=create_inline_keyboard([
                [{"text": "Volver al Gabinete", "callback_data": "cabinet:main"}]
            ]),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    # Mensaje de categoría
    category_msg = CATEGORY_MESSAGES.get(lucien_category, "")
    if category_msg:
        text = category_msg.format(favors=favors)
    else:
        text = f"Sus Favores: <b>{favors}</b>"

    await callback.message.edit_text(
        text,
        reply_markup=_build_category_keyboard(items, lucien_category, page),
        parse_mode="HTML"
    )
    await callback.answer()


# =============================================================================
# DETALLE DE ITEM
# =============================================================================

@shop_user_router.callback_query(F.data.startswith("cabinet:item:"))
async def callback_cabinet_item_detail(callback: CallbackQuery, session: AsyncSession):
    """Callback para ver detalle de un producto."""
    container = ShopContainer(session)
    user_id = callback.from_user.id
    favors = await _get_user_favors(session, user_id)

    item_id = int(callback.data.split(":")[2])
    item = await container.shop.get_item(item_id)

    if not item:
        await callback.answer("Artículo no encontrado", show_alert=True)
        return

    # Verificar si puede comprar
    can_buy, reason = await container.shop.can_purchase(user_id, item_id)

    # Construir texto del item
    text = (
        f"{item.icon} <b>{item.name}</b>\n\n"
        f'"{item.description}"\n\n'
        f"Costo: <b>{item.price_besitos}</b> Favor(es)\n"
        f"Sus Favores: <b>{favors}</b>"
    )

    if item.stock is not None:
        text += f"\nDisponibles: {item.stock}"

    # Verificar si ya lo tiene
    has_item = await container.inventory.has_item(user_id, item_id)
    if has_item:
        text += "\n\n<i>Ya posee este artículo.</i>"

    # Botones
    buttons = []
    if can_buy and not has_item:
        buttons.append([{"text": "Adquirir", "callback_data": f"cabinet:confirm:{item_id}"}])
    elif not can_buy:
        buttons.append([{"text": f"No disponible", "callback_data": "cabinet:cannot_buy"}])

    buttons.append([{"text": "Volver al Gabinete", "callback_data": "cabinet:main"}])

    await callback.message.edit_text(
        text,
        reply_markup=create_inline_keyboard(buttons),
        parse_mode="HTML"
    )
    await callback.answer()


# =============================================================================
# FLUJO DE COMPRA
# =============================================================================

@shop_user_router.callback_query(F.data.startswith("cabinet:confirm:"))
async def callback_cabinet_confirm_purchase(callback: CallbackQuery, session: AsyncSession):
    """Paso 1: Confirmación de compra."""
    container = ShopContainer(session)
    user_id = callback.from_user.id
    favors = await _get_user_favors(session, user_id)

    item_id = int(callback.data.split(":")[2])
    item = await container.shop.get_item(item_id)

    if not item:
        await callback.answer("Artículo no encontrado", show_alert=True)
        return

    remaining = favors - item.price_besitos

    text = Lucien.CABINET_CONFIRM_PURCHASE.format(
        item_name=item.name,
        price=item.price_besitos,
        total=favors,
        remaining=remaining,
        description=item.description
    )

    await callback.message.edit_text(
        text,
        reply_markup=create_inline_keyboard([
            [{"text": "Confirmar compra", "callback_data": f"cabinet:buy:{item_id}"}],
            [{"text": "Cancelar", "callback_data": f"cabinet:item:{item_id}"}]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@shop_user_router.callback_query(F.data.startswith("cabinet:buy:"))
async def callback_cabinet_buy(callback: CallbackQuery, session: AsyncSession):
    """Paso 2: Ejecutar compra."""
    container = ShopContainer(session)
    user_id = callback.from_user.id

    item_id = int(callback.data.split(":")[2])

    # Intentar comprar
    success, message, purchase = await container.shop.purchase_item(user_id, item_id)

    if success:
        item = await container.shop.get_item(item_id)
        new_favors = await _get_user_favors(session, user_id)

        text = Lucien.CABINET_PURCHASE_SUCCESS.format(
            item_name=item.name,
            new_total=new_favors
        )

        buttons = [
            [{"text": "Ver mi inventario", "callback_data": "backpack:main"}],
            [{"text": "Seguir explorando", "callback_data": "cabinet:main"}],
            [{"text": "Volver al menú", "callback_data": "start:menu"}]
        ]
    else:
        # Compra fallida
        item = await container.shop.get_item(item_id)
        favors = await _get_user_favors(session, user_id)

        if "besitos" in message.lower() or "insuficiente" in message.lower():
            missing = item.price_besitos - favors
            text = Lucien.CABINET_INSUFFICIENT_FUNDS.format(
                price=item.price_besitos,
                total=favors,
                missing=max(0, missing)
            )
            buttons = [
                [{"text": "Ver cómo ganar Favores", "callback_data": "missions:list"}],
                [{"text": "Volver al Gabinete", "callback_data": "cabinet:main"}]
            ]
        else:
            text = f"No se pudo completar la transacción.\n\n{message}"
            buttons = [[{"text": "Volver al Gabinete", "callback_data": "cabinet:main"}]]

    await callback.message.edit_text(
        text,
        reply_markup=create_inline_keyboard(buttons),
        parse_mode="HTML"
    )
    await callback.answer()


@shop_user_router.callback_query(F.data == "cabinet:cannot_buy")
async def callback_cannot_buy(callback: CallbackQuery):
    """Callback cuando no se puede comprar."""
    await callback.answer("No puede adquirir este artículo en este momento.", show_alert=True)


# =============================================================================
# COMPATIBILIDAD CON CALLBACKS ANTIGUOS
# =============================================================================

@shop_user_router.callback_query(F.data.startswith("shop:cat:"))
async def callback_shop_category_compat(callback: CallbackQuery, session: AsyncSession):
    """Compatibilidad con callbacks antiguos de tienda."""
    # Redirigir a cabinet:main
    await callback_cabinet_main(callback, session)


@shop_user_router.callback_query(F.data.startswith("shop:item:"))
async def callback_shop_item_compat(callback: CallbackQuery, session: AsyncSession):
    """Compatibilidad con callbacks antiguos de items."""
    item_id = callback.data.split(":")[2]
    callback.data = f"cabinet:item:{item_id}"
    await callback_cabinet_item_detail(callback, session)


@shop_user_router.callback_query(F.data.startswith("shop:buy:"))
async def callback_shop_buy_compat(callback: CallbackQuery, session: AsyncSession):
    """Compatibilidad con callbacks antiguos de compra."""
    item_id = callback.data.split(":")[2]
    callback.data = f"cabinet:buy:{item_id}"
    await callback_cabinet_buy(callback, session)
