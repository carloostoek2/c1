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
    if is_vip:
        buttons = [
            [{"text": "Continuar Historia", "callback_data": "story:continue"}],
            [{"text": "Mi Perfil", "callback_data": "profile:view"}],
            [{"text": "El Gabinete", "callback_data": "cabinet:browse"}],
            [{"text": "Mis Encargos", "callback_data": "missions:list"}],
            [{"text": "Mis Favores", "callback_data": "favors:balance"}],
            [{"text": "Lo Nuevo", "callback_data": "content:new"}],
            [{"text": "Mapa del Deseo", "callback_data": "map:view"}],
        ]
    else:
        buttons = [
            [{"text": "La Historia", "callback_data": "story:start"}],
            [{"text": "Mi Perfil", "callback_data": "profile:view"}],
            [{"text": "El Gabinete", "callback_data": "cabinet:browse"}],
            [{"text": "Mis Encargos", "callback_data": "missions:list"}],
            [{"text": "Mis Favores", "callback_data": "favors:balance"}],
        ]

    return create_inline_keyboard(buttons)


def lucien_returning_long_keyboard() -> dict:
    """Keyboard para usuario ausente > 14 días."""
    return create_inline_keyboard([
        [{"text": "Ver qué hay de nuevo", "callback_data": "content:new"}],
        [{"text": "Ir al menú principal", "callback_data": "start:menu"}]
    ])


def lucien_profile_keyboard() -> dict:
    """Keyboard para la vista de perfil."""
    return create_inline_keyboard([
        [{"text": "Ver todos mis distintivos", "callback_data": "profile:badges"}],
        [{"text": "Volver al menú", "callback_data": "start:menu"}]
    ])


# =============================================================================
# HELPERS
# =============================================================================

async def _get_context_message(session: AsyncSession, user_id: int, bot) -> str:
    """
    Obtiene el mensaje de contexto dinámico según el estado del usuario.

    Prioridad:
    1. Tiene misión diaria sin completar
    2. Subió de nivel recientemente
    3. Tiene favores acumulados (>20)
    4. Racha activa 7+ días
    5. Default

    Returns:
        Mensaje de contexto de Lucien
    """
    try:
        from bot.gamification.services.container import GamificationContainer
        gamification = GamificationContainer(session, bot)

        # Verificar misión pendiente
        try:
            pending_missions = await gamification.mission.get_pending_missions(user_id)
            if pending_missions:
                return Lucien.MENU_CONTEXT_MISSION_PENDING
        except Exception as e:
            logger.warning(f"⚠️ Error verificando misiones pendientes para usuario {user_id}: {e}")

        # Verificar favores acumulados (>20)
        try:
            balance = await gamification.besitos.get_balance(user_id)
            if balance and balance > 20:
                return Lucien.MENU_CONTEXT_FAVORS_ACCUMULATED
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo balance de favores para usuario {user_id}: {e}")

        # Verificar racha activa 7+ días
        try:
            streak = await gamification.daily_gift.get_streak_info(user_id)
            if streak and streak.get("current_streak", 0) >= 7:
                return Lucien.MENU_CONTEXT_STREAK_ACTIVE
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo racha para usuario {user_id}: {e}")

    except Exception as e:
        logger.warning(f"⚠️ Error obteniendo contexto: {e}")

    return Lucien.MENU_CONTEXT_DEFAULT


def _create_progress_bar(current: int, maximum: int, length: int = 10) -> str:
    """
    Crea una barra de progreso visual.

    Args:
        current: Valor actual
        maximum: Valor máximo
        length: Longitud de la barra (default 10)

    Returns:
        String con barra de progreso (ej: "▓▓▓▓▓▒▒▒▒▒")
    """
    if maximum <= 0:
        return "▒" * length

    filled = int((current / maximum) * length)
    filled = min(filled, length)
    empty = length - filled

    return "▓" * filled + "▒" * empty


