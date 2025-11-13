from aiogram import Dispatcher

from .router import router as global_router
from .router.user import router as user_router

# Global dispatcher (Router) object.
# Attach new routers to it as needed.
dp = Dispatcher()

for router in [global_router, user_router]:
    dp.include_router(router)
