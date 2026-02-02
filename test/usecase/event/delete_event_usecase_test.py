from decimal import Decimal
from pytest import fixture, mark, raises
from sqlalchemy.ext.asyncio import AsyncSession

from midas.usecase.event import DeleteEventUsecase
from midas.util.enums import Currency, EventFrequency, TransactionType


@fixture
def test_delete_event(test_engine) -> DeleteEventUsecase:
    session = AsyncSession(test_engine)
    usecase = DeleteEventUsecase(session)
    return usecase


@mark.asyncio
async def test_create_income_event_and_delete_it(
    test_register_usecase, test_create_event, test_delete_event, test_get_events
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    event_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.INCOME,
        "title": "Income transaction",
        "amount": Decimal("100"),
        "frequency": EventFrequency.MONTHLY,
    }
    await test_create_event.execute(**event_data)

    events = await test_get_events.execute(user_id)
    assert len(events) == 1

    await test_delete_event.execute(events[0].id)
    events = await test_get_events.execute(user_id)

    assert len(events) == 0


@mark.asyncio
async def test_create_expense_event_and_delete_it(
    test_register_usecase, test_create_event, test_delete_event, test_get_events
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    event_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.TRANSPORTATION,
        "title": "Bus pass",
        "amount": Decimal("69.42"),
        "frequency": EventFrequency.WEEKLY,
    }
    await test_create_event.execute(**event_data)

    events = await test_get_events.execute(user_id)
    assert len(events) == 1

    await test_delete_event.execute(events[0].id)
    events = await test_get_events.execute(user_id)

    assert len(events) == 0


@mark.asyncio
async def test_create_multiple_events_and_delete_them_all(
    test_register_usecase, test_create_event, test_delete_event, test_get_events
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    event_data = [
        {
            "user_id": user_id,
            "transaction_type": TransactionType.BILLS_AND_FEES,
            "title": "Monthly rent",
            "amount": Decimal("400"),
            "frequency": EventFrequency.MONTHLY,
        },
        {
            "user_id": user_id,
            "transaction_type": TransactionType.BILLS_AND_FEES,
            "title": "Internet bill",
            "amount": Decimal("21.99"),
            "frequency": EventFrequency.MONTHLY,
            "description": "Iliad internet bill",
        },
        {
            "user_id": user_id,
            "transaction_type": TransactionType.TRANSPORTATION,
            "title": "Trenord Pass",
            "amount": Decimal("65"),
            "frequency": EventFrequency.MONTHLY,
            "description": "IoViaggio trenord monthly pass",
        },
    ]

    for data in event_data:
        await test_create_event.execute(**data)

    events = await test_get_events.execute(user_id)
    assert len(events) == len(event_data)

    for event in events:
        await test_delete_event.execute(event.id)

    events = await test_get_events.execute(user_id)
    assert len(events) == 0


@mark.asyncio
async def test_delete_non_existing_event(test_delete_event):
    with raises(ValueError):
        await test_delete_event.execute(69420)
