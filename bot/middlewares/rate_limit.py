"""
Middleware de Rate Limiting.

Previene spam y abuso limitando acciones por usuario por minuto.
"""

import logging
import time
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware para limitar la cantidad de acciones por usuario.

    Límite por defecto: 30 acciones por minuto.
    Si se excede, la acción es ignorada silenciosamente.
    """

    def __init__(
        self,
        rate_limit: int = 30,
        window_seconds: int = 60,
        warning_threshold: int = 25
    ):
        """
        Inicializa el middleware.

        Args:
            rate_limit: Máximo de acciones permitidas en la ventana
            window_seconds: Tamaño de la ventana en segundos
            warning_threshold: Umbral para emitir warning
        """
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        self.warning_threshold = warning_threshold
        self.user_actions: Dict[int, list] = defaultdict(list)

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        """Procesa el evento y aplica rate limiting."""
        # Obtener user_id del evento
        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id is None:
            # Sin user_id, permitir
            return await handler(event, data)

        now = time.time()

        # Limpiar acciones antiguas (fuera de la ventana)
        self.user_actions[user_id] = [
            timestamp for timestamp in self.user_actions[user_id]
            if now - timestamp < self.window_seconds
        ]

        action_count = len(self.user_actions[user_id])

        # Verificar límite
        if action_count >= self.rate_limit:
            logger.warning(
                f"Rate limit exceeded for user {user_id}: "
                f"{action_count}/{self.rate_limit} actions in {self.window_seconds}s"
            )
            # Silenciosamente ignorar el evento
            if isinstance(event, CallbackQuery):
                await event.answer("Demasiadas acciones. Espere un momento.", show_alert=True)
            return None

        # Advertir si se acerca al límite
        if action_count >= self.warning_threshold:
            logger.debug(
                f"User {user_id} approaching rate limit: "
                f"{action_count}/{self.rate_limit}"
            )

        # Registrar esta acción
        self.user_actions[user_id].append(now)

        return await handler(event, data)

    def get_remaining_actions(self, user_id: int) -> int:
        """Obtiene acciones restantes para un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Cantidad de acciones restantes
        """
        now = time.time()

        # Limpiar antiguas
        self.user_actions[user_id] = [
            t for t in self.user_actions[user_id]
            if now - t < self.window_seconds
        ]

        return max(0, self.rate_limit - len(self.user_actions[user_id]))

    def reset_user(self, user_id: int) -> None:
        """Resetea el contador de un usuario (para admins).

        Args:
            user_id: ID del usuario
        """
        if user_id in self.user_actions:
            del self.user_actions[user_id]
            logger.info(f"Rate limit reset for user {user_id}")


# Instancia global para uso en la aplicación
rate_limiter = RateLimitMiddleware()
