"""
Free Join Request Handler - ChatJoinRequest del canal Free.

Flujo:
1. Usuario hace click en "Unirse" en el canal Free
2. Telegram envía ChatJoinRequest al bot
3. Bot verifica canal correcto
4. Si duplicada: Declina + notifica tiempo restante
5. Si nueva: Registra en BD + envía mensaje de espera
6. Background task aprobará después de N minutos
"""
import logging
from aiogram import Router, F
from aiogram.types import ChatJoinRequest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.middlewares import DatabaseMiddleware
from bot.services.container import ServiceContainer

logger = logging.getLogger(__name__)

free_join_router = Router(name="free_join")
free_join_router.chat_join_request.middleware(DatabaseMiddleware())


@free_join_router.chat_join_request(F.chat.type.in_({"channel", "supergroup"}))
async def handle_free_join_request(
    join_request: ChatJoinRequest,
    session: AsyncSession
):
    """
    Handler para ChatJoinRequest del canal Free.

    Valida canal, verifica duplicados, registra solicitud y envía notificación.

    Args:
        join_request: Solicitud de unión al canal
        session: Sesión de base de datos (inyectada por middleware)
    """
    user_id = join_request.from_user.id
    user_name = join_request.from_user.first_name or "Usuario"
    from_chat_id = str(join_request.chat.id)
    channel_name = join_request.chat.title or "Canal Free"

    logger.info(f"📺 ChatJoinRequest: User={user_id} | Chat={from_chat_id}")

    container = ServiceContainer(session, join_request.bot)

    # Verificar canal configurado
    configured_channel_id = await container.channel.get_free_channel_id()

    if not configured_channel_id:
        logger.warning("⚠️ Canal Free no configurado")
        try:
            await join_request.decline()
        except Exception as e:
            logger.error(f"❌ Error declinando (canal no configurado): {e}")
        return

    # Verificar canal correcto (SEGURIDAD)
    if configured_channel_id != from_chat_id:
        logger.warning(
            f"⚠️ Solicitud desde canal no autorizado: {from_chat_id} "
            f"(esperado: {configured_channel_id})"
        )
        try:
            await join_request.decline()
        except Exception as e:
            logger.error(f"❌ Error declinando (canal no autorizado): {e}")
        return

    # Los middlewares globales se encargan de:
    # - Typing indicator (TypingIndicatorMiddleware)
    # - Auto-reacción con ❤️ (AutoReactionMiddleware)

    # Crear solicitud (verifica duplicados internamente)
    success, message, request = await container.subscription.create_free_request_from_join_request(
        user_id=user_id,
        from_chat_id=from_chat_id
    )

    if not success:
        # Solicitud duplicada
        logger.info(f"⚠️ Solicitud duplicada: user {user_id}")

        # Declinar
        try:
            await join_request.decline()
        except Exception as e:
            logger.error(f"❌ Error declinando duplicada: {e}")

        # Notificar tiempo restante con progreso visual
        if request:
            from bot.utils.formatters import format_progress_with_time

            wait_time = await container.config.get_wait_time()
            minutes_since = request.minutes_since_request()
            minutes_remaining = max(0, wait_time - minutes_since)

            # Generar barra de progreso
            progress_bar = format_progress_with_time(minutes_remaining, wait_time, length=15)

            try:
                await join_request.bot.send_message(
                    chat_id=user_id,
                    text=(
                        f"<b>🎭 Lucien:</b>\n\n"
                        f"Ah, {user_name}... veo que eres de los impacientes.\n\n"
                        f"Diana adora cuando la gente repite acciones como si eso "
                        f"hiciera que las cosas pasen más rápido. Es adorable, realmente.\n\n"
                        f"Tu solicitud sigue activa. No necesitas insistir:\n\n"
                        f"{progress_bar}\n\n"
                        f"⏰ <b>Tu situación actual:</b>\n"
                        f"• Tiempo transcurrido: {minutes_since} minutos\n"
                        f"• Tiempo restante: {minutes_remaining} minutos\n\n"
                        f"Entre {minutes_remaining} minutos recibirás acceso. "
                        f"Mientras tanto, podrías intentar... ¿cómo se dice? "
                        f"<i>Paciencia</i>. Es una virtud, dicen.\n\n"
                        f"Yo estaré aquí esperando. Siempre estoy aquí."
                    ),
                    parse_mode="HTML"
                )

                logger.info(f"✅ Notificación duplicada enviada a user {user_id} con progreso visual")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo notificar duplicada a user {user_id}: {e}")

        return

    # Solicitud nueva creada exitosamente
    logger.info(f"✅ Nueva solicitud Free registrada: user {user_id}")

    # Obtener tiempo de espera
    wait_time = await container.config.get_wait_time()

    # Enviar notificación con voz de Lucien
    try:
        await join_request.bot.send_message(
            chat_id=user_id,
            text=(
                f"<b>🎭 Lucien:</b>\n\n"
                f"Ahh, {user_name}... otro viajero buscando cruzar el umbral.\n\n"
                f"Soy Lucien, mayordomo digital y guardián de las puertas. "
                f"Veo que has solicitado acceso al canal de Diana.\n\n"
                f"Ahora... debo explicarte cómo funcionan las cosas aquí. "
                f"No es tan simple como tocar y entrar. Diana valora la "
                f"<i>anticipación</i>. Y yo... bueno, yo valoro no tener "
                f"que explicar lo obvio múltiples veces.\n\n"
                f"<b>⏳ Tu situación:</b>\n"
                f"• Tu solicitud está en la cola\n"
                f"• Tiempo de espera: <b>{wait_time} minutos</b>\n"
                f"• Aprobación: Automática (yo no decido, Diana no decide, "
                f"el sistema simplemente... <i>hace</i>)\n\n"
                f"En {wait_time} minutos recibirás acceso. "
                f"Hasta entonces, te sugiero encontrar algo productivo que hacer. "
                f"Contar ovejas, quizás. Observar pintura secarse. "
                f"Cualquier cosa que no involucre solicitar de nuevo.\n\n"
                f"<i>La paciencia, mi querido {user_name}, es el primer "
                f"paso de este viaje. Apréndela bien.</i>"
            ),
            parse_mode="HTML"
        )

        logger.info(
            f"✅ Usuario {user_id} notificado | "
            f"Aprobación automática en {wait_time} min"
        )
    except Exception as e:
        logger.warning(
            f"⚠️ No se pudo notificar a user {user_id}, pero solicitud registrada: {e}"
        )
