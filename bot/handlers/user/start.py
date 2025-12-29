"""
User Start Handler - Punto de entrada con la voz de Lucien.

Handler del comando /start que implementa flujos diferenciados según
el estado del usuario:
- Flujo A: Usuario completamente nuevo
- Flujo B: Usuario que regresa (< 7 días)
- Flujo C: Usuario que regresa (7-14 días)
- Flujo D: Usuario que regresa (> 14 días)
- Flujo E: Usuario VIP

Deep Link Format: t.me/botname?start=TOKEN
"""
import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.enums import UserRole
from bot.middlewares import DatabaseMiddleware
from bot.services.container import ServiceContainer
from bot.utils.keyboards import create_inline_keyboard
from bot.utils.lucien_messages import Lucien
from config import Config

logger = logging.getLogger(__name__)

# Router para handlers de usuario
user_router = Router(name="user")

# Aplicar middleware de database
user_router.message.middleware(DatabaseMiddleware())
user_router.callback_query.middleware(DatabaseMiddleware())


# =============================================================================
# KEYBOARDS DE LUCIEN
# =============================================================================

def lucien_new_user_keyboard() -> dict:
    """Keyboard para usuario nuevo (primer mensaje)."""
    return create_inline_keyboard([
        [
            {"text": "Entendido, continuar", "callback_data": "start:continue"},
            {"text": "¿Quién es Diana?", "callback_data": "start:who_diana"}
        ]
    ])


def lucien_continue_keyboard() -> dict:
    """Keyboard después de explicar quién es Diana."""
    return create_inline_keyboard([
        [{"text": "Continuar", "callback_data": "start:continue"}]
    ])


def lucien_main_menu_keyboard(is_vip: bool = False) -> dict:
    """Keyboard del menú principal de Lucien."""
    buttons = [
        [{"text": "La Historia", "callback_data": "menu:historia"}],
        [{"text": "Mi Perfil", "callback_data": "start:profile"}],
        [{"text": "El Gabinete", "callback_data": "menu:gabinete"}],
        [{"text": "Mis Encargos", "callback_data": "menu:encargos"}],
    ]

    if is_vip:
        buttons.append([{"text": "Contenido Nuevo", "callback_data": "menu:nuevo"}])

    return create_inline_keyboard(buttons)


def lucien_returning_long_keyboard() -> dict:
    """Keyboard para usuario ausente > 14 días."""
    return create_inline_keyboard([
        [{"text": "Ver qué hay de nuevo", "callback_data": "menu:nuevo"}],
        [{"text": "Ir al menú principal", "callback_data": "start:menu"}]
    ])


# =============================================================================
# HELPERS
# =============================================================================

async def _get_user_context(session: AsyncSession, user_id: int, bot) -> dict:
    """
    Obtiene el contexto completo del usuario para determinar el flujo.

    Returns:
        Dict con: user, is_new, is_vip, days_away, level_name, favors, vip_days, archetype
    """
    container = ServiceContainer(session, bot)

    # Obtener o crear usuario
    user = await container.user.get_user(user_id)
    is_new = user is None or user.is_new_user if user else True

    if not user:
        return {
            "user": None,
            "is_new": True,
            "is_vip": False,
            "days_away": 0,
            "level_name": "Visitante",
            "favors": 0,
            "vip_days": 0,
            "archetype": None,
            "streak_status": ""
        }

    # Verificar VIP
    is_vip = await container.subscription.is_vip_active(user_id)

    # Calcular días de ausencia
    days_away = user.days_since_last_activity

    # Obtener datos de gamificación
    level_name = "Visitante"
    favors = 0
    archetype = None
    streak_status = ""

    try:
        from bot.gamification.services.container import GamificationContainer
        gamification = GamificationContainer(session, bot)

        # Obtener nivel
        user_gam = await gamification.user_gamification.get_or_create_profile(user_id)
        if user_gam and user_gam.current_level:
            level_name = user_gam.current_level.name

        # Obtener favores (besitos)
        besitos_balance = await gamification.besitos.get_balance(user_id)
        favors = besitos_balance or 0

        # Obtener arquetipo
        archetype = user_gam.archetype if user_gam else None

        # Obtener estado de racha
        streak = await gamification.daily_gift.get_streak_info(user_id)
        if streak and streak.get("current_streak", 0) > 0:
            streak_status = f"Racha activa: {streak['current_streak']} días"
        else:
            streak_status = "Sin racha activa"

    except Exception as e:
        logger.warning(f"⚠️ Error obteniendo datos de gamificación: {e}")

    # Calcular días VIP
    vip_days = 0
    if is_vip:
        subscriber = await container.subscription.get_vip_subscriber(user_id)
        if subscriber and subscriber.join_date:
            join = subscriber.join_date
            if join.tzinfo is None:
                join = join.replace(tzinfo=timezone.utc)
            vip_days = (datetime.now(timezone.utc) - join).days

    return {
        "user": user,
        "is_new": is_new,
        "is_vip": is_vip,
        "days_away": days_away,
        "level_name": level_name,
        "favors": favors,
        "vip_days": vip_days,
        "archetype": archetype,
        "streak_status": streak_status
    }


