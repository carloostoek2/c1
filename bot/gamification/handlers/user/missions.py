"""
Handler para Encargos (Misiones) del usuario con la voz de Lucien.

Funcionalidades:
- Ver encargos en progreso
- Ver encargos completados
- Reclamar recompensas de encargos
- Ver encargos disponibles
"""

import logging
from datetime import datetime, timezone, timedelta

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.middlewares import DatabaseMiddleware
from bot.gamification.services.container import GamificationContainer
from bot.gamification.database.enums import MissionStatus
from bot.utils.lucien_messages import Lucien
from bot.utils.keyboards import create_inline_keyboard

logger = logging.getLogger(__name__)

router = Router()

# Registrar middleware para inyectar session y gamification
router.callback_query.middleware(DatabaseMiddleware())


# =============================================================================
# HELPERS
# =============================================================================

def _format_time_remaining(expires_at: datetime) -> str:
    """Formatea el tiempo restante hasta expiración."""
    if not expires_at:
        return "Sin límite"

    now = datetime.now(timezone.utc)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    delta = expires_at - now

    if delta.total_seconds() <= 0:
        return "Expirado"

    hours = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)

    if hours > 24:
        days = hours // 24
        return f"{days}d {hours % 24}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def _format_time_until_reset() -> str:
    """Formatea el tiempo hasta el próximo reset (medianoche UTC)."""
    now = datetime.now(timezone.utc)
    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    delta = tomorrow - now

    hours = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)

    return f"{hours}h {minutes}m"


def _get_mission_complete_comment(mission_type: str, current_streak: int = 0) -> str:
    """Obtiene el comentario de Lucien según el tipo de misión."""
    if mission_type == "daily":
        if current_streak > 1:
            return Lucien.MISSION_COMPLETE_DAILY_STREAK
        else:
            return Lucien.MISSION_COMPLETE_DAILY_FIRST
    elif mission_type == "weekly":
        return Lucien.MISSION_COMPLETE_WEEKLY
    else:
        return Lucien.MISSION_COMPLETE_SPECIAL


# =============================================================================
# VISTA PRINCIPAL DE ENCARGOS
# =============================================================================

