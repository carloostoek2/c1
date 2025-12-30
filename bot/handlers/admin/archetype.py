"""
Archetype Admin Handlers - Comandos de administración de arquetipos.

Handlers para:
- Ver arquetipo de un usuario específico
- Estadísticas globales de arquetipos
- Forzar re-evaluación de arquetipo
"""

import logging
from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.admin.main import admin_router
from bot.gamification.services.container import GamificationContainer
from bot.database.enums import ArchetypeType
from bot.utils.keyboards import back_to_main_menu_keyboard

logger = logging.getLogger(__name__)


# ========================================
# CONSTANTES
# ========================================

ARCHETYPE_EMOJIS = {
    ArchetypeType.EXPLORER: "🔍",
    ArchetypeType.DIRECT: "⚡",
    ArchetypeType.ROMANTIC: "💝",
    ArchetypeType.ANALYTICAL: "🧠",
    ArchetypeType.PERSISTENT: "🔄",
    ArchetypeType.PATIENT: "⏳",
}

ARCHETYPE_NAMES = {
    ArchetypeType.EXPLORER: "El Explorador",
    ArchetypeType.DIRECT: "El Directo",
    ArchetypeType.ROMANTIC: "El Romántico",
    ArchetypeType.ANALYTICAL: "El Analítico",
    ArchetypeType.PERSISTENT: "El Persistente",
    ArchetypeType.PATIENT: "El Paciente",
}


# ========================================
# HELPER FUNCTIONS
# ========================================

def format_archetype_name(archetype: ArchetypeType) -> str:
    """Formatea nombre de arquetipo con emoji."""
    emoji = ARCHETYPE_EMOJIS.get(archetype, "❓")
    name = ARCHETYPE_NAMES.get(archetype, archetype.value)
    return f"{emoji} {name}"


