from aiogram import Router

from .form_handler import router as form_router

router = Router(name=__name__)
router.include_routers(form_router)

__all__ = ("router",)
