"""
Handlers de administración de la Tienda.
"""

from bot.shop.handlers.admin.shop_config import shop_admin_router
from bot.shop.handlers.admin.content_admin import router as content_admin_router

__all__ = [
    "shop_admin_router",
    "content_admin_router",
]
