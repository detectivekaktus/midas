from pytest import fixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.usecase.transaction import CreateTransactionUsecase


@fixture
def test_create_transaction(test_engine) -> CreateTransactionUsecase:
    session = AsyncSession(test_engine)
    usecase = CreateTransactionUsecase(session=session)
    return usecase