@router.callback_query(F.data == "user:missions")
async def show_missions(callback: CallbackQuery, gamification: GamificationContainer):
    """
    Lista encargos del usuario con el estilo de Lucien.

    Secciones:
    - PROTOCOLO DIARIO: Misiones diarias
    - ENCARGO SEMANAL: Misiones semanales
    - EVALUACIONES ESPECIALES: Misiones narrativas/especiales
    """
    try:
        user_id = callback.from_user.id

        # Obtener misiones del usuario
        in_progress = await gamification.mission.get_user_missions(
            user_id, status=MissionStatus.IN_PROGRESS
        )
        completed = await gamification.mission.get_user_missions(
            user_id, status=MissionStatus.COMPLETED
        )

        # Obtener misiones disponibles (no iniciadas)
        all_missions = await gamification.mission.get_all_missions()
        user_mission_ids = {um.mission_id for um in (in_progress + completed)}
        available = [m for m in all_missions if m.id not in user_mission_ids]

        # Construir mensaje con secciones
        text = f"{Lucien.MISSIONS_HEADER}\n\n"
        keyboard_buttons = []

        # Separar por tipo
        daily_missions = [um for um in in_progress if um.mission.criteria.get('type') == 'daily']
        weekly_missions = [um for um in in_progress if um.mission.criteria.get('type') == 'weekly']
        special_missions = [um for um in in_progress if um.mission.criteria.get('type') not in ['daily', 'weekly']]

        daily_completed = [um for um in completed if um.mission.criteria.get('type') == 'daily']
        weekly_completed = [um for um in completed if um.mission.criteria.get('type') == 'weekly']

        # ━━━━━━━━━━━━━━━━━━━━━━━━
        # PROTOCOLO DIARIO
        # ━━━━━━━━━━━━━━━━━━━━━━━━
        text += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"{Lucien.MISSIONS_DAILY_HEADER}\n"
        text += f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        if daily_missions:
            for um in daily_missions:
                mission = um.mission
                progress = um.progress_data or {}
                current = progress.get('count', progress.get('current_streak', 0))
                required = mission.criteria.get('count', mission.criteria.get('days', 1))

                text += f"▸ {mission.name}\n"
                text += f"  {mission.description}\n"
                text += f"  Progreso: {current}/{required}\n"
                text += f"  Recompensa: +{mission.besitos_reward} Favor(es)\n"

                if hasattr(um, 'expires_at') and um.expires_at:
                    text += f"  Expira en: {_format_time_remaining(um.expires_at)}\n"

                text += "\n"

                keyboard_buttons.append([{
                    "text": f"Ver: {mission.name}",
                    "callback_data": f"user:mission:view:{mission.id}"
                }])
        elif daily_completed:
            text += Lucien.MISSIONS_DAILY_COMPLETE.format(
                time_until_reset=_format_time_until_reset()
            )
            text += "\n\n"
        else:
            text += "Sin encargos diarios activos.\n\n"

        # ━━━━━━━━━━━━━━━━━━━━━━━━
        # ENCARGO SEMANAL
        # ━━━━━━━━━━━━━━━━━━━━━━━━
        text += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"{Lucien.MISSIONS_WEEKLY_HEADER}\n"
        text += f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        if weekly_missions:
            for um in weekly_missions:
                mission = um.mission
                progress = um.progress_data or {}
                current = progress.get('count', 0)
                required = mission.criteria.get('count', 1)

                text += f"▸ {mission.name}\n"
                text += f"  {mission.description}\n"
                text += f"  Progreso: {current}/{required}\n"
                text += f"  Recompensa: +{mission.besitos_reward} Favor(es)\n\n"

                keyboard_buttons.append([{
                    "text": f"Ver: {mission.name}",
                    "callback_data": f"user:mission:view:{mission.id}"
                }])
        else:
            text += "Sin encargos semanales activos.\n\n"

        # ━━━━━━━━━━━━━━━━━━━━━━━━
        # EVALUACIONES ESPECIALES
        # ━━━━━━━━━━━━━━━━━━━━━━━━
        if special_missions or available:
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            text += f"{Lucien.MISSIONS_SPECIAL_HEADER}\n"
            text += f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

            if special_missions:
                for um in special_missions:
                    mission = um.mission
                    text += f"▸ {mission.name}\n"
                    text += f"  {mission.description}\n"
                    text += f"  Recompensa: +{mission.besitos_reward} Favor(es)\n\n"

                    keyboard_buttons.append([{
                        "text": f"Ver: {mission.name}",
                        "callback_data": f"user:mission:view:{mission.id}"
                    }])

        # Misiones completadas pendientes de reclamar
        unclaimed = [um for um in completed if not getattr(um, 'reward_claimed', False)]
        if unclaimed:
            text += "\n<b>Pendientes de reclamar:</b>\n"
            for um in unclaimed:
                mission = um.mission
                text += f"▸ {mission.name} — +{mission.besitos_reward} Favor(es)\n"
                keyboard_buttons.append([{
                    "text": f"Reclamar: {mission.name}",
                    "callback_data": f"user:mission:claim:{mission.id}"
                }])

        # Si no hay nada
        if not (in_progress or completed or available):
            text = Lucien.MISSIONS_EMPTY

        keyboard_buttons.append([{
            "text": "Volver al menú",
            "callback_data": "start:menu"
        }])

        await callback.message.edit_text(
            text,
            reply_markup=create_inline_keyboard(keyboard_buttons),
            parse_mode="HTML"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"❌ Error mostrando misiones: {e}", exc_info=True)
        await callback.answer("Error al cargar encargos", show_alert=True)


# =============================================================================
# VER DETALLE DE MISIÓN
# =============================================================================

