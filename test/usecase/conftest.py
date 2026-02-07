from pytest import fixture
from sqlalchemy.ext.asyncio import AsyncSession

from midas.usecase.event import CreateEventUsecase
from midas.usecase.transaction import CreateTransactionUsecase
from midas.usecase.user import RegisterUserUsecase, GetUserUsecase


@fixture
def test_register_usecase(test_engine) -> RegisterUserUsecase:
    session = AsyncSession(test_engine)
    usecase = RegisterUserUsecase(session=session)
    return usecase


@fixture
def test_get_usecase(test_engine) -> GetUserUsecase:
    session = AsyncSession(test_engine)
    usecase = GetUserUsecase(session=session)
    return usecase


@fixture
def test_create_transaction(test_engine) -> CreateTransactionUsecase:
    session = AsyncSession(test_engine)
    usecase = CreateTransactionUsecase(session=session)
    return usecase


@fixture
def test_create_event(test_engine) -> CreateEventUsecase:
    session = AsyncSession(test_engine)
    usecase = CreateEventUsecase(session=session)
    return usecase
