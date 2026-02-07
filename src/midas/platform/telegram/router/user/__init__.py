from aiogram import Router
from .form_handler import router as registration
from .deletion_handler import router as deletion

router = Router(name=__name__)
router.include_routers(registration, deletion)

__all__ = ("router",)
