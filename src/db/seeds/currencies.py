#!/usr/bin/env python3
from json import loads
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import engine
from src.db.schemas.currency import Currency


async def seed() -> None:
    with open("src/db/seeds/data/currencies.json", "r") as f:
        content = f.read()
        seed_currencies: list[dict[str, str]] = loads(content)

    async with AsyncSession(engine) as session:
        currencies = [
            Currency(name=cur["name"], code=cur["code"], symbol=cur["symbol"])
            for cur in seed_currencies
        ]
        session.add_all(currencies)
        await session.commit()


TABLENAME = "currencies"