async def _determine_flow(context: dict) -> str:
    """
    Determina qué flujo usar según el contexto del usuario.

    Returns:
        String: "new", "returning_short", "returning_medium", "returning_long", "vip"
    """
    if context["is_new"]:
        return "new"

    if context["is_vip"]:
        return "vip"

    days = context["days_away"]

    if days < 7:
        return "returning_short"
    elif days < 14:
        return "returning_medium"
    else:
        return "returning_long"


# =============================================================================
# HANDLER PRINCIPAL /start
# =============================================================================

@user_router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    """
    Handler del comando /start para usuarios.

    Flujos:
    - A: Usuario nuevo → Presentación de Lucien
    - B: Regresa < 7 días → Bienvenida corta
    - C: Regresa 7-14 días → Bienvenida media con drama
    - D: Regresa > 14 días → Bienvenida dramática
    - E: VIP → Bienvenida especial

    Deep Link: /start TOKEN → Activa token automáticamente
    """
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Usuario"

    logger.info(f"👋 Usuario {user_id} ({user_name}) ejecutó /start")

    container = ServiceContainer(session, message.bot)

    # Crear/obtener usuario
    user = await container.user.get_or_create_user(
        telegram_user=message.from_user,
        default_role=UserRole.FREE
    )

    # Verificar si es admin
    if Config.is_admin(user_id):
        await message.answer(
            "Bienvenido de nuevo.\n\n"
            "Como administrador, tiene acceso a funciones especiales. "
            "Use /admin para gestionar el sistema.",
            parse_mode="HTML"
        )
        return

    # Verificar deep link
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        token_string = args[1].strip()
        logger.info(f"🔗 Deep link detectado: Token={token_string}")
        await _activate_token_from_deeplink(message, session, container, user, token_string)
        return

    # Obtener contexto y determinar flujo
    context = await _get_user_context(session, user_id, message.bot)
    flow = await _determine_flow(context)

    logger.debug(f"📊 Flujo determinado: {flow} | days_away={context['days_away']}")

    # Ejecutar flujo correspondiente
    if flow == "new":
        await _flow_new_user(message, session, user)
    elif flow == "returning_short":
        await _flow_returning_short(message, context)
    elif flow == "returning_medium":
        await _flow_returning_medium(message, context)
    elif flow == "returning_long":
        await _flow_returning_long(message, context)
    elif flow == "vip":
        await _flow_vip(message, context)

    # Actualizar última actividad
    user.update_activity()
    await session.commit()


# =============================================================================
# FLUJOS DE BIENVENIDA
# =============================================================================

async def _flow_new_user(message: Message, session: AsyncSession, user):
    """Flujo A: Usuario completamente nuevo."""

    # Mensaje 1: Presentación de Lucien
    await message.answer(
        Lucien.START_NEW_USER_1,
        parse_mode="HTML"
    )

    # Delay dramático
    await asyncio.sleep(2)

    # Mensaje 2: Advertencia de observación
    await message.answer(
        Lucien.START_NEW_USER_2,
        reply_markup=lucien_new_user_keyboard(),
        parse_mode="HTML"
    )


async def _flow_returning_short(message: Message, context: dict):
    """Flujo B: Usuario que regresa (< 7 días)."""
    days = context["days_away"]
    if days == 0:
        days_text = "Hace unas horas"
    elif days == 1:
        days_text = "1 día"
    else:
        days_text = f"{days} días"

    text = Lucien.START_RETURNING_SHORT.format(
        days_away=days_text,
        level_name=context["level_name"],
        favors=context["favors"]
    )

    await message.answer(
        text,
        reply_markup=lucien_main_menu_keyboard(context["is_vip"]),
        parse_mode="HTML"
    )


