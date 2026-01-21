from pytest import fixture
from sqlalchemy.ext.asyncio import AsyncSession

from midas.usecase.transaction import GetTransactionsUsecase


@fixture
def test_get_transactions(test_engine) -> GetTransactionsUsecase:
    session = AsyncSession(test_engine)
    usecase = GetTransactionsUsecase(session=session)
    return usecase
