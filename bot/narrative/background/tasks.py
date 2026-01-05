"""
Background tasks para el módulo de narrativa.

Tareas programadas que se ejecutan periódicamente para mantener
el sistema de narrativa (cleanup de cooldowns, reset de límites diarios).
"""
import logging
from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler

if TYPE_CHECKING:
    from aiogram import Bot

from bot.database.engine import get_session
from bot.narrative.services.engagement import EngagementService
from bot.narrative.services.cooldown import CooldownService

logger = logging.getLogger(__name__)

# Scheduler global
_narrative_scheduler: AsyncIOScheduler | None = None


async def reset_daily_narrative_limits():
    """
    Reset de límites diarios de narrativa.

    Ejecutar diariamente a medianoche (00:00 UTC) para resetear
    contadores de fragmentos, decisiones y challenges.
    """
    try:
        async with get_session() as session:
            engagement_service = EngagementService(session)
            count = await engagement_service.reset_daily_limits()

            if count > 0:
                logger.info(
                    f"[Narrative] Reset de límites diarios: {count} usuarios procesados"
                )
            else:
                logger.debug("[Narrative] Reset de límites: sin usuarios pendientes")

    except Exception as e:
        logger.error(
            f"[Narrative] Error en reset de límites diarios: {e}", exc_info=True
        )


async def cleanup_expired_cooldowns():
    """
    Limpieza de cooldowns expirados.

    Ejecutar cada hora para eliminar registros de cooldowns
    que ya expiraron y no son necesarios en la BD.
    """
    try:
        async with get_session() as session:
            cooldown_service = CooldownService(session)
            count = await cooldown_service.cleanup_expired_cooldowns()

            if count > 0:
                logger.info(
                    f"[Narrative] Cleanup de cooldowns: {count} registros eliminados"
                )
            else:
                logger.debug("[Narrative] Cleanup de cooldowns: sin registros expirados")

    except Exception as e:
        logger.error(
            f"[Narrative] Error en cleanup de cooldowns: {e}", exc_info=True
        )


def start_narrative_tasks(bot: "Bot"):
    """
    Inicia las tareas programadas de narrativa.

    Args:
        bot: Instancia del bot de Telegram
    """
    global _narrative_scheduler

    if _narrative_scheduler is not None and _narrative_scheduler.running:
        logger.warning(
            "[Narrative] Scheduler ya está corriendo, ignorando segundo start"
        )
        return

    _narrative_scheduler = AsyncIOScheduler(timezone="UTC")

    # Reset de límites diarios a medianoche (00:00 UTC)
    _narrative_scheduler.add_job(
        reset_daily_narrative_limits,
        trigger="cron",
        hour=0,
        minute=0,
        id="reset_narrative_limits",
        replace_existing=True,
        max_instances=1,
    )

    # Cleanup de cooldowns cada hora
    _narrative_scheduler.add_job(
        cleanup_expired_cooldowns,
        trigger="interval",
        hours=1,
        id="cleanup_narrative_cooldowns",
        replace_existing=True,
        max_instances=1,
    )

    _narrative_scheduler.start()

    logger.info("[Narrative] Background tasks iniciados")


def stop_narrative_tasks():
    """Detiene las tareas programadas de narrativa."""
    global _narrative_scheduler

    if _narrative_scheduler is None or not _narrative_scheduler.running:
        logger.warning(
            "[Narrative] Scheduler no está corriendo, ignorando stop"
        )
        return

    _narrative_scheduler.shutdown(wait=True)
    _narrative_scheduler = None

    logger.info("[Narrative] Background tasks detenidos")


def get_narrative_scheduler_status() -> dict:
    """
    Obtiene el estado del scheduler de narrativa.

    Returns:
        dict: Estado del scheduler
            - running: Si está corriendo
            - jobs: Lista de jobs programados
    """
    if _narrative_scheduler is None:
        return {"running": False, "jobs": []}

    jobs = []
    if _narrative_scheduler.running:
        for job in _narrative_scheduler.get_jobs():
            jobs.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": str(job.next_run_time) if job.next_run_time else None,
                }
            )

    return {
        "running": _narrative_scheduler.running,
        "jobs": jobs,
    }