def _get_profile_comment(level_number: int) -> str:
    """Obtiene el comentario de Lucien según el nivel."""
    if level_number <= 2:
        return Lucien.PROFILE_COMMENT_LEVEL_1_2
    elif level_number <= 4:
        return Lucien.PROFILE_COMMENT_LEVEL_3_4
    elif level_number <= 6:
        return Lucien.PROFILE_COMMENT_LEVEL_5_6
    else:
        return Lucien.PROFILE_COMMENT_LEVEL_7


async def _get_user_context(session: AsyncSession, user_id: int, bot) -> dict:
    """
    Obtiene el contexto completo del usuario para determinar el flujo.

    Returns:
        Dict con datos completos del usuario para menú y perfil
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
            "level_number": 1,
            "level_progress": 0,
            "level_next_req": 100,
            "favors": 0,
            "vip_days": 0,
            "archetype": None,
            "archetype_name": None,
            "streak_status": "",
            "current_streak": 0,
            "best_streak": 0,
            "total_days": 0,
            "chapters_done": 0,
            "chapters_total": 6,
            "badges": [],
        }

    # Verificar VIP
    is_vip = await container.subscription.is_vip_active(user_id)

    # Calcular días de ausencia
    days_away = user.days_since_last_activity

    # Calcular días totales en el sistema
    total_days = 0
    if user.created_at:
        created = user.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        total_days = (datetime.now(timezone.utc) - created).days

    # Obtener datos de gamificación
    level_name = "Visitante"
    level_number = 1
    level_progress = 0
    level_next_req = 100
    favors = 0
    archetype = None
    archetype_name = None
    streak_status = ""
    current_streak = 0
    best_streak = 0
    badges = []

    try:
        from bot.gamification.services.container import GamificationContainer
        gamification = GamificationContainer(session, bot)

        # Obtener nivel
        user_gam = await gamification.user_gamification.get_or_create_profile(user_id)
        if user_gam:
            if user_gam.current_level:
                level_name = user_gam.current_level.name
                level_number = user_gam.current_level.level_number
                level_next_req = user_gam.current_level.min_besitos_required or 100

            # Obtener progreso hacia siguiente nivel
            level_progress = user_gam.total_besitos or 0

            # Obtener arquetipo
            archetype = user_gam.archetype if user_gam else None
            if archetype:
                archetype_val = archetype.value if hasattr(archetype, 'value') else archetype
                archetype_names = {
                    "explorer": "Explorador",
                    "direct": "Directo",
                    "romantic": "Romántico",
                    "analytical": "Analítico",
                    "persistent": "Persistente",
                    "patient": "Paciente",
                    "impulsive": "Impulsivo",
                    "contemplative": "Contemplativo",
                    "silent": "Silencioso",
                }
                archetype_name = archetype_names.get(archetype_val)

        # Obtener favores (besitos)
        besitos_balance = await gamification.besitos.get_balance(user_id)
        favors = besitos_balance or 0

        # Obtener estado de racha
        streak = await gamification.daily_gift.get_streak_info(user_id)
        if streak:
            current_streak = streak.get("current_streak", 0)
            best_streak = streak.get("best_streak", 0)
            if current_streak > 0:
                streak_status = f"Racha activa: {current_streak} días"
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

    # Obtener capítulos completados (placeholder)
    chapters_done = 0
    chapters_total = 6

    return {
        "user": user,
        "is_new": is_new,
        "is_vip": is_vip,
        "days_away": days_away,
        "level_name": level_name,
        "level_number": level_number,
        "level_progress": level_progress,
        "level_next_req": level_next_req,
        "favors": favors,
        "vip_days": vip_days,
        "archetype": archetype,
        "archetype_name": archetype_name,
        "streak_status": streak_status,
        "current_streak": current_streak,
        "best_streak": best_streak,
        "total_days": total_days,
        "chapters_done": chapters_done,
        "chapters_total": chapters_total,
        "badges": badges,
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


@user_router.callback_query(F.data.in_({"start:profile", "profile:view"}))
async def callback_show_profile(callback: CallbackQuery, session: AsyncSession):
    """Muestra el perfil del usuario con la voz de Lucien."""
    try:
        context = await _get_user_context(session, callback.from_user.id, callback.bot)

        # Construir barra de progreso
        progress_bar = _create_progress_bar(
            context["level_progress"],
            context["level_next_req"]
        )

        # Construir sección de arquetipo
        archetype_section = ""
        if context["archetype_name"]:
            archetype_descriptions = {
                "Explorador": "Busca cada detalle, quiere ver todo.",
                "Directo": "Va al grano, sin rodeos.",
                "Romántico": "Busca conexión, no solo contenido.",
                "Analítico": "Estudia, calcula, optimiza.",
                "Persistente": "No se rinde ante el primer fracaso.",
                "Paciente": "Toma su tiempo, procesa profundamente.",
                "Impulsivo": "Actúa primero, reflexiona después.",
                "Contemplativo": "Observa antes de actuar.",
                "Silencioso": "Prefiere observar en las sombras.",
            }
            desc = archetype_descriptions.get(context["archetype_name"], "")
            archetype_section = f'\nClasificación: <b>{context["archetype_name"]}</b>\n"{desc}"\n'

        # Construir sección de distinciones
        badges_section = ""
        if context["badges"]:
            badges_display = context["badges"][:6]
            badges_section = " ".join(badges_display)
            if len(context["badges"]) > 6:
                badges_section += f'\n+ {len(context["badges"]) - 6} más'
        else:
            badges_section = "Ninguna distinción aún."

        # Comentario de Lucien
        lucien_comment = _get_profile_comment(context["level_number"])

        # Construir mensaje completo
        text = f"""{Lucien.PROFILE_HEADER}

