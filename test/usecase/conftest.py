from pytest import fixture
from sqlalchemy.ext.asyncio import AsyncSession

from src.usecase.user import RegisterUserUsecase, GetUserUsecase


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
