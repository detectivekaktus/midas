#!/usr/bin/env python3
from sys import stdout
from sqlalchemy import text
from src.db import engine
import src.db.seeds.currencies as currencies
import src.db.seeds.transaction_types as transaction_types


def truncate_table(tablename: str) -> None:
    """
    Truncates table `tablename`. Truncating means deleting all rows in the
    table and resetting the serial type of column back to 1.

    Args:
        tablename (str): SQL table name.
    """
    with engine.connect() as con:
        if not tablename.isidentifier():
            raise ValueError(f"Invalid table name: {tablename}")

        con.execute(text(f"TRUNCATE TABLE {tablename} RESTART IDENTITY CASCADE"))
        con.commit()


def main() -> None:
    print("Truncating tables...", file=stdout)
    for name in (currencies.TABLENAME, transaction_types.TABLENAME):
        truncate_table(name)

    print("Started seeding...", file=stdout)
    currencies.seed()
    transaction_types.seed()
    print("Finished seeding...", file=stdout)


if __name__ == "__main__":
    main()
