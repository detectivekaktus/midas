from aiogram import Router
from .menu_handler import router as menu_router

router = Router(name=__name__)
router.include_routers(menu_router)

__all__ = ("router",)
