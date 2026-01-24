from aiogram import Dispatcher

from .router import router as global_router
from .router.user import router as user_router
from .router.transaction import router as transaction_router
from .router.event import router as event_router
from .router.menu import router as menu_router
from .middleware import AuthMiddleware

# Global dispatcher (Router) object.
# Attach new routers to it as needed.
dp = Dispatcher()

for middleware in [AuthMiddleware()]:
    dp.message.middleware(middleware)

# turns out the order of routers matters, so menu router is the last one to be
# triggered, so it doesn't steal events from other routers
dp.include_routers(
    global_router, user_router, transaction_router, event_router, menu_router
)
