from pytest import fixture, mark, raises
from sqlalchemy.ext.asyncio import AsyncSession

from midas.usecase.user import EditUserUsecase
from midas.util.enums import Currency
from midas.util.errors import NoChangesDetectedException


@fixture
def test_edit_user(test_engine) -> EditUserUsecase:
    session = AsyncSession(test_engine)
    usecase = EditUserUsecase(session=session)
    return usecase


@mark.asyncio
async def test_register_user_and_change_their_currency(
    test_register_usecase, test_get_usecase, test_edit_user
):
    user_id = 123456789
    currency = Currency.EUR

    await test_register_usecase.execute(user_id, currency)
    old_user = await test_get_usecase.execute(user_id)

    await test_edit_user.execute(user_id, Currency.USD)
    new_user = await test_get_usecase.execute(user_id)

    assert old_user.id == new_user.id
    assert old_user.currency_id == Currency.EUR
    assert new_user.currency_id == Currency.USD


@mark.asyncio
async def test_change_invalid_user(test_edit_user):
    with raises(ValueError):
        await test_edit_user.execute(69420, Currency.UAH)


@mark.asyncio
async def test_change_nothing(test_register_usecase, test_edit_user):
    user_id = 123456789
    currency = Currency.EUR

    await test_register_usecase.execute(user_id, currency)
    with raises(NoChangesDetectedException):
        await test_edit_user.execute(user_id, Currency.EUR)
