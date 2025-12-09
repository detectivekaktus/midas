from aiogram import Router
from .form_handler import router as form_router
from .pagination_handler import router as pagination_router

router = Router(name=__name__)
router.include_routers(form_router, pagination_router)

__all__ = ("router",)
