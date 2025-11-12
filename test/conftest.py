from typing import Generator
from pytest import fixture
from sqlalchemy import Engine, create_engine

from src.db import Base


@fixture
def test_engine() -> Generator[Engine]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

