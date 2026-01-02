"""
User handlers module.
"""
# Importar router primero
from bot.handlers.user.start import user_router
from bot.handlers.user.favors import favors_router

# Importar handlers adicionales para que sus decoradores se ejecuten
# IMPORTANTE: Estos imports ejecutan los decoradores @user_router.callback_query()
import bot.handlers.user.vip_flow
import bot.handlers.user.vip_menu
import bot.handlers.user.free_join_request
import bot.handlers.user.conversion

__all__ = ["user_router", "favors_router"]
