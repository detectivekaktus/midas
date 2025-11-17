from typing import AsyncGenerator
from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.db import Base


@fixture
async def test_engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        yield engine
        await conn.run_sync(Base.metadata.drop_all)
