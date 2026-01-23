from decimal import Decimal
from pytest import fixture, mark, raises
from sqlalchemy.ext.asyncio import AsyncSession

from midas.query.event.repository import EventRepository
from midas.usecase.event import CreateEventUsecase
from midas.util.enums import Currency, TransactionType


@fixture
def test_create_event(test_engine) -> CreateEventUsecase:
    session = AsyncSession(test_engine)
    usecase = CreateEventUsecase(session=session)
    return usecase


@mark.asyncio
async def test_create_event_without_description(
    test_engine, test_register_usecase, test_create_event
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    event_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.BILLS_AND_FEES,
        "title": "Monthly rent",
        "amount": Decimal(400),
        "update_interval": 30,
    }
    await test_create_event.execute(**event_data)

    session = AsyncSession(test_engine)
    repo = EventRepository(session)
    async with session:
        event = await repo.get_by_id(1)

        assert event is not None
        assert event.user_id == event_data["user_id"]
        assert event.transaction_type_id == event_data["transaction_type"]
        assert event.title == event_data["title"]
        assert event.amount == event_data["amount"]
        assert event.interval == event_data["update_interval"]
        assert event.description is None


@mark.asyncio
async def test_create_event_with_description(
    test_engine, test_register_usecase, test_create_event
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    event_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.BILLS_AND_FEES,
        "title": "Monthly rent",
        "amount": Decimal(400),
        "update_interval": 30,
        "description": "Made up description",
    }
    await test_create_event.execute(**event_data)

    session = AsyncSession(test_engine)
    repo = EventRepository(session)
    async with session:
        event = await repo.get_by_id(1)

        assert event is not None
        assert event.user_id == event_data["user_id"]
        assert event.transaction_type_id == event_data["transaction_type"]
        assert event.title == event_data["title"]
        assert event.amount == event_data["amount"]
        assert event.interval == event_data["update_interval"]
        assert event.description == event_data["description"]


@mark.asyncio
async def test_create_event_for_invalid_user(test_create_event):
    event_data = {
        "user_id": 69420,
        "transaction_type": TransactionType.BILLS_AND_FEES,
        "title": "Monthly rent",
        "amount": Decimal(400),
        "update_interval": 30,
        "description": "Made up description",
    }

    with raises(ValueError):
        await test_create_event.execute(**event_data)
