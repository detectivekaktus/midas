from decimal import Decimal
from pytest import mark

from midas.util.enums import Currency, EventFrequency, TransactionType


@mark.asyncio
async def test_create_event_and_get_it_back(
    test_register_usecase, test_create_event, test_get_events
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    event_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.BILLS_AND_FEES,
        "title": "Monthly rent",
        "amount": Decimal(400),
        "frequency": EventFrequency.MONTHLY,
    }
    await test_create_event.execute(**event_data)

    events = await test_get_events.execute(user_id)
    assert len(events) == 1

    event = events[0]
    assert event is not None
    assert event.user_id == event_data["user_id"]
    assert event.transaction_type_id == event_data["transaction_type"]
    assert event.title == event_data["title"]
    assert event.amount == event_data["amount"]
    assert event.interval == event_data["frequency"]
    assert event.description is None


@mark.asyncio
async def test_get_many_events(
    test_register_usecase, test_create_event, test_get_events
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

    for i, event in enumerate(events):
        assert event.user_id == event_data[i]["user_id"]
        assert event.transaction_type_id == event_data[i]["transaction_type"]
        assert event.title == event_data[i]["title"]
        assert event.amount == event_data[i]["amount"]
        assert event.interval == event_data[i]["frequency"]
        assert event.description == event_data[i].get("description", None)


@mark.asyncio
async def test_get_events_of_invalid_user(test_get_events):
    events = await test_get_events.execute(69420)
    assert len(events) == 0
