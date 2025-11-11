from typing import Generator
from pytest import fixture, raises
from sqlalchemy import Engine, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.query.repository import Repository


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)


@fixture
def test_engine() -> Generator[Engine]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@fixture
def test_repo(test_engine) -> Repository:
    repo = Repository[User, int](User, custom_engine=test_engine)  # type: ignore
    return repo


def test_add_one_and_get_it_back(test_repo):
    with test_repo:
        user = User(name="Sponge Bob", email="spongebob@example.com")
        test_repo.add(user)

        fetched_user = test_repo.get_by_id(1)

        assert fetched_user
        assert user is fetched_user
        assert fetched_user.id == 1
        assert fetched_user.name == "Sponge Bob"
        assert fetched_user.email == "spongebob@example.com"


def test_add_one_and_get_invalid(test_repo):
    with test_repo:
        user = User(name="Sponge Bob", email="spongebob@example.com")
        test_repo.add(user)

        fetched_user = test_repo.get_by_id(2)

        assert not fetched_user
        assert fetched_user is not user


def test_add_many_and_get_first_one(test_repo):
    with test_repo:
        users = [
            User(name="Sponge Bob", email="spongebob@example.com"),
            User(name="Patrick Star", email="patrickstar@example.com"),
            User(name="Squidward Tentacles", email="squidwardtentacles@example.com"),
            User(name="Sandy Cheeks", email="sandycheeks@example.com"),
        ]
        test_repo.add_many(users)

        fetched_user = test_repo.get_by_id(1)

        assert fetched_user
        assert fetched_user.id == 1
        assert fetched_user.name == "Sponge Bob"
        assert fetched_user.email == "spongebob@example.com"


def test_add_many_and_get_last_one(test_repo):
    with test_repo:
        users = [
            User(name="Sponge Bob", email="spongebob@example.com"),
            User(name="Patrick Star", email="patrickstar@example.com"),
            User(name="Squidward Tentacles", email="squidwardtentacles@example.com"),
            User(name="Sandy Cheeks", email="sandycheeks@example.com"),
        ]
        test_repo.add_many(users)

        fetched_user = test_repo.get_by_id(4)

        assert fetched_user
        assert fetched_user.id == 4
        assert fetched_user.name == "Sandy Cheeks"
        assert fetched_user.email == "sandycheeks@example.com"


def test_add_many_and_get_all(test_repo):
    with test_repo:
        users = [
            User(name="Sponge Bob", email="spongebob@example.com"),
            User(name="Patrick Star", email="patrickstar@example.com"),
            User(name="Squidward Tentacles", email="squidwardtentacles@example.com"),
            User(name="Sandy Cheeks", email="sandycheeks@example.com"),
        ]
        test_repo.add_many(users)

        for i in range(1, 5):
            fetched_user = test_repo.get_by_id(i)
            assert fetched_user.id == users[i - 1].id
            assert fetched_user.name == users[i - 1].name
            assert fetched_user.email == users[i - 1].email


def test_add_one_and_update_one(test_repo):
    with test_repo:
        user = User(name="Sponge Bob", email="spongebob@example.com")
        test_repo.add(user)

        fetched_user = test_repo.get_by_id(1)
        fetched_user.email = "spongebob@krustykrab.com"
        test_repo.flush()

        assert fetched_user
        assert fetched_user.id == 1
        assert fetched_user.name == "Sponge Bob"
        assert fetched_user.email == "spongebob@krustykrab.com"


def test_add_many_and_update_first_one(test_repo):
    with test_repo:
        users = [
            User(name="Sponge Bob", email="spongebob@example.com"),
            User(name="Patrick Star", email="patrickstar@example.com"),
            User(name="Squidward Tentacles", email="squidwardtentacles@example.com"),
            User(name="Sandy Cheeks", email="sandycheeks@example.com"),
        ]
        test_repo.add_many(users)

        fetched_user = test_repo.get_by_id(1)
        fetched_user.email = "spongebob@krustykrab.com"
        test_repo.flush()

        assert fetched_user
        assert fetched_user.id == 1
        assert fetched_user.name == "Sponge Bob"
        assert fetched_user.email == "spongebob@krustykrab.com"


def test_add_many_and_update_last_one(test_repo):
    with test_repo:
        users = [
            User(name="Sponge Bob", email="spongebob@example.com"),
            User(name="Patrick Star", email="patrickstar@example.com"),
            User(name="Squidward Tentacles", email="squidwardtentacles@example.com"),
            User(name="Sandy Cheeks", email="sandycheeks@example.com"),
        ]
        test_repo.add_many(users)

        fetched_user = test_repo.get_by_id(4)
        fetched_user.email = "sandycheeks@mail.com"
        test_repo.flush()

        assert fetched_user
        assert fetched_user.id == 4
        assert fetched_user.name == "Sandy Cheeks"
        assert fetched_user.email == "sandycheeks@mail.com"


def test_add_one_and_delete_one(test_repo):
    with test_repo:
        user = User(name="Sponge Bob", email="spongebob@example.com")
        test_repo.add(user)

        test_repo.delete_by_id(1)
        test_repo.flush()

        fetched_user = test_repo.get_by_id(1)

        assert not fetched_user


def test_add_one_and_delete_invalid_one(test_repo):
    with test_repo:
        user = User(name="Sponge Bob", email="spongebob@example.com")
        test_repo.add(user)

        test_repo.delete_by_id(1)
        test_repo.flush()

        with raises(ValueError):
            test_repo.delete_by_id(2)


def test_add_many_and_delete_first_one(test_repo):
    with test_repo:
        users = [
            User(name="Sponge Bob", email="spongebob@example.com"),
            User(name="Patrick Star", email="patrickstar@example.com"),
            User(name="Squidward Tentacles", email="squidwardtentacles@example.com"),
            User(name="Sandy Cheeks", email="sandycheeks@example.com"),
        ]
        test_repo.add_many(users)

        test_repo.delete_by_id(1)
        test_repo.flush()
        
        fetched_user = test_repo.get_by_id(1)

        assert not fetched_user


def test_add_many_and_delete_last_one(test_repo):
    with test_repo:
        users = [
            User(name="Sponge Bob", email="spongebob@example.com"),
            User(name="Patrick Star", email="patrickstar@example.com"),
            User(name="Squidward Tentacles", email="squidwardtentacles@example.com"),
            User(name="Sandy Cheeks", email="sandycheeks@example.com"),
        ]
        test_repo.add_many(users)

        test_repo.delete_by_id(4)
        test_repo.flush()
        
        fetched_user = test_repo.get_by_id(4)

        assert not fetched_user


def test_add_many_and_delete_all(test_repo):
    with test_repo:
        users = [
            User(name="Sponge Bob", email="spongebob@example.com"),
            User(name="Patrick Star", email="patrickstar@example.com"),
            User(name="Squidward Tentacles", email="squidwardtentacles@example.com"),
            User(name="Sandy Cheeks", email="sandycheeks@example.com"),
        ]
        test_repo.add_many(users)

        for i in range(1, 5):
            test_repo.delete_by_id(i)
            test_repo.flush()
            assert not test_repo.get_by_id(i)