@router.callback_query(F.data.startswith("user:mission:view:"))
async def view_mission_progress(callback: CallbackQuery, gamification: GamificationContainer):
    """
    Muestra progreso detallado de un encargo.

    Muestra:
    - Nombre y descripción
    - Progreso actual vs requerido
    - Recompensa al completar
    """
    try:
        mission_id = int(callback.data.split(":")[-1])
        user_id = callback.from_user.id

        # Obtener misión y progreso
        mission = await gamification.mission.get_mission(mission_id)
        user_mission = await gamification.mission.get_user_mission(user_id, mission_id)

        if not mission or not user_mission:
            await callback.answer("Encargo no encontrado", show_alert=True)
            return

        # Construir mensaje de progreso
        text = f"<b>{mission.name}</b>\n\n"
        text += f"{mission.description}\n\n"

        # Mostrar progreso según tipo
        criteria = mission.criteria
        progress = user_mission.progress_data or {}

        mission_type = criteria.get('type', 'one_time')

        if mission_type == 'streak':
            current_days = progress.get('current_streak', 0)
            required_days = criteria.get('days', 0)
            text += f"Progreso: {current_days}/{required_days} días consecutivos\n"
        else:
            current_count = progress.get('count', 0)
            required_count = criteria.get('count', 1)
            text += f"Progreso: {current_count}/{required_count}\n"

        text += f"\nRecompensa: +{mission.besitos_reward} Favor(es)"

        # Verificar si está completada
        if user_mission.status == MissionStatus.COMPLETED:
            text += "\n\n<i>Encargo completado. Reclame su recompensa.</i>"
            buttons = [
                [{"text": "Reclamar recompensa", "callback_data": f"user:mission:claim:{mission_id}"}],
                [{"text": "Volver a encargos", "callback_data": "user:missions"}]
            ]
        else:
            buttons = [[{"text": "Volver a encargos", "callback_data": "user:missions"}]]

        await callback.message.edit_text(
            text,
            reply_markup=create_inline_keyboard(buttons),
            parse_mode="HTML"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"❌ Error mostrando detalle de misión: {e}", exc_info=True)
        await callback.answer("Error al cargar detalle", show_alert=True)


# =============================================================================
# RECLAMAR RECOMPENSA
# =============================================================================

@router.callback_query(F.data.startswith("user:mission:claim:"))
async def claim_mission_reward(callback: CallbackQuery, gamification: GamificationContainer):
    """
    Reclama recompensa de un encargo completado.

    Flujo:
    1. Valida que el encargo esté completado
    2. Otorga favores al usuario
    3. Marca como reclamado
    4. Muestra mensaje de Lucien con comentario según tipo
    """
    try:
        mission_id = int(callback.data.split(":")[-1])
        user_id = callback.from_user.id

        # Obtener misión para datos
        mission = await gamification.mission.get_mission(mission_id)
        if not mission:
            await callback.answer("Encargo no encontrado", show_alert=True)
            return

        # Intentar reclamar recompensa
        success, message, rewards_info = await gamification.mission.claim_reward(
            user_id, mission_id
        )

        if success:
            # Obtener datos para el mensaje
            mission_type = mission.criteria.get('type', 'one_time')

            # Obtener racha actual para el comentario
            current_streak = 0
            try:
                streak_info = await gamification.daily_gift.get_streak_info(user_id)
                current_streak = streak_info.get('current_streak', 0) if streak_info else 0
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo racha del usuario {user_id}: {e}")

            comment = _get_mission_complete_comment(mission_type, current_streak)

            # Obtener nuevo total de favores
            new_total = 0
            try:
                new_total = await gamification.besitos.get_balance(user_id) or 0
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo balance del usuario {user_id}: {e}")

            text = Lucien.MISSION_COMPLETE.format(
                mission_name=mission.name,
                amount=mission.besitos_reward,
                comment=comment,
                new_total=new_total
            )

            buttons = [
                [{"text": "Ver próximo encargo", "callback_data": "user:missions"}],
                [{"text": "Volver al menú", "callback_data": "start:menu"}]
            ]

            await callback.message.edit_text(
                text,
                reply_markup=create_inline_keyboard(buttons),
                parse_mode="HTML"
            )
            await callback.answer()

        else:
            await callback.answer(f"No se pudo reclamar: {message}", show_alert=True)

    except Exception as e:
        logger.error(f"❌ Error reclamando recompensa: {e}", exc_info=True)
        await callback.answer("Error al reclamar recompensa", show_alert=True)
