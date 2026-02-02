from decimal import Decimal
from pytest import fixture, mark, raises
from sqlalchemy.ext.asyncio import AsyncSession

from midas.usecase.event import EditEventUsecase
from midas.util.enums import Currency, EventFrequency, TransactionType
from midas.util.errors import NoChangesDetectedException


@fixture
def test_edit_event(test_engine) -> EditEventUsecase:
    session = AsyncSession(test_engine)
    usecase = EditEventUsecase(session=session)
    return usecase


@mark.asyncio
async def test_edit_event_description_and_amount(
    test_register_usecase,
    test_create_event,
    test_get_events,
    test_edit_event,
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    event_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.INCOME,
        "title": "Income event",
        "amount": Decimal("100"),
        "frequency": EventFrequency.DAILY,
    }
    await test_create_event.execute(**event_data)

    old_event = (await test_get_events.execute(user_id))[0]
    await test_edit_event.execute(
        old_event.id,
        description="What I would like to earn every day",
        amount=Decimal("1000"),
    )
    new_event = (await test_get_events.execute(user_id))[0]

    assert old_event.id == new_event.id
    assert old_event.transaction_type_id == new_event.transaction_type_id
    assert old_event.title == new_event.title
    assert old_event.amount == Decimal("100") and new_event.amount == Decimal("1000")
    assert (
        old_event.description is None
        and new_event.description == "What I would like to earn every day"
    )
    assert old_event.interval == new_event.interval


@mark.asyncio
async def test_edit_event_amount_and_frequency(
    test_register_usecase,
    test_create_event,
    test_get_events,
    test_edit_event,
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    event_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.ENTERTAINMENT,
        "title": "Random title",
        "amount": Decimal("100"),
        "frequency": EventFrequency.DAILY,
    }
    await test_create_event.execute(**event_data)

    old_event = (await test_get_events.execute(user_id))[0]
    await test_edit_event.execute(
        old_event.id, amount=Decimal("69"), frequency=EventFrequency.WEEKLY
    )
    new_event = (await test_get_events.execute(user_id))[0]

    assert old_event.id == new_event.id
    assert old_event.transaction_type_id == new_event.transaction_type_id
    assert old_event.title == new_event.title
    assert old_event.amount == Decimal("100") and new_event.amount == Decimal("69")
    assert old_event.description is None and new_event.description is None
    assert (
        old_event.interval == EventFrequency.DAILY
        and new_event.interval == EventFrequency.WEEKLY
    )


@mark.asyncio
async def test_pass_same_arguments(
    test_register_usecase,
    test_create_event,
    test_get_events,
    test_edit_event,
) -> None:
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

    event = (await test_get_events.execute(user_id))[0]

    with raises(NoChangesDetectedException):
        await test_edit_event.execute(
            event.id,
            event.transaction_type_id,
            event.title,
            event.amount,
            event.description,
            event.interval,
        )
