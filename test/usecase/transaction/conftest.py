from pytest import fixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.usecase.transaction import CreateTransactionUsecase, GetTransactionsUsecase


@fixture
def test_create_transaction(test_engine) -> CreateTransactionUsecase:
    session = AsyncSession(test_engine)
    usecase = CreateTransactionUsecase(session=session)
    return usecase


@fixture
def test_get_transactions(test_engine) -> GetTransactionsUsecase:
    session = AsyncSession(test_engine)
    usecase = GetTransactionsUsecase(session=session)
    return usecase
