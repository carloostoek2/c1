"""
Middleware de tracking de comportamiento para detección de arquetipos.

Este middleware registra automáticamente las interacciones del usuario
para construir su perfil de comportamiento sin modificar cada handler.
"""

import logging
import time
from datetime import datetime, UTC, timedelta
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from bot.database import get_session
from bot.database.enums import InteractionType
from bot.database.models import User
from bot.gamification.services.behavior_tracking import BehaviorTrackingService
from bot.gamification.utils.emotional_words import has_emotional_content

logger = logging.getLogger(__name__)

# Días de inactividad para considerar "return after inactivity"
INACTIVITY_THRESHOLD_DAYS = 3


class BehaviorTrackingMiddleware(BaseMiddleware):
    """
    Middleware que trackea automáticamente interacciones del usuario.

    Registra:
    - SESSION_START: Cuando usuario inicia conversación
    - RETURN_AFTER_INACTIVITY: Cuando vuelve después de 3+ días
    - BUTTON_CLICK: Cuando presiona un botón (callback)
    - TEXT_RESPONSE: Cuando envía mensaje de texto
    - MENU_NAVIGATION: Cuando navega por menús

    Usage:
        router.message.middleware(BehaviorTrackingMiddleware())
        router.callback_query.middleware(BehaviorTrackingMiddleware())
    """

    def __init__(self):
        """Inicializa el middleware."""
        super().__init__()
        self._last_message_time: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Procesa el evento y registra la interacción.

        Args:
            handler: Handler del evento
            event: Evento de Telegram
            data: Datos del contexto

        Returns:
            Resultado del handler
        """
        user = self._get_user_from_event(event)
        if not user:
            return await handler(event, data)

        user_id = user.id
        start_time = time.time()

        try:
            # Registrar interacción ANTES del handler
            await self._track_pre_handler(event, user_id, data)

            # Ejecutar handler
            result = await handler(event, data)

            # Registrar tiempo de procesamiento
            elapsed = time.time() - start_time
            self._last_message_time[user_id] = start_time

            return result

        except Exception as e:
            logger.debug(f"Error in behavior tracking: {e}")
            # No interrumpir el flujo por errores de tracking
            return await handler(event, data)

    def _get_user_from_event(self, event: TelegramObject) -> Optional[Any]:
        """Extrae el usuario del evento."""
        if isinstance(event, Message):
            return event.from_user
        elif isinstance(event, CallbackQuery):
            return event.from_user
        return None

    async def _track_pre_handler(
        self,
        event: TelegramObject,
        user_id: int,
        data: Dict[str, Any]
    ) -> None:
        """
        Trackea la interacción antes del handler.

        Args:
            event: Evento de Telegram
            user_id: ID del usuario
            data: Datos del contexto
        """
        try:
            async with get_session() as session:
                service = BehaviorTrackingService(session)

                # Verificar si es retorno después de inactividad
                await self._check_return_after_inactivity(
                    session, service, user_id
                )

                # Trackear según tipo de evento
                if isinstance(event, Message):
                    await self._track_message(service, event, user_id)
                elif isinstance(event, CallbackQuery):
                    await self._track_callback(service, event, user_id)

        except Exception as e:
            logger.debug(f"Error tracking interaction: {e}")

    async def _check_return_after_inactivity(
        self,
        session,
        service: BehaviorTrackingService,
        user_id: int
    ) -> None:
        """Verifica si el usuario vuelve después de inactividad."""
        from sqlalchemy import select

        result = await session.execute(
            select(User.last_activity).where(User.user_id == user_id)
        )
        last_activity = result.scalar_one_or_none()

        if last_activity:
            days_inactive = (datetime.now(UTC) - last_activity.replace(tzinfo=UTC)).days
            if days_inactive >= INACTIVITY_THRESHOLD_DAYS:
                await service.track_interaction(
                    user_id=user_id,
                    interaction_type=InteractionType.RETURN_AFTER_INACTIVITY,
                    metadata={"days_inactive": days_inactive}
                )
                logger.debug(
                    f"User {user_id} returned after {days_inactive} days"
                )

    async def _track_message(
        self,
        service: BehaviorTrackingService,
        message: Message,
        user_id: int
    ) -> None:
        """Trackea un mensaje de texto."""
        if not message.text:
            return

        # Calcular tiempo de respuesta
        response_time = 0.0
        if user_id in self._last_message_time:
            response_time = time.time() - self._last_message_time[user_id]

        # Analizar texto
        text = message.text
        analysis = service.analyze_text_response(text)

        # Si es /start, es SESSION_START
        if text.startswith("/start"):
            await service.track_interaction(
                user_id=user_id,
                interaction_type=InteractionType.SESSION_START,
                metadata={"command": "start"}
            )
            return

        # Si es comando, es navegación de menú
        if text.startswith("/"):
            await service.track_interaction(
                user_id=user_id,
                interaction_type=InteractionType.MENU_NAVIGATION,
                metadata={"command": text.split()[0]}
            )
            return

        # Es respuesta de texto normal
        await service.track_interaction(
            user_id=user_id,
            interaction_type=InteractionType.TEXT_RESPONSE,
            metadata={
                "word_count": analysis["word_count"],
                "has_emotional_words": analysis["has_emotional_words"],
                "has_questions": analysis["has_questions"],
                "is_structured": analysis["is_structured"],
                "response_time": response_time
            }
        )

    async def _track_callback(
        self,
        service: BehaviorTrackingService,
        callback: CallbackQuery,
        user_id: int
    ) -> None:
        """Trackea un callback (click en botón)."""
        # Calcular tiempo de click
        time_to_click = 0.0
        if user_id in self._last_message_time:
            time_to_click = time.time() - self._last_message_time[user_id]

        callback_data = callback.data or ""

        # Determinar tipo de interacción basado en callback_data
        if self._is_menu_navigation(callback_data):
            await service.track_interaction(
                user_id=user_id,
                interaction_type=InteractionType.MENU_NAVIGATION,
                metadata={
                    "callback_data": callback_data,
                    "time_to_click": time_to_click
                }
            )
        elif self._is_decision(callback_data):
            await service.track_interaction(
                user_id=user_id,
                interaction_type=InteractionType.DECISION_MADE,
                metadata={
                    "decision_id": callback_data,
                    "time_to_decide": time_to_click
                }
            )
        elif self._is_skip_action(callback_data):
            await service.track_interaction(
                user_id=user_id,
                interaction_type=InteractionType.SKIP_ACTION,
                metadata={"callback_data": callback_data}
            )
        else:
            await service.track_interaction(
                user_id=user_id,
                interaction_type=InteractionType.BUTTON_CLICK,
                metadata={
                    "button_id": callback_data,
                    "time_to_click": time_to_click
                }
            )

    def _is_menu_navigation(self, callback_data: str) -> bool:
        """Determina si el callback es navegación de menú."""
        menu_patterns = [
            "menu:", "nav:", "back:", "main:", "admin:",
            "vip:", "free:", "user:", "home"
        ]
        return any(callback_data.startswith(p) for p in menu_patterns)

    def _is_decision(self, callback_data: str) -> bool:
        """Determina si el callback es una decisión narrativa."""
        decision_patterns = [
            "decision:", "choice:", "narrative:", "fragment:"
        ]
        return any(callback_data.startswith(p) for p in decision_patterns)

    def _is_skip_action(self, callback_data: str) -> bool:
        """Determina si el callback es saltar/omitir."""
        skip_patterns = ["skip", "omitir", "saltar", "cancel"]
        return any(p in callback_data.lower() for p in skip_patterns)
