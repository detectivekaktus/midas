from random import choice, randrange
from pytest import mark
from sqlalchemy.ext.asyncio import AsyncSession

from midas.util.enums import Currency


@mark.asyncio
async def test_register_and_get_back(
    test_register_usecase, test_get_usecase, test_engine
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    user = await test_get_usecase.execute(user_id)
    session = AsyncSession(test_engine)
    async with session:
        session.add(user)

        assert user is not None
        assert user.id == user_id
        assert user.currency_id == currency


@mark.asyncio
async def test_register_multiple_and_get_back(
    test_register_usecase, test_get_usecase, test_engine
):
    user_data = [
        {"user_id": randrange(100000000, 999999999), "currency": choice(list(Currency))}
        for _ in range(5)
    ]

    session = AsyncSession(test_engine)
    async with session:
        for data in user_data:
            await test_register_usecase.execute(data["user_id"], data["currency"])
            user = await test_get_usecase.execute(data["user_id"])
            session.add(user)

            assert user is not None
            assert user.id == data["user_id"]
            assert user.currency_id == data["currency"]


@mark.asyncio
async def test_get_unknown_user(test_get_usecase):
    user = await test_get_usecase.execute(1)
    assert user is None
