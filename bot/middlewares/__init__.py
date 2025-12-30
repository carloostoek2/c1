"""
Middlewares module - Procesamiento pre/post handlers.
"""
from bot.middlewares.admin_auth import AdminAuthMiddleware
from bot.middlewares.database import DatabaseMiddleware
from bot.middlewares.typing_indicator import TypingIndicatorMiddleware
from bot.middlewares.auto_reaction import AutoReactionMiddleware
from bot.middlewares.rate_limit import RateLimitMiddleware, rate_limiter
from bot.middlewares.behavior_tracking import BehaviorTrackingMiddleware

__all__ = [
    "AdminAuthMiddleware",
    "DatabaseMiddleware",
    "TypingIndicatorMiddleware",
    "AutoReactionMiddleware",
    "RateLimitMiddleware",
    "rate_limiter",
    "BehaviorTrackingMiddleware",
]
