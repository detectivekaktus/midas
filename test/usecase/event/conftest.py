from pytest import fixture
from sqlalchemy.ext.asyncio import AsyncSession

from midas.usecase.event import GetEventsUsecase


@fixture
def test_get_events(test_engine) -> GetEventsUsecase:
    session = AsyncSession(test_engine)
    usecase = GetEventsUsecase(session=session)
    return usecase
