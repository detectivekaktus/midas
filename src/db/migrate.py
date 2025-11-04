#!/usr/bin/env python3
from sys import stdout
from src.db import Base, engine
from src.db.schema import *


def main() -> None:
    print("Running a migration on the database...", file=stdout)
    Base.metadata.create_all(engine)
    print("Migration successful. Exiting...", file=stdout)


if __name__ == "__main__":
    main()