━━━━━━━━━━━━━━━━━━━━━━━━
PROTOCOLO DE ACCESO
━━━━━━━━━━━━━━━━━━━━━━━━

Nivel: <b>{context["level_number"]} - {context["level_name"]}</b>
Progreso: {progress_bar} {context["level_progress"]}/{context["level_next_req"]}
Favores: <b>{context["favors"]}</b>
{archetype_section}
━━━━━━━━━━━━━━━━━━━━━━━━
ACTIVIDAD
━━━━━━━━━━━━━━━━━━━━━━━━

Días en el universo: <b>{context["total_days"]}</b>
Racha actual: <b>{context["current_streak"]}</b> días
Mejor racha: <b>{context["best_streak"]}</b> días
Capítulos completados: <b>{context["chapters_done"]}/{context["chapters_total"]}</b>

━━━━━━━━━━━━━━━━━━━━━━━━
DISTINCIONES
━━━━━━━━━━━━━━━━━━━━━━━━

{badges_section}

━━━━━━━━━━━━━━━━━━━━━━━━

<i>{lucien_comment}</i>"""

        await callback.message.edit_text(
            text=text,
            reply_markup=lucien_profile_keyboard(),
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


# =============================================================================
# CALLBACKS DEL MENÚ PRINCIPAL
# =============================================================================

@user_router.callback_query(F.data.in_({"story:start", "story:continue"}))
async def callback_story(callback: CallbackQuery, session: AsyncSession):
    """Handler para iniciar/continuar la historia."""
    context = await _get_user_context(session, callback.from_user.id, callback.bot)

    if callback.data == "story:continue" and context["is_vip"]:
        text = (
            "La historia continúa en el Diván.\n\n"
            "Diana ha preparado nuevos capítulos para usted. "
            "Los secretos que aún no conoce están a punto de revelarse."
        )
    else:
        text = (
            "La Historia del Diván.\n\n"
            "Cada capítulo revela más sobre Diana y su universo. "
            "Pero los capítulos más profundos... esos requieren algo más que curiosidad."
        )

    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_keyboard([
            [{"text": "Volver al menú", "callback_data": "start:menu"}]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@user_router.callback_query(F.data == "cabinet:browse")
async def callback_cabinet(callback: CallbackQuery, session: AsyncSession):
    """Handler para el Gabinete (tienda)."""
    text = (
        "Bienvenido a mi Gabinete.\n\n"
        "Aquí guardo ciertos... artículos que Diana ha autorizado para intercambio.\n\n"
        "Los Favores que ha acumulado pueden convertirse en algo más tangible. "
        "Examine con cuidado. No todo lo que brilla merece su inversión."
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_keyboard([
            [{"text": "Ver artículos", "callback_data": "shop:browse"}],
            [{"text": "Volver al menú", "callback_data": "start:menu"}]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@user_router.callback_query(F.data == "missions:list")
async def callback_missions(callback: CallbackQuery, session: AsyncSession):
    """Handler para Mis Encargos (misiones)."""
    text = (
        "Sus Encargos.\n\n"
        "Diana asigna tareas a quienes considera dignos de su atención. "
        "Completarlas demuestra compromiso. Los Favores son su recompensa."
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_keyboard([
            [{"text": "Ver encargos activos", "callback_data": "user:missions"}],
            [{"text": "Volver al menú", "callback_data": "start:menu"}]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@user_router.callback_query(F.data == "favors:balance")
async def callback_favors(callback: CallbackQuery, session: AsyncSession):
    """Handler para ver balance de Favores."""
    context = await _get_user_context(session, callback.from_user.id, callback.bot)

    text = (
        f"Sus Favores: <b>{context['favors']}</b>\n\n"
        "Cada Favor representa un momento en que Diana consideró que usted "
        "merecía reconocimiento.\n\n"
        "Úselos con criterio. El Gabinete ofrece formas de invertirlos."
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_keyboard([
            [{"text": "Ir al Gabinete", "callback_data": "cabinet:browse"}],
            [{"text": "Volver al menú", "callback_data": "start:menu"}]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@user_router.callback_query(F.data == "content:new")
async def callback_new_content(callback: CallbackQuery, session: AsyncSession):
    """Handler para contenido nuevo."""
    context = await _get_user_context(session, callback.from_user.id, callback.bot)

    if context["is_vip"]:
        text = (
            "Lo Nuevo en el Diván.\n\n"
            "Diana ha estado activa. Hay contenido fresco esperando su atención.\n\n"
            "Los privilegios de su membresía le dan acceso a todo lo nuevo."
        )
    else:
        text = (
            "Lo Nuevo.\n\n"
            "El universo de Diana sigue expandiéndose. "
            "Pero parte de ese contenido... está reservado para el Diván.\n\n"
            "Si desea acceso completo, hay formas de obtenerlo."
        )

    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_keyboard([
            [{"text": "Volver al menú", "callback_data": "start:menu"}]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@user_router.callback_query(F.data == "map:view")
async def callback_map(callback: CallbackQuery, session: AsyncSession):
    """Handler para el Mapa del Deseo (solo VIP)."""
    text = (
        "El Mapa del Deseo.\n\n"
        "Un recorrido personalizado por los territorios de Diana. "
        "No es para todos. Solo para quienes buscan algo más profundo que el acceso.\n\n"
        "Pronto, más detalles sobre cómo navegar este mapa."
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_keyboard([
            [{"text": "Volver al menú", "callback_data": "start:menu"}]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()


@user_router.callback_query(F.data == "profile:badges")
async def callback_badges(callback: CallbackQuery, session: AsyncSession):
    """Handler para ver todas las distinciones."""
    text = (
        "Sus Distinciones.\n\n"
        "Cada distintivo representa un logro en el universo de Diana.\n\n"
        "Por ahora, su colección está vacía. "
        "Pero con el tiempo y la dedicación, eso puede cambiar."
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=create_inline_keyboard([
            [{"text": "Volver al perfil", "callback_data": "profile:view"}],
            [{"text": "Volver al menú", "callback_data": "start:menu"}]
        ]),
        parse_mode="HTML"
    )
    await callback.answer()
