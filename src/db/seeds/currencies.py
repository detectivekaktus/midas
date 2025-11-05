#!/usr/bin/env python3
from json import loads
from sqlalchemy.orm import Session
from src.db import engine
from src.db.schemas.currency import Currency


def seed() -> None:
    with open("src/db/seeds/data/currencies.json", "r") as f:
        content = f.read()
        seed_currencies: list[dict[str, str]] = loads(content)

    with Session(engine) as session:
        currencies = [
            Currency(name=cur["name"], code=cur["code"], symbol=cur["symbol"])
            for cur in seed_currencies
        ]
        session.add_all(currencies)
        session.commit()


TABLENAME = "currencies"
