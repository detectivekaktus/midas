#!/usr/bin/env python3
from asyncio import run
from sys import stdout
from sqlalchemy import text
from src.db import engine
import src.db.seeds.currencies as currencies
import src.db.seeds.transaction_types as transaction_types


async def truncate_table(tablename: str) -> None:
    """
    Truncates table `tablename`. Truncating means deleting all rows in the
    table and resetting the serial type of column back to 1.

    Args:
        tablename (str): SQL table name.
    """
    async with engine.connect() as con:
        if not tablename.isidentifier():
            raise ValueError(f"Invalid table name: {tablename}")

        await con.execute(text(f"TRUNCATE TABLE {tablename} RESTART IDENTITY CASCADE"))
        await con.commit()


async def do_run_main() -> None:
    print("Truncating tables...", file=stdout)
    for name in (currencies.TABLENAME, transaction_types.TABLENAME):
        await truncate_table(name)

    print("Started seeding...", file=stdout)
    await currencies.seed()
    await transaction_types.seed()
    print("Finished seeding...", file=stdout)


def main() -> None:
    run(do_run_main())


if __name__ == "__main__":
    main()
