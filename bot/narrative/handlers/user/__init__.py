"""
Handlers de narrativa para usuarios.

Exporta los routers de interacción narrativa del usuario.
"""
from bot.narrative.handlers.user.story import story_router
from bot.narrative.handlers.user.journal import journal_router
from bot.narrative.handlers.user.challenge import challenge_router
from bot.middlewares import DatabaseMiddleware

# Aplicar middleware de database a todos los routers
story_router.message.middleware(DatabaseMiddleware())
story_router.callback_query.middleware(DatabaseMiddleware())

journal_router.message.middleware(DatabaseMiddleware())
journal_router.callback_query.middleware(DatabaseMiddleware())

challenge_router.message.middleware(DatabaseMiddleware())
challenge_router.callback_query.middleware(DatabaseMiddleware())

__all__ = ["story_router", "journal_router", "challenge_router"]