async def _flow_returning_medium(message: Message, context: dict):
    """Flujo C: Usuario que regresa (7-14 días)."""

    # Mensaje 1: Drama
    await message.answer(
        Lucien.START_RETURNING_MEDIUM,
        parse_mode="HTML"
    )

    await asyncio.sleep(2)

    # Mensaje 2: Status
    text = Lucien.START_RETURNING_MEDIUM_STATUS.format(
        level_name=context["level_name"],
        favors=context["favors"],
        streak_status=context["streak_status"]
    )

    await message.answer(
        text,
        reply_markup=lucien_main_menu_keyboard(context["is_vip"]),
        parse_mode="HTML"
    )


async def _flow_returning_long(message: Message, context: dict):
    """Flujo D: Usuario que regresa (> 14 días)."""

    # Mensaje 1: Drama intenso
    text = Lucien.START_RETURNING_LONG.format(
        days_away=context["days_away"]
    )

    await message.answer(text, parse_mode="HTML")

    await asyncio.sleep(2)

    # Mensaje 2: Oferta de regreso
    await message.answer(
        Lucien.START_RETURNING_LONG_2,
        reply_markup=lucien_returning_long_keyboard(),
        parse_mode="HTML"
    )


async def _flow_vip(message: Message, context: dict):
    """Flujo E: Usuario VIP."""
    archetype_title = "estimado miembro"
    if context["archetype"]:
        # Mapear arquetipo a título
        archetype_titles = {
            "explorer": "Explorador",
            "direct": "miembro Directo",
            "romantic": "Romántico",
            "analytical": "Analítico",
            "persistent": "Persistente",
            "patient": "Paciente",
        }
        archetype_val = context["archetype"]
        if hasattr(archetype_val, 'value'):
            archetype_val = archetype_val.value
        archetype_title = archetype_titles.get(archetype_val, "estimado miembro")

    text = Lucien.START_VIP.format(
        archetype_title=archetype_title,
        level_name=context["level_name"],
        favors=context["favors"],
        vip_days=context["vip_days"]
    )

    await message.answer(
        text,
        reply_markup=lucien_main_menu_keyboard(is_vip=True),
        parse_mode="HTML"
    )


# =============================================================================
# CALLBACKS DEL ONBOARDING
# =============================================================================