def format_score_bar(score: float, width: int = 10) -> str:
    """Genera barra visual de progreso."""
    filled = int(score * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def format_percentage(value: float) -> str:
    """Formatea porcentaje."""
    return f"{value:.1f}%"


# ========================================
# COMANDO: /admin_archetype <user_id>
# ========================================

@admin_router.message(Command("admin_archetype"))
async def cmd_admin_archetype(
    message: Message,
    command: CommandObject,
    session: AsyncSession
):
    """
    Muestra información del arquetipo de un usuario.

    Uso: /admin_archetype <user_id>

    Muestra:
    - Arquetipo actual
    - Confianza
    - Scores de todos los arquetipos
    - Top 3 señales que más influyen
    - Fecha de detección
    - Interacciones desde detección
    """
    # Validar argumentos
    if not command.args:
        await message.answer(
            "❌ <b>Uso:</b> <code>/admin_archetype &lt;user_id&gt;</code>\n\n"
            "Ejemplo: <code>/admin_archetype 123456789</code>",
            parse_mode="HTML"
        )
        return

    try:
        user_id = int(command.args.strip())
    except ValueError:
        await message.answer(
            "❌ <b>Error:</b> El user_id debe ser un número.",
            parse_mode="HTML"
        )
        return

    logger.info(f"Admin {message.from_user.id} consultando arquetipo de user {user_id}")

    container = GamificationContainer(session)

    try:
        # Obtener insights
        insights = await container.archetype_detection.get_archetype_insights(user_id)

        # Construir mensaje
        if not insights.current_archetype:
            text = (
                f"📊 <b>Arquetipo de Usuario {user_id}</b>\n\n"
                f"Estado: <i>Sin arquetipo detectado</i>\n"
                f"Interacciones: {insights.total_interactions}\n\n"
            )

            if insights.total_interactions < 20:
                text += (
                    "ℹ️ Se necesitan al menos 20 interacciones para detectar arquetipo.\n"
                    f"Faltan: {20 - insights.total_interactions}"
                )
            else:
                text += "ℹ️ Datos insuficientes o confianza muy baja."
        else:
            # Formatear arquetipo actual
            archetype_display = format_archetype_name(insights.current_archetype)
            confidence_pct = format_percentage(insights.confidence * 100)

            text = (
                f"📊 <b>Arquetipo de Usuario {user_id}</b>\n\n"
                f"<b>Arquetipo:</b> {archetype_display}\n"
                f"<b>Confianza:</b> {confidence_pct}\n"
                f"<b>Interacciones:</b> {insights.total_interactions}\n"
            )

            if insights.detected_at:
                text += f"<b>Detectado:</b> {insights.detected_at.strftime('%Y-%m-%d %H:%M')}\n"

            # Top 3 arquetipos con barras
            text += "\n<b>Scores:</b>\n"
            for archetype, score in insights.top_archetypes:
                emoji = ARCHETYPE_EMOJIS.get(archetype, "❓")
                bar = format_score_bar(score)
                score_pct = format_percentage(score * 100)
                text += f"{emoji} {bar} {score_pct}\n"

            # Comportamientos clave
            if insights.key_behaviors:
                text += "\n<b>Señales principales:</b>\n"
                for behavior in insights.key_behaviors:
                    text += f"• {behavior}\n"

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error consultando arquetipo: {e}")
        await message.answer(
            f"❌ <b>Error:</b> No se pudo obtener información del usuario {user_id}.",
            parse_mode="HTML"
        )


# ========================================
# COMANDO: /admin_archetype_stats
# ========================================

@admin_router.message(Command("admin_archetype_stats"))
async def cmd_admin_archetype_stats(message: Message, session: AsyncSession):
    """
    Muestra estadísticas globales de arquetipos.

    Incluye:
    - Distribución de arquetipos (% de usuarios)
    - Usuarios sin arquetipo definido
    """
    logger.info(f"Admin {message.from_user.id} consultando estadísticas de arquetipos")

    container = GamificationContainer(session)

    try:
        # Obtener distribución
        distribution = await container.archetype_detection.get_archetype_distribution()
        unclassified = await container.archetype_detection.get_unclassified_count()

        # Calcular totales
        total_classified = sum(distribution.values())
        total_users = total_classified + unclassified

        # Construir mensaje
        text = "📊 <b>Estadísticas de Arquetipos</b>\n\n"

        if total_users == 0:
            text += "<i>No hay usuarios registrados.</i>"
        else:
            # Distribución
            text += "<b>Distribución:</b>\n"

            # Ordenar por cantidad (mayor a menor)
            sorted_dist = sorted(
                distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for archetype_value, count in sorted_dist:
                try:
                    archetype = ArchetypeType(archetype_value)
                    emoji = ARCHETYPE_EMOJIS.get(archetype, "❓")
                    name = ARCHETYPE_NAMES.get(archetype, archetype_value)
                except ValueError:
                    emoji = "❓"
                    name = archetype_value

                if total_classified > 0:
                    pct = (count / total_classified) * 100
                    bar = format_score_bar(pct / 100, width=8)
                    text += f"{emoji} {name}: {count} ({pct:.1f}%) {bar}\n"
                else:
                    text += f"{emoji} {name}: {count}\n"

            # Resumen
            text += f"\n<b>Resumen:</b>\n"
            text += f"✅ Clasificados: {total_classified}\n"
            text += f"❓ Sin arquetipo: {unclassified}\n"
            text += f"📊 Total usuarios: {total_users}\n"

            if total_users > 0:
                classification_rate = (total_classified / total_users) * 100
                text += f"📈 Tasa de clasificación: {classification_rate:.1f}%"

        await message.answer(text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de arquetipos: {e}")
        await message.answer(
            "❌ <b>Error:</b> No se pudieron obtener las estadísticas.",
            parse_mode="HTML"
        )


# ========================================
# COMANDO: /admin_archetype_refresh <user_id>
# ========================================

@admin_router.message(Command("admin_archetype_refresh"))
async def cmd_admin_archetype_refresh(
    message: Message,
    command: CommandObject,
    session: AsyncSession
):
    """
    Fuerza re-evaluación del arquetipo de un usuario.

    Uso: /admin_archetype_refresh <user_id>
    """
    # Validar argumentos
    if not command.args:
        await message.answer(
            "❌ <b>Uso:</b> <code>/admin_archetype_refresh &lt;user_id&gt;</code>\n\n"
            "Ejemplo: <code>/admin_archetype_refresh 123456789</code>",
            parse_mode="HTML"
        )
        return

    try:
        user_id = int(command.args.strip())
    except ValueError:
        await message.answer(
            "❌ <b>Error:</b> El user_id debe ser un número.",
            parse_mode="HTML"
        )
        return

    logger.info(f"Admin {message.from_user.id} forzando re-evaluación para user {user_id}")

    # Enviar mensaje de "procesando"
    processing_msg = await message.answer(
        "🔄 <b>Re-evaluando arquetipo...</b>",
        parse_mode="HTML"
    )

    container = GamificationContainer(session)

    try:
        # Forzar re-evaluación
        result = await container.archetype_detection.force_reevaluation(user_id)

        # Construir mensaje de resultado
        if result.is_detected:
            archetype_display = format_archetype_name(result.archetype)
            confidence_pct = format_percentage(result.confidence * 100)

            text = (
                f"✅ <b>Re-evaluación completada</b>\n\n"
                f"<b>Usuario:</b> {user_id}\n"
                f"<b>Nuevo arquetipo:</b> {archetype_display}\n"
                f"<b>Confianza:</b> {confidence_pct}\n\n"
                f"<b>Todos los scores:</b>\n"
            )

            # Mostrar todos los scores
            sorted_scores = sorted(
                result.scores.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for archetype_value, score in sorted_scores:
                try:
                    archetype = ArchetypeType(archetype_value)
                    emoji = ARCHETYPE_EMOJIS.get(archetype, "❓")
                except ValueError:
                    emoji = "❓"

                bar = format_score_bar(score)
                score_pct = format_percentage(score * 100)
                text += f"{emoji} {bar} {score_pct}\n"
        else:
            # No se detectó arquetipo
            reason_messages = {
                "no_signals": "No hay señales de comportamiento registradas.",
                "insufficient_data": "Insuficientes interacciones (mínimo 20).",
                "low_confidence": "Confianza muy baja para determinar arquetipo.",
            }
            reason_text = reason_messages.get(result.reason, result.reason)

            text = (
                f"⚠️ <b>No se pudo detectar arquetipo</b>\n\n"
                f"<b>Usuario:</b> {user_id}\n"
                f"<b>Razón:</b> {reason_text}\n"
            )

            if result.scores:
                text += "\n<b>Scores parciales:</b>\n"
                for archetype_value, score in sorted(
                    result.scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]:
                    try:
                        archetype = ArchetypeType(archetype_value)
                        emoji = ARCHETYPE_EMOJIS.get(archetype, "❓")
                    except ValueError:
                        emoji = "❓"
                    score_pct = format_percentage(score * 100)
                    text += f"{emoji} {score_pct}\n"

        # Editar mensaje
        try:
            await processing_msg.edit_text(text, parse_mode="HTML")
        except TelegramBadRequest:
            await message.answer(text, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error en re-evaluación de arquetipo: {e}")
        try:
            await processing_msg.edit_text(
                f"❌ <b>Error:</b> No se pudo re-evaluar el arquetipo para {user_id}.\n"
                f"<i>{str(e)[:100]}</i>",
                parse_mode="HTML"
            )
        except TelegramBadRequest:
            await message.answer(
                f"❌ <b>Error:</b> No se pudo re-evaluar el arquetipo.",
                parse_mode="HTML"
            )
