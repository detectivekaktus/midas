#!/usr/bin/env python3
from os import getenv
from sys import stderr
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
_POSTGRES_USER: Optional[str] = getenv("POSTGRES_USER")
_POSTGRES_PASSWORD: Optional[str] = getenv("POSTGRES_PASSWORD")
_POSTGRES_DB: Optional[str] = getenv("POSTGRES_DB")
_POSTGRES_HOST: Optional[str] = getenv("POSTGRES_HOST")

if not all((_POSTGRES_USER, _POSTGRES_PASSWORD, _POSTGRES_DB, _POSTGRES_HOST)):
    print("FATAL: PostgreSQL is not set up correctly. At least one of (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB or POSTGRES_HOST) environmental variables is missing.", file=stderr)
    print("Finishing job...", file=stderr)
    exit(1)

# https://docs.sqlalchemy.org/en/20/tutorial/engine.html#tutorial-engine
engine = create_engine(f"postgresql+psycopg2://{_POSTGRES_USER}:{_POSTGRES_PASSWORD}@{_POSTGRES_HOST}:5432/{_POSTGRES_DB}", echo=True)


# https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#establishing-a-declarative-base
class Base(DeclarativeBase):
    pass


__all__ = ["engine", "Base"]