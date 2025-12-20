from decimal import Decimal
from pytest import fixture, mark, raises
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.schemas.account import Account
from src.db.schemas.storage import Storage
from src.query.account import AccountRepository
from src.usecase.transaction import EditTransactionUsecase
from src.util.enums import Currency, TransactionType


@fixture
def test_edit_transaction(test_engine) -> EditTransactionUsecase:
    session = AsyncSession(test_engine)
    usecase = EditTransactionUsecase(session=session)
    return usecase


@mark.asyncio
async def test_add_one_transaction_and_edit_it(
    test_engine,
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_edit_transaction,
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transaction_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.INCOME,
        "title": "Income transaction",
        "amount": Decimal("100"),
    }
    await test_create_transaction.execute(**transaction_data)

    old_transaction = (await test_get_transactions.execute(user_id))[0]
    await test_edit_transaction.execute(
        old_transaction.id, description="December 2025", amount=Decimal("1000")
    )
    new_transaction = (await test_get_transactions.execute(user_id))[0]

    assert old_transaction.id == new_transaction.id
    assert old_transaction.transaction_type_id == new_transaction.transaction_type_id
    assert old_transaction.title == new_transaction.title
    assert old_transaction.amount == Decimal(
        "100"
    ) and new_transaction.amount == Decimal("1000")
    assert (
        old_transaction.description is None
        and new_transaction.description == "December 2025"
    )

    session = AsyncSession(test_engine)
    account_repo = AccountRepository(session=session)
    async with session:
        income_account = await account_repo.get_user_account_by_transaction_type(
            user_id, TransactionType.INCOME, eager=True
        )

        assert income_account is not None
        assert income_account.debit_amount == Decimal("1000")
        assert income_account.credit_amount == Decimal()

        storage: Storage = income_account.storage
        assert storage is not None
        assert storage.amount == Decimal("1000")


@mark.asyncio
async def test_edit_income_and_expense(
    test_engine,
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_edit_transaction,
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transaction_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.INCOME,
        "title": "Income transaction",
        "amount": Decimal("100"),
    }
    await test_create_transaction.execute(**transaction_data)

    old_transaction = (await test_get_transactions.execute(user_id))[0]
    await test_edit_transaction.execute(
        old_transaction.id, description="December 2025", amount=Decimal("1000")
    )
    new_transaction = (await test_get_transactions.execute(user_id))[0]

    assert old_transaction.id == new_transaction.id
    assert old_transaction.transaction_type_id == new_transaction.transaction_type_id
    assert old_transaction.title == new_transaction.title
    assert old_transaction.amount == Decimal(
        "100"
    ) and new_transaction.amount == Decimal("1000")
    assert (
        old_transaction.description is None
        and new_transaction.description == "December 2025"
    )

    session = AsyncSession(test_engine)
    account_repo = AccountRepository(session=session)
    async with session:
        income_account = await account_repo.get_user_account_by_transaction_type(
            user_id, TransactionType.INCOME, eager=True
        )

        assert income_account is not None
        assert income_account.debit_amount == Decimal("1000")
        assert income_account.credit_amount == Decimal()

        storage: Storage = income_account.storage
        assert storage is not None
        assert storage.amount == Decimal("1000")

    transaction_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.ENTERTAINMENT,
        "title": "Entertainment transaction",
        "amount": Decimal("100"),
    }
    await test_create_transaction.execute(**transaction_data)

    old_transaction = (await test_get_transactions.execute(user_id))[0]
    await test_edit_transaction.execute(
        old_transaction.id, description="", amount=Decimal("250")
    )
    new_transaction = (await test_get_transactions.execute(user_id))[0]

    assert old_transaction.id == new_transaction.id
    assert old_transaction.transaction_type_id == new_transaction.transaction_type_id
    assert old_transaction.title == new_transaction.title
    assert old_transaction.amount == Decimal(
        "100"
    ) and new_transaction.amount == Decimal("250")
    assert old_transaction.description is None and new_transaction.description == ""

    async with session:
        income_account = await account_repo.get_user_account_by_transaction_type(
            user_id, TransactionType.INCOME, eager=True
        )

        assert income_account is not None
        assert income_account.debit_amount == Decimal("1000")
        assert income_account.credit_amount == Decimal("250")

        storage: Storage = income_account.storage
        assert storage is not None
        assert storage.amount == Decimal("750")


@mark.asyncio
async def test_pass_no_arguments(
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_edit_transaction,
) -> None:
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transaction_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.INCOME,
        "title": "Income transaction",
        "amount": Decimal("100"),
    }
    await test_create_transaction.execute(**transaction_data)

    transaction = (await test_get_transactions.execute(user_id))[0]

    with raises(ValueError):
        await test_edit_transaction.execute(transaction.id)


@mark.asyncio
async def test_pass_same_arguments(
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_edit_transaction,
) -> None:
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transaction_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.INCOME,
        "title": "Income transaction",
        "amount": Decimal("100"),
    }
    await test_create_transaction.execute(**transaction_data)

    transaction = (await test_get_transactions.execute(user_id))[0]

    with raises(ValueError):
        await test_edit_transaction.execute(
            transaction.id,
            transaction.transaction_type_id,
            transaction.title,
            transaction.amount,
            transaction.description,
        )