@user_router.callback_query(F.data == "start:who_diana")
async def callback_who_is_diana(callback: CallbackQuery, session: AsyncSession):
    """Responde a la pregunta ¿Quién es Diana?"""
    await callback.message.edit_text(
        Lucien.START_WHO_IS_DIANA,
        reply_markup=lucien_continue_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@user_router.callback_query(F.data == "start:continue")
async def callback_continue_onboarding(callback: CallbackQuery, session: AsyncSession):
    """Continúa el onboarding después del mensaje inicial."""
    user_id = callback.from_user.id

    container = ServiceContainer(session, callback.bot)

    # Obtener usuario y marcar como no nuevo
    user = await container.user.get_user(user_id)
    if user:
        user.is_new_user = False
        user.update_activity()

    # Obtener datos de gamificación
    level_name = "Visitante"
    favors = 0

    try:
        from bot.gamification.services.container import GamificationContainer
        gamification = GamificationContainer(session, callback.bot)

        user_gam = await gamification.user_gamification.get_or_create_profile(user_id)
        if user_gam and user_gam.current_level:
            level_name = user_gam.current_level.name

        besitos_balance = await gamification.besitos.get_balance(user_id)
        favors = besitos_balance or 0
    except Exception as e:
        logger.warning(f"⚠️ Error obteniendo gamificación: {e}")

    # Mensaje de registro completado
    text = Lucien.START_REGISTERED.format(
        level_name=level_name,
        favors=favors
    )

    await callback.message.edit_text(
        text,
        reply_markup=lucien_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
    await session.commit()


@user_router.callback_query(F.data == "start:menu")
async def callback_show_menu(callback: CallbackQuery, session: AsyncSession):
    """Muestra el menú principal."""
    context = await _get_user_context(session, callback.from_user.id, callback.bot)

    text = Lucien.START_REGISTERED.format(
        level_name=context["level_name"],
        favors=context["favors"]
    )

    await callback.message.edit_text(
        text,
        reply_markup=lucien_main_menu_keyboard(context["is_vip"]),
        parse_mode="HTML"
    )
    await callback.answer()


@user_router.callback_query(F.data == "start:profile")
async def callback_show_profile(callback: CallbackQuery, session: AsyncSession):
    """Muestra el perfil del usuario."""
    from bot.utils.menu_helpers import build_profile_menu

    try:
        summary, keyboard = await build_profile_menu(
            session=session,
            bot=callback.bot,
            user_id=callback.from_user.id
        )

        await callback.message.edit_text(
            text=summary,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"❌ Error mostrando profile: {e}", exc_info=True)
        await callback.answer("Error al cargar perfil", show_alert=True)


@user_router.callback_query(F.data == "profile:back")
async def callback_back_to_start(callback: CallbackQuery, session: AsyncSession):
    """Regresa al menú principal."""
    context = await _get_user_context(session, callback.from_user.id, callback.bot)

    text = Lucien.START_REGISTERED.format(
        level_name=context["level_name"],
        favors=context["favors"]
    )

    await callback.message.edit_text(
        text,
        reply_markup=lucien_main_menu_keyboard(context["is_vip"]),
        parse_mode="HTML"
    )
    await callback.answer()


# =============================================================================
# DEEP LINK HANDLER
# =============================================================================

async def _activate_token_from_deeplink(
    message: Message,
    session: AsyncSession,
    container: ServiceContainer,
    user,
    token_string: str
):
    """Activa un token VIP desde un deep link."""
    from bot.utils.formatters import format_currency

    try:
        is_valid, msg_result, token = await container.subscription.validate_token(token_string)

        if not is_valid:
            await message.answer(
                "El token que intenta usar no es válido.\n\n"
                "Posibles causas:\n"
                "- Token incorrecto\n"
                "- Token ya utilizado\n"
                "- Token expirado\n\n"
                "Contacte con quien le proporcionó el enlace.",
                parse_mode="HTML"
            )
            return

        plan = token.plan if hasattr(token, 'plan') else None

        if not plan:
            await message.answer(
                "Este token no tiene un plan de suscripción asociado.\n\n"
                "Contacte al administrador.",
                parse_mode="HTML"
            )
            return

        # Marcar token como usado
        token.used = True
        token.used_by = user.user_id
        token.used_at = datetime.utcnow()

        # Activar suscripción VIP
        subscriber = await container.subscription.activate_vip_subscription(
            user_id=user.user_id,
            token_id=token.id,
            duration_hours=plan.duration_days * 24
        )

        # Actualizar rol
        user.role = UserRole.VIP
        user.is_new_user = False
        user.update_activity()

        await session.commit()
        await session.refresh(subscriber)

        logger.info(f"✅ Usuario {user.user_id} activado como VIP | Plan: {plan.name}")

        # Generar link de invitación
        vip_channel_id = await container.channel.get_vip_channel_id()

        if not vip_channel_id:
            await message.answer(
                "Su suscripción fue activada exitosamente.\n\n"
                "Sin embargo, el canal VIP no está configurado actualmente. "
                "Contacte al administrador para obtener acceso.",
                parse_mode="HTML"
            )
            return

        try:
            invite_link = await container.subscription.create_invite_link(
                channel_id=vip_channel_id,
                user_id=user.user_id,
                expire_hours=5
            )

            expiry = subscriber.expiry_date
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)
            days_remaining = max(0, (expiry - now).days)

            text = (
                "Bienvenido al Diván.\n\n"
                "Diana ha aprobado su acceso. Su suscripción está activa.\n\n"
                f"<b>Plan:</b> {plan.name}\n"
                f"<b>Duración:</b> {plan.duration_days} días\n"
                f"<b>Válido hasta:</b> {days_remaining} días restantes\n\n"
                "El botón a continuación le dará acceso al canal exclusivo. "
                "Tiene 5 horas para utilizarlo.\n\n"
                "No comparta este enlace. Es personal e intransferible."
            )

            await message.answer(
                text=text,
                reply_markup=create_inline_keyboard([
                    [{"text": "Entrar al Diván", "url": invite_link.invite_link}]
                ]),
                parse_mode="HTML"
            )

        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear invite link: {e}")

            await message.answer(
                "Su suscripción VIP ha sido activada correctamente.\n\n"
                f"<b>Plan:</b> {plan.name}\n"
                f"<b>Duración:</b> {plan.duration_days} días\n\n"
                "Hubo un problema al crear el enlace de invitación. "
                "Contacte al administrador para obtener acceso al canal.",
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"❌ Error activando token: {e}", exc_info=True)

        await message.answer(
            "Ocurrió un error al procesar su solicitud.\n\n"
            "Contacte al administrador.",
            parse_mode="HTML"
        )
