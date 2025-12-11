from json import loads
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import engine
from src.db.schemas.transaction_type import TransactionType


async def seed() -> None:
    with open("src/db/seeds/data/transaction_types.json", "r") as f:
        content = f.read()
        seed_types: list[dict[str, str | bool]] = loads(content)

    async with AsyncSession(engine) as session:
        types = [
            TransactionType(name=type_["name"], income=type_["income"])
            for type_ in seed_types
        ]
        session.add_all(types)
        await session.commit()


TABLENAME = "transaction_types"
