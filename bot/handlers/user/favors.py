"""
Handler de Favores - Sistema de balance y estadísticas.

Maneja:
- Visualización del balance de Favores
- Actividad reciente (hoy, semana, mes)
- Próximos hitos de nivel
- Historial de transacciones
- Información sobre cómo ganar Favores
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares import DatabaseMiddleware
from bot.gamification.services.container import GamificationContainer
from bot.gamification.database.models import BesitoTransaction, Level
from bot.gamification.utils.formatters import format_currency
from bot.utils.lucien_messages import Lucien
from bot.utils.keyboards import create_inline_keyboard

logger = logging.getLogger(__name__)

# Router para favores
favors_router = Router(name="favors")
favors_router.message.middleware(DatabaseMiddleware())
favors_router.callback_query.middleware(DatabaseMiddleware())


def _get_favor_comment(total: int) -> str:
    """Obtiene comentario de Lucien según cantidad de Favores.

    Args:
        total: Total de Favores acumulados

    Returns:
        Comentario apropiado según el rango
    """
    if total <= 5:
        return Lucien.FAVORS_COMMENT_0_5
    elif total <= 15:
        return Lucien.FAVORS_COMMENT_6_15
    elif total <= 35:
        return Lucien.FAVORS_COMMENT_16_35
    elif total <= 70:
        return Lucien.FAVORS_COMMENT_36_70
    elif total <= 120:
        return Lucien.FAVORS_COMMENT_71_120
    elif total <= 200:
        return Lucien.FAVORS_COMMENT_121_200
    else:
        return Lucien.FAVORS_COMMENT_200_PLUS


async def _get_period_stats(
    session: AsyncSession,
    user_id: int,
    start_date: datetime
) -> tuple[float, float]:
    """Obtiene estadísticas de período (ganado/gastado).

    Args:
        session: Sesión de BD
        user_id: ID del usuario
        start_date: Fecha de inicio del período

    Returns:
        Tuple (earned, spent) para el período
    """
    # Ganado en el período
    stmt_earned = select(
        func.coalesce(func.sum(BesitoTransaction.amount), 0)
    ).where(
        BesitoTransaction.user_id == user_id,
        BesitoTransaction.amount > 0,
        BesitoTransaction.created_at >= start_date
    )
    result = await session.execute(stmt_earned)
    earned = float(result.scalar() or 0)

    # Gastado en el período (valor absoluto)
    stmt_spent = select(
        func.coalesce(func.sum(BesitoTransaction.amount), 0)
    ).where(
        BesitoTransaction.user_id == user_id,
        BesitoTransaction.amount < 0,
        BesitoTransaction.created_at >= start_date
    )
    result = await session.execute(stmt_spent)
    spent = abs(float(result.scalar() or 0))

    return earned, spent


def _build_favors_keyboard(show_back: bool = True) -> list:
    """Construye keyboard para menú de Favores.

    Args:
        show_back: Si mostrar botón de volver

    Returns:
        InlineKeyboardMarkup
    """
    buttons = [
        [{"text": "📜 Ver historial", "callback_data": "favors:history"}],
        [{"text": "💡 Cómo ganar Favores", "callback_data": "favors:how_to_earn"}],
    ]

    if show_back:
        buttons.append([{"text": "🔙 Volver", "callback_data": "dynmenu:back"}])

    return create_inline_keyboard(buttons)


@favors_router.message(Command("favores"))
async def cmd_favors(message: Message, session: AsyncSession):
    """Handler para comando /favores.

    Muestra el balance completo de Favores con la voz de Lucien.
    """
    user_id = message.from_user.id

    try:
        container = GamificationContainer(session, message.bot)

        # Obtener perfil del usuario
        profile = await container.user_gamification.get_user_profile(user_id)

        # Datos de Favores
        total = profile['besitos']['total']
        comment = _get_favor_comment(total)

        # Obtener estadísticas de actividad
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)

        today_earned, today_spent = await _get_period_stats(session, user_id, today_start)
        week_earned, week_spent = await _get_period_stats(session, user_id, week_start)
        month_earned, month_spent = await _get_period_stats(session, user_id, month_start)

        # Información de nivel
        level_info = profile['level']
        next_level = level_info.get('next')
        besitos_to_next = level_info.get('besitos_to_next')

        # Construir mensaje
        text_parts = [
            Lucien.FAVORS_MENU_HEADER,
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            f"💫 {Lucien.format('FAVORS_BALANCE_SECTION', total=total, comment=comment)}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📊 {Lucien.format('FAVORS_ACTIVITY_SECTION', today_earned=today_earned, today_spent=today_spent, week_earned=week_earned, week_spent=week_spent, month_earned=month_earned, month_spent=month_spent)}",
        ]

        # Agregar sección de hitos si hay siguiente nivel
        if next_level and besitos_to_next:
            text_parts.extend([
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━",
                f"📈 {Lucien.format('FAVORS_MILESTONES_SECTION', next_level_name=next_level.name, favors_needed=besitos_to_next)}",
            ])

        text = "\n".join(text_parts)

        await message.answer(
            text=text,
            reply_markup=_build_favors_keyboard(),
            parse_mode="HTML"
        )

        logger.info(f"User {user_id} viewed favors balance: {total}")

    except Exception as e:
        logger.error(f"Error showing favors for user {user_id}: {e}", exc_info=True)
        await message.answer(
            Lucien.ERROR_GENERIC,
            parse_mode="HTML"
        )


@favors_router.callback_query(F.data == "start:favors")
async def callback_favors_menu(callback: CallbackQuery, session: AsyncSession):
    """Handler para callback de botón "Mis Favores".

    Muestra el balance de Favores editando el mensaje actual.
    """
    user_id = callback.from_user.id

    try:
        container = GamificationContainer(session, callback.bot)

        # Obtener perfil del usuario
        profile = await container.user_gamification.get_user_profile(user_id)

        # Datos de Favores
        total = profile['besitos']['total']
        comment = _get_favor_comment(total)

        # Obtener estadísticas de actividad
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)

        today_earned, today_spent = await _get_period_stats(session, user_id, today_start)
        week_earned, week_spent = await _get_period_stats(session, user_id, week_start)
        month_earned, month_spent = await _get_period_stats(session, user_id, month_start)

        # Información de nivel
        level_info = profile['level']
        next_level = level_info.get('next')
        besitos_to_next = level_info.get('besitos_to_next')

        # Construir mensaje
        text_parts = [
            Lucien.FAVORS_MENU_HEADER,
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            f"💫 {Lucien.format('FAVORS_BALANCE_SECTION', total=total, comment=comment)}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📊 {Lucien.format('FAVORS_ACTIVITY_SECTION', today_earned=today_earned, today_spent=today_spent, week_earned=week_earned, week_spent=week_spent, month_earned=month_earned, month_spent=month_spent)}",
        ]

        # Agregar sección de hitos si hay siguiente nivel
        if next_level and besitos_to_next:
            text_parts.extend([
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━",
                f"📈 {Lucien.format('FAVORS_MILESTONES_SECTION', next_level_name=next_level.name, favors_needed=besitos_to_next)}",
            ])

        text = "\n".join(text_parts)

        await callback.message.edit_text(
            text=text,
            reply_markup=_build_favors_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()

        logger.info(f"User {user_id} viewed favors menu: {total}")

    except Exception as e:
        logger.error(f"Error showing favors menu for user {user_id}: {e}", exc_info=True)
        await callback.answer(Lucien.ERROR_GENERIC[:200], show_alert=True)


@favors_router.callback_query(F.data == "favors:history")
async def callback_favors_history(callback: CallbackQuery, session: AsyncSession):
    """Handler para ver historial de Favores."""
    user_id = callback.from_user.id

    try:
        container = GamificationContainer(session, callback.bot)

        # Obtener historial reciente
        history = await container.besito.get_transaction_history(user_id, limit=10)

        if not history:
            text = Lucien.FAVORS_HISTORY_EMPTY
        else:
            text_parts = [Lucien.FAVORS_HISTORY_HEADER, ""]

            for tx in history:
                # Formatear cada transacción
                sign = "+" if tx.amount > 0 else ""
                date_str = tx.created_at.strftime("%d/%m %H:%M")
                amount_str = f"{sign}{tx.amount}"

                # Descripción corta
                desc = tx.description[:30] + "..." if len(tx.description) > 30 else tx.description

                text_parts.append(f"• {date_str}: <b>{amount_str}</b> - {desc}")

            text = "\n".join(text_parts)

        keyboard = create_inline_keyboard([
            [{"text": "🔙 Volver a Favores", "callback_data": "start:favors"}]
        ])

        await callback.message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error showing history for user {user_id}: {e}", exc_info=True)
        await callback.answer(Lucien.ERROR_GENERIC[:200], show_alert=True)


@favors_router.callback_query(F.data == "favors:how_to_earn")
async def callback_how_to_earn(callback: CallbackQuery, session: AsyncSession):
    """Handler para mostrar cómo ganar Favores."""
    try:
        keyboard = create_inline_keyboard([
            [{"text": "🔙 Volver a Favores", "callback_data": "start:favors"}]
        ])

        await callback.message.edit_text(
            text=Lucien.FAVORS_HOW_TO_EARN,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error showing how to earn: {e}", exc_info=True)
        await callback.answer(Lucien.ERROR_GENERIC[:200], show_alert=True)


# ============================================================
# FUNCIONES DE NOTIFICACIÓN
# ============================================================

def get_favor_notification(amount: float, new_total: int) -> str:
    """Genera notificación apropiada al ganar Favores.

    Args:
        amount: Cantidad ganada
        new_total: Nuevo total

    Returns:
        Mensaje de notificación apropiado
    """
    # Ganancia pequeña (0.1-0.5)
    if amount < 1:
        return Lucien.format("FAVOR_NOTIFICATION_SMALL", amount=format_currency(amount))

    # Ganancia media (1-3)
    elif amount < 5:
        return Lucien.format(
            "FAVOR_NOTIFICATION_MEDIUM",
            amount=format_currency(amount),
            new_total=new_total
        )

    # Ganancia alta (5+)
    else:
        return Lucien.format(
            "FAVOR_NOTIFICATION_HIGH",
            amount=format_currency(amount),
            new_total=new_total
        )


def get_milestone_notification(total: int, percentile: Optional[int] = None) -> str:
    """Genera notificación de hito alcanzado.

    Args:
        total: Total de Favores alcanzado
        percentile: Percentil del usuario (opcional)

    Returns:
        Mensaje de notificación de hito
    """
    return Lucien.format(
        "FAVOR_NOTIFICATION_MILESTONE",
        total=total,
        percentile=percentile or 10
    )


def is_milestone(total: int) -> bool:
    """Determina si un total es un hito.

    Hitos: 10, 25, 50, 100, 150, 200, 250, etc.

    Args:
        total: Total de Favores

    Returns:
        True si es un hito
    """
    milestones = {10, 25, 50, 100, 150, 200, 250, 300, 400, 500}
    return total in milestones
