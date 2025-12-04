from aiogram import Router
from .creation_handler import router as creation_router
from .transaction_pagination import router as pagination_router

router = Router(name=__name__)
router.include_routers(creation_router, pagination_router)

__all__ = ("router",)
