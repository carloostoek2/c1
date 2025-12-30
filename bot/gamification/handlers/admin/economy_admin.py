"""
Handlers de Admin para Gestión de Economía de Favores.

Comandos disponibles:
- /admin_grant <user_id> <amount> <reason> - Otorgar Favores
- /admin_deduct <user_id> <amount> <reason> - Deducir Favores
- /admin_balance <user_id> - Ver balance de usuario
- /admin_economy_stats - Ver estadísticas globales de economía
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from config import Config
from bot.middlewares import DatabaseMiddleware, AdminAuthMiddleware
from bot.gamification.services.container import GamificationContainer
from bot.gamification.services.besito import BesitoService
from bot.gamification.database.models import UserGamification, BesitoTransaction, UserStreak
from bot.gamification.database.enums import TransactionType
from bot.database.models import User
from bot.utils.keyboards import create_inline_keyboard
from bot.gamification.utils.formatters import format_currency

logger = logging.getLogger(__name__)

# Router para admin de economía
economy_admin_router = Router(name="economy_admin")
economy_admin_router.message.middleware(DatabaseMiddleware())
economy_admin_router.message.middleware(AdminAuthMiddleware())
economy_admin_router.callback_query.middleware(DatabaseMiddleware())
economy_admin_router.callback_query.middleware(AdminAuthMiddleware())


class EconomyAdminStates(StatesGroup):
    """Estados para flujos de admin de economía."""
    waiting_grant_user_id = State()
    waiting_grant_amount = State()
    waiting_grant_reason = State()
    waiting_deduct_user_id = State()
    waiting_deduct_amount = State()
    waiting_deduct_reason = State()
    waiting_balance_user_id = State()


# ============================================================
# COMANDO: /admin_grant
# ============================================================

@economy_admin_router.message(Command("admin_grant"))
async def cmd_admin_grant(message: Message, session: AsyncSession, state: FSMContext):
    """Handler para /admin_grant - Otorgar Favores a un usuario.

    Uso: /admin_grant <user_id> <amount> <reason>
    Ejemplo: /admin_grant 123456789 10 Compensación por bug
    """
    admin_id = message.from_user.id
    args = message.text.split(maxsplit=3)

    # Si se proporcionan todos los argumentos
    if len(args) >= 4:
        try:
            user_id = int(args[1])
            amount = float(args[2])
            reason = args[3]

            await _process_grant(message, session, admin_id, user_id, amount, reason)
            return

        except ValueError:
            await message.answer(
                "Formato incorrecto.\n\n"
                "Uso: /admin_grant &lt;user_id&gt; &lt;amount&gt; &lt;reason&gt;\n"
                "Ejemplo: /admin_grant 123456789 10 Compensación por bug",
                parse_mode="HTML"
            )
            return

    # Si no hay argumentos, iniciar flujo interactivo
    await state.set_state(EconomyAdminStates.waiting_grant_user_id)
    await message.answer(
        "<b>Otorgar Favores</b>\n\n"
        "Envíe el ID del usuario al que desea otorgar Favores.\n\n"
        "Puede cancelar con /cancel",
        parse_mode="HTML"
    )


@economy_admin_router.message(EconomyAdminStates.waiting_grant_user_id)
async def process_grant_user_id(message: Message, session: AsyncSession, state: FSMContext):
    """Procesa ID de usuario para grant."""
    try:
        user_id = int(message.text.strip())

        # Verificar que el usuario existe
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await message.answer(
                f"Usuario con ID {user_id} no encontrado.\n"
                "Envíe un ID válido o /cancel para cancelar."
            )
            return

        await state.update_data(target_user_id=user_id, target_username=user.username)
        await state.set_state(EconomyAdminStates.waiting_grant_amount)
        await message.answer(
            f"Usuario: <b>{user.first_name}</b> (@{user.username or 'sin username'})\n\n"
            "Ahora envíe la cantidad de Favores a otorgar (puede ser decimal, ej: 5.5)",
            parse_mode="HTML"
        )

    except ValueError:
        await message.answer("ID inválido. Envíe un número entero o /cancel para cancelar.")


@economy_admin_router.message(EconomyAdminStates.waiting_grant_amount)
async def process_grant_amount(message: Message, state: FSMContext):
    """Procesa cantidad para grant."""
    try:
        amount = float(message.text.strip().replace(",", "."))

        if amount <= 0:
            await message.answer("La cantidad debe ser mayor a 0.")
            return

        await state.update_data(amount=amount)
        await state.set_state(EconomyAdminStates.waiting_grant_reason)
        await message.answer(
            f"Cantidad: <b>{format_currency(amount)}</b>\n\n"
            "Ahora envíe la razón de este otorgamiento.",
            parse_mode="HTML"
        )

    except ValueError:
        await message.answer("Cantidad inválida. Envíe un número o /cancel para cancelar.")


@economy_admin_router.message(EconomyAdminStates.waiting_grant_reason)
async def process_grant_reason(message: Message, session: AsyncSession, state: FSMContext):
    """Procesa razón y ejecuta grant."""
    reason = message.text.strip()

    if len(reason) < 3:
        await message.answer("La razón debe tener al menos 3 caracteres.")
        return

    data = await state.get_data()
    admin_id = message.from_user.id
    user_id = data["target_user_id"]
    amount = data["amount"]

    await _process_grant(message, session, admin_id, user_id, amount, reason)
    await state.clear()


async def _process_grant(
    message: Message,
    session: AsyncSession,
    admin_id: int,
    user_id: int,
    amount: float,
    reason: str
):
    """Procesa el otorgamiento de Favores."""
    try:
        besito_service = BesitoService(session)

        # Obtener balance actual
        old_balance = await besito_service.get_balance(user_id)

        # Otorgar
        description = f"[Admin {admin_id}] {reason}"
        await besito_service.grant_besitos(
            user_id=user_id,
            amount=amount,
            transaction_type=TransactionType.ADMIN_GRANT,
            description=description
        )

        # Obtener nuevo balance
        new_balance = await besito_service.get_balance(user_id)

        await message.answer(
            "<b>Favores otorgados</b>\n\n"
            f"Usuario: {user_id}\n"
            f"Cantidad: +{format_currency(amount)}\n"
            f"Razón: {reason}\n\n"
            f"Balance anterior: {format_currency(old_balance)}\n"
            f"Balance nuevo: <b>{format_currency(new_balance)}</b>",
            parse_mode="HTML"
        )

        logger.info(
            f"Admin {admin_id} granted {amount} Favores to user {user_id}. "
            f"Reason: {reason}. New balance: {new_balance}"
        )

    except Exception as e:
        logger.error(f"Error granting Favores: {e}", exc_info=True)
        await message.answer(
            "Error al otorgar Favores. Revise los logs.",
            parse_mode="HTML"
        )


# ============================================================
# COMANDO: /admin_deduct
# ============================================================

@economy_admin_router.message(Command("admin_deduct"))
async def cmd_admin_deduct(message: Message, session: AsyncSession, state: FSMContext):
    """Handler para /admin_deduct - Deducir Favores de un usuario.

    Uso: /admin_deduct <user_id> <amount> <reason>
    Ejemplo: /admin_deduct 123456789 5 Penalización por spam
    """
    admin_id = message.from_user.id
    args = message.text.split(maxsplit=3)

    # Si se proporcionan todos los argumentos
    if len(args) >= 4:
        try:
            user_id = int(args[1])
            amount = float(args[2])
            reason = args[3]

            await _process_deduct(message, session, admin_id, user_id, amount, reason)
            return

        except ValueError:
            await message.answer(
                "Formato incorrecto.\n\n"
                "Uso: /admin_deduct &lt;user_id&gt; &lt;amount&gt; &lt;reason&gt;\n"
                "Ejemplo: /admin_deduct 123456789 5 Penalización por spam",
                parse_mode="HTML"
            )
            return

    # Si no hay argumentos, iniciar flujo interactivo
    await state.set_state(EconomyAdminStates.waiting_deduct_user_id)
    await message.answer(
        "<b>Deducir Favores</b>\n\n"
        "Envíe el ID del usuario al que desea deducir Favores.\n\n"
        "Puede cancelar con /cancel",
        parse_mode="HTML"
    )


@economy_admin_router.message(EconomyAdminStates.waiting_deduct_user_id)
async def process_deduct_user_id(message: Message, session: AsyncSession, state: FSMContext):
    """Procesa ID de usuario para deduct."""
    try:
        user_id = int(message.text.strip())

        # Verificar que el usuario existe
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await message.answer(
                f"Usuario con ID {user_id} no encontrado.\n"
                "Envíe un ID válido o /cancel para cancelar."
            )
            return

        # Obtener balance actual
        besito_service = BesitoService(session)
        balance = await besito_service.get_balance(user_id)

        await state.update_data(
            target_user_id=user_id,
            target_username=user.username,
            current_balance=balance
        )
        await state.set_state(EconomyAdminStates.waiting_deduct_amount)
        await message.answer(
            f"Usuario: <b>{user.first_name}</b> (@{user.username or 'sin username'})\n"
            f"Balance actual: <b>{format_currency(balance)}</b>\n\n"
            "Ahora envíe la cantidad de Favores a deducir.",
            parse_mode="HTML"
        )

    except ValueError:
        await message.answer("ID inválido. Envíe un número entero o /cancel para cancelar.")


@economy_admin_router.message(EconomyAdminStates.waiting_deduct_amount)
async def process_deduct_amount(message: Message, state: FSMContext):
    """Procesa cantidad para deduct."""
    try:
        amount = float(message.text.strip().replace(",", "."))
        data = await state.get_data()
        current_balance = data.get("current_balance", 0)

        if amount <= 0:
            await message.answer("La cantidad debe ser mayor a 0.")
            return

        if amount > current_balance:
            await message.answer(
                f"El usuario solo tiene {format_currency(current_balance)}.\n"
                f"No puede deducir más de lo que tiene."
            )
            return

        await state.update_data(amount=amount)
        await state.set_state(EconomyAdminStates.waiting_deduct_reason)
        await message.answer(
            f"Cantidad: <b>{format_currency(amount)}</b>\n\n"
            "Ahora envíe la razón de esta deducción.",
            parse_mode="HTML"
        )

    except ValueError:
        await message.answer("Cantidad inválida. Envíe un número o /cancel para cancelar.")


@economy_admin_router.message(EconomyAdminStates.waiting_deduct_reason)
async def process_deduct_reason(message: Message, session: AsyncSession, state: FSMContext):
    """Procesa razón y ejecuta deduct."""
    reason = message.text.strip()

    if len(reason) < 3:
        await message.answer("La razón debe tener al menos 3 caracteres.")
        return

    data = await state.get_data()
    admin_id = message.from_user.id
    user_id = data["target_user_id"]
    amount = data["amount"]

    await _process_deduct(message, session, admin_id, user_id, amount, reason)
    await state.clear()


async def _process_deduct(
    message: Message,
    session: AsyncSession,
    admin_id: int,
    user_id: int,
    amount: float,
    reason: str
):
    """Procesa la deducción de Favores."""
    try:
        besito_service = BesitoService(session)

        # Obtener balance actual
        old_balance = await besito_service.get_balance(user_id)

        # Deducir
        description = f"[Admin {admin_id}] {reason}"
        success, msg, new_balance = await besito_service.deduct_besitos(
            user_id=user_id,
            amount=amount,
            transaction_type=TransactionType.ADMIN_DEDUCT,
            description=description
        )

        if success:
            await message.answer(
                "<b>Favores deducidos</b>\n\n"
                f"Usuario: {user_id}\n"
                f"Cantidad: -{format_currency(amount)}\n"
                f"Razón: {reason}\n\n"
                f"Balance anterior: {format_currency(old_balance)}\n"
                f"Balance nuevo: <b>{format_currency(new_balance)}</b>",
                parse_mode="HTML"
            )

            logger.info(
                f"Admin {admin_id} deducted {amount} Favores from user {user_id}. "
                f"Reason: {reason}. New balance: {new_balance}"
            )
        else:
            await message.answer(
                f"No se pudieron deducir los Favores.\n\n"
                f"Razón: {msg}",
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"Error deducting Favores: {e}", exc_info=True)
        await message.answer(
            "Error al deducir Favores. Revise los logs.",
            parse_mode="HTML"
        )


# ============================================================
# COMANDO: /admin_balance
# ============================================================

@economy_admin_router.message(Command("admin_balance"))
async def cmd_admin_balance(message: Message, session: AsyncSession, state: FSMContext):
    """Handler para /admin_balance - Ver balance de un usuario.

    Uso: /admin_balance <user_id>
    Ejemplo: /admin_balance 123456789
    """
    args = message.text.split()

    # Si se proporciona el user_id
    if len(args) >= 2:
        try:
            user_id = int(args[1])
            await _show_user_balance(message, session, user_id)
            return
        except ValueError:
            await message.answer(
                "ID inválido.\n\n"
                "Uso: /admin_balance &lt;user_id&gt;",
                parse_mode="HTML"
            )
            return

    # Si no hay argumentos, solicitar ID
    await state.set_state(EconomyAdminStates.waiting_balance_user_id)
    await message.answer(
        "<b>Consultar Balance</b>\n\n"
        "Envíe el ID del usuario cuyo balance desea consultar.\n\n"
        "Puede cancelar con /cancel",
        parse_mode="HTML"
    )


@economy_admin_router.message(EconomyAdminStates.waiting_balance_user_id)
async def process_balance_user_id(message: Message, session: AsyncSession, state: FSMContext):
    """Procesa ID de usuario para consulta de balance."""
    try:
        user_id = int(message.text.strip())
        await _show_user_balance(message, session, user_id)
        await state.clear()

    except ValueError:
        await message.answer("ID inválido. Envíe un número entero o /cancel para cancelar.")


async def _show_user_balance(message: Message, session: AsyncSession, user_id: int):
    """Muestra el balance completo de un usuario."""
    try:
        # Obtener usuario
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            await message.answer(f"Usuario con ID {user_id} no encontrado.")
            return

        container = GamificationContainer(session, message.bot)

        # Obtener perfil de gamificación
        profile = await container.user_gamification.get_user_profile(user_id)

        # Obtener racha
        result = await session.execute(
            select(UserStreak).where(UserStreak.user_id == user_id)
        )
        streak = result.scalar_one_or_none()

        # Obtener últimas transacciones
        besito_service = BesitoService(session)
        transactions = await besito_service.get_transaction_history(user_id, limit=5)

        # Construir mensaje
        text_parts = [
            f"<b>Balance de Usuario</b>",
            "",
            f"ID: {user_id}",
            f"Username: @{user.username or 'N/A'}",
            f"Nombre: {user.first_name}",
            f"Rol: {user.role}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "<b>ECONOMÍA</b>",
            "",
            f"Balance: <b>{format_currency(profile['besitos']['total'])}</b>",
            f"Total ganado: {format_currency(profile['besitos']['earned'])}",
            f"Total gastado: {format_currency(profile['besitos']['spent'])}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "<b>NIVEL Y RACHA</b>",
            "",
            f"Nivel: {profile['level']['current'].name if profile['level']['current'] else 'Sin nivel'}",
        ]

        if streak:
            text_parts.append(f"Racha actual: {streak.current_streak} días")
            text_parts.append(f"Racha máxima: {streak.longest_streak} días")
        else:
            text_parts.append("Racha: Sin datos")

        # Últimas transacciones
        if transactions:
            text_parts.extend([
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━",
                "<b>ÚLTIMAS TRANSACCIONES</b>",
                ""
            ])

            for tx in transactions:
                sign = "+" if tx.amount > 0 else ""
                date_str = tx.created_at.strftime("%d/%m %H:%M")
                desc = tx.description[:25] + "..." if len(tx.description) > 25 else tx.description
                text_parts.append(f"• {date_str}: {sign}{tx.amount} - {desc}")

        text = "\n".join(text_parts)

        await message.answer(text, parse_mode="HTML")

        logger.info(f"Admin viewed balance for user {user_id}")

    except Exception as e:
        logger.error(f"Error showing balance: {e}", exc_info=True)
        await message.answer("Error al consultar balance. Revise los logs.")


# ============================================================
# COMANDO: /admin_economy_stats
# ============================================================

@economy_admin_router.message(Command("admin_economy_stats"))
async def cmd_admin_economy_stats(message: Message, session: AsyncSession):
    """Handler para /admin_economy_stats - Estadísticas globales de economía."""
    try:
        # Total de Favores en circulación
        result = await session.execute(
            select(func.coalesce(func.sum(UserGamification.total_besitos), 0))
        )
        total_in_circulation = result.scalar() or 0

        # Total de usuarios con Favores
        result = await session.execute(
            select(func.count()).select_from(UserGamification).where(
                UserGamification.total_besitos > 0
            )
        )
        users_with_favors = result.scalar() or 0

        # Promedio por usuario
        result = await session.execute(
            select(func.avg(UserGamification.total_besitos))
        )
        avg_per_user = result.scalar() or 0

        # Favores otorgados hoy
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        result = await session.execute(
            select(func.coalesce(func.sum(BesitoTransaction.amount), 0)).where(
                BesitoTransaction.amount > 0,
                BesitoTransaction.created_at >= today_start
            )
        )
        earned_today = result.scalar() or 0

        # Favores gastados hoy
        result = await session.execute(
            select(func.coalesce(func.sum(BesitoTransaction.amount), 0)).where(
                BesitoTransaction.amount < 0,
                BesitoTransaction.created_at >= today_start
            )
        )
        spent_today = abs(result.scalar() or 0)

        # Favores esta semana
        week_start = today_start - timedelta(days=today_start.weekday())
        result = await session.execute(
            select(func.coalesce(func.sum(BesitoTransaction.amount), 0)).where(
                BesitoTransaction.amount > 0,
                BesitoTransaction.created_at >= week_start
            )
        )
        earned_week = result.scalar() or 0

        result = await session.execute(
            select(func.coalesce(func.sum(BesitoTransaction.amount), 0)).where(
                BesitoTransaction.amount < 0,
                BesitoTransaction.created_at >= week_start
            )
        )
        spent_week = abs(result.scalar() or 0)

        # Total de transacciones
        result = await session.execute(
            select(func.count()).select_from(BesitoTransaction)
        )
        total_transactions = result.scalar() or 0

        # Top 5 usuarios por balance
        result = await session.execute(
            select(UserGamification).order_by(
                UserGamification.total_besitos.desc()
            ).limit(5)
        )
        top_users = result.scalars().all()

        # Construir mensaje
        text_parts = [
            "<b>Estadísticas Globales de Economía</b>",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "<b>CIRCULACIÓN</b>",
            "",
            f"Total en circulación: <b>{format_currency(total_in_circulation)}</b>",
            f"Usuarios con Favores: {users_with_favors}",
            f"Promedio por usuario: {format_currency(avg_per_user)}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "<b>ACTIVIDAD HOY</b>",
            "",
            f"Otorgados: +{format_currency(earned_today)}",
            f"Gastados: -{format_currency(spent_today)}",
            f"Neto: {format_currency(earned_today - spent_today)}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "<b>ACTIVIDAD SEMANA</b>",
            "",
            f"Otorgados: +{format_currency(earned_week)}",
            f"Gastados: -{format_currency(spent_week)}",
            f"Neto: {format_currency(earned_week - spent_week)}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "<b>TOTALES</b>",
            "",
            f"Total transacciones: {total_transactions}",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "<b>TOP 5 USUARIOS</b>",
            ""
        ]

        for i, ug in enumerate(top_users, 1):
            text_parts.append(f"{i}. User {ug.user_id}: {format_currency(ug.total_besitos)}")

        text = "\n".join(text_parts)

        await message.answer(text, parse_mode="HTML")

        logger.info(f"Admin {message.from_user.id} viewed economy stats")

    except Exception as e:
        logger.error(f"Error showing economy stats: {e}", exc_info=True)
        await message.answer("Error al obtener estadísticas. Revise los logs.")


# ============================================================
# COMANDO: /cancel (para cancelar flujos FSM)
# ============================================================

@economy_admin_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Cancela cualquier flujo activo."""
    current_state = await state.get_state()

    if current_state is None:
        await message.answer("No hay ninguna operación en curso.")
        return

    await state.clear()
    await message.answer("Operación cancelada.")