@mark.asyncio
async def test_change_income_to_expense(
    test_engine,
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_edit_transaction,
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transaction_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.INCOME,
        "title": "Income transaction",
        "amount": Decimal("100"),
    }
    await test_create_transaction.execute(**transaction_data)

    old_transaction = (await test_get_transactions.execute(user_id))[0]
    await test_edit_transaction.execute(
        old_transaction.id, transaction_type=TransactionType.ENTERTAINMENT
    )
    new_transaction = (await test_get_transactions.execute(user_id))[0]

    assert old_transaction.id == new_transaction.id
    assert (
        old_transaction.transaction_type_id == TransactionType.INCOME
        and new_transaction.transaction_type_id == TransactionType.ENTERTAINMENT
    )
    assert old_transaction.title == new_transaction.title
    assert old_transaction.amount == new_transaction.amount
    assert old_transaction.description == new_transaction.description

    session = AsyncSession(test_engine)
    account_repo = AccountRepository(session=session)
    async with session:
        income_account: Account = (
            await account_repo.get_user_account_by_transaction_type(
                user_id, TransactionType.INCOME, eager=True
            )
        )  # type: ignore
        entertainment_account: Account = (
            await account_repo.get_user_account_by_transaction_type(
                user_id, TransactionType.ENTERTAINMENT, eager=True
            )
        )  # type: ignore

        assert old_transaction.debit_account_id == income_account.id
        assert old_transaction.credit_account_id is None

        assert new_transaction.debit_account_id == entertainment_account.id
        assert new_transaction.credit_account_id == income_account.id

        storage: Storage = income_account.storage
        assert storage.amount == Decimal("-100")


@mark.asyncio
async def test_change_expense_to_expense(
    test_engine,
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_edit_transaction,
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transaction_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.ENTERTAINMENT,
        "title": "Transaction #1",
        "amount": Decimal("100"),
    }
    await test_create_transaction.execute(**transaction_data)

    old_transaction = (await test_get_transactions.execute(user_id))[0]
    await test_edit_transaction.execute(
        old_transaction.id, transaction_type=TransactionType.GROCERIES
    )
    new_transaction = (await test_get_transactions.execute(user_id))[0]

    assert old_transaction.id == new_transaction.id
    assert (
        old_transaction.transaction_type_id == TransactionType.ENTERTAINMENT
        and new_transaction.transaction_type_id == TransactionType.GROCERIES
    )
    assert old_transaction.title == new_transaction.title
    assert old_transaction.amount == new_transaction.amount
    assert old_transaction.description == new_transaction.description

    session = AsyncSession(test_engine)
    account_repo = AccountRepository(session=session)
    async with session:
        income_account: Account = (
            await account_repo.get_user_account_by_transaction_type(
                user_id, TransactionType.INCOME, eager=True
            )
        )  # type: ignore
        entertainment_account: Account = (
            await account_repo.get_user_account_by_transaction_type(
                user_id, TransactionType.ENTERTAINMENT, eager=True
            )
        )  # type: ignore
        groceries_account: Account = (
            await account_repo.get_user_account_by_transaction_type(
                user_id, TransactionType.GROCERIES, eager=True
            )
        )  # type: ignore

        assert old_transaction.debit_account_id == entertainment_account.id
        assert old_transaction.credit_account_id == income_account.id

        assert new_transaction.debit_account_id == groceries_account.id
        assert new_transaction.credit_account_id == income_account.id

        storage: Storage = income_account.storage
        assert storage.amount == Decimal("-100")


@mark.asyncio
async def test_change_expense_to_income(
    test_engine,
    test_register_usecase,
    test_create_transaction,
    test_get_transactions,
    test_edit_transaction,
):
    user_id = 123456789
    currency = Currency.EUR
    await test_register_usecase.execute(user_id, currency)

    transaction_data = {
        "user_id": user_id,
        "transaction_type": TransactionType.ENTERTAINMENT,
        "title": "Transaction #1",
        "amount": Decimal("100"),
    }
    await test_create_transaction.execute(**transaction_data)

    old_transaction = (await test_get_transactions.execute(user_id))[0]
    await test_edit_transaction.execute(
        old_transaction.id, transaction_type=TransactionType.INCOME
    )
    new_transaction = (await test_get_transactions.execute(user_id))[0]

    assert old_transaction.id == new_transaction.id
    assert (
        old_transaction.transaction_type_id == TransactionType.ENTERTAINMENT
        and new_transaction.transaction_type_id == TransactionType.INCOME
    )
    assert old_transaction.title == new_transaction.title
    assert old_transaction.amount == new_transaction.amount
    assert old_transaction.description == new_transaction.description

    session = AsyncSession(test_engine)
    account_repo = AccountRepository(session=session)
    async with session:
        income_account: Account = (
            await account_repo.get_user_account_by_transaction_type(
                user_id, TransactionType.INCOME, eager=True
            )
        )  # type: ignore
        entertainment_account: Account = (
            await account_repo.get_user_account_by_transaction_type(
                user_id, TransactionType.ENTERTAINMENT, eager=True
            )
        )  # type: ignore

        assert old_transaction.debit_account_id == entertainment_account.id
        assert old_transaction.credit_account_id == income_account.id

        assert new_transaction.debit_account_id == income_account.id
        assert new_transaction.credit_account_id is None

        storage: Storage = income_account.storage
        assert storage.amount == Decimal("100")
