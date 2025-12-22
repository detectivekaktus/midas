from typing import Sequence, cast
from uuid import UUID
from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message,
    ReplyKeyboardRemove,
)

from src.loggers import aiogram_logger
from src.service.user_caching import CachedUser

from src.db.schemas.transaction import Transaction
from src.usecase.transaction import DeleteTransactionUsecase, GetTransactionsUsecase
from src.util.enums import Currency, TransactionType

from src.platform.telegram.keyboard import get_yes_no_keyboard
from src.platform.telegram.keyboard.transaction import get_transaction_type_keyboard
from src.platform.telegram.keyboard.inline.transaction import (
    Command as PaginationCommand,
    TransactionPaginationCommand,
    get_transaction_pagination_inline_keyboard,
)
from src.platform.telegram.state import FormMode
from src.platform.telegram.state.transaction import (
    TransactionForm,
    TransactionPaginationState,
)
from src.platform.telegram.validator import YesNoAnswer
from src.platform.telegram.util.menu.events import remove_menu, send_main_menu
from src.platform.telegram.util.menu.options import TransactionsMenuOption


router = Router(name=__name__)


async def get_transactions(user_id: int, count: int) -> Sequence[Transaction]:
    """
    Wrapper for `GetTransactionsUsecase.execute()` method.

    :param user_id: user's telegram id.
    :type user_id: int
    :param count: number of transactions to retrieve.
    :type count: int
    :return: user's transactions or empty list if `user_id` is invalid.
    :rtype: Sequence[Transaction]
    """
    usecase = GetTransactionsUsecase()
    transactions = await usecase.execute(user_id, count)
    return transactions


def render_transaction(transaction: Transaction, currency: Currency) -> str:
    """
    Render transaction to the end user.

    :param transaction: transaction to be rendered.
    :type transaction: Transaction
    :return: rendered transaction
    :rtype: str
    """
    type_ = TransactionType(transaction.transaction_type_id).readable()
    description = transaction.description
    creation_date = transaction.created_at.strftime("%d/%m/%Y")  # 25/12/2025

    text = (
        f"📅 {creation_date}{html.italic(" - Edited") if transaction.updated_at is not None else ""}\n"
        f"📌 {transaction.title}\n"
        f"💳 {type_}\n"
        f"📝 {description if description else html.italic("No description provided")}\n"
        f"💰 {currency.name} {transaction.amount}"
    )
    return text


async def answer_query(
    query: CallbackQuery, transaction: Transaction, currency: Currency
) -> None:
    """
    Answer callback query, render and send back transaction page.
    """
    message = query.message
    if not message or isinstance(message, InaccessibleMessage):
        aiogram_logger.warning("Couldn't find message bound to the callback query.")
        await query.answer("If you see this message, report a bug on github.")
        return

    await query.answer()
    text = render_transaction(transaction, currency)
    await message.edit_text(
        text, reply_markup=get_transaction_pagination_inline_keyboard()
    )


@router.message(Command("transactions"))
@router.message(F.text == TransactionsMenuOption.VIEW)
async def handle_transactions_command(
    message: Message, state: FSMContext, user: CachedUser
) -> None:
    aiogram_logger.info(f"Received `/transactions` command: {user.id}")

    current = 0
    max_transactions = 16
    transactions = await get_transactions(user.id, max_transactions)

    if len(transactions) == 0:
        await message.answer("Nothing to display ☹️")
        return

    await remove_menu(message, state)

    await state.update_data(
        user=user,
        transactions=transactions,
        current=current,
        max_transactions=max_transactions,
    )
    await state.set_state(TransactionPaginationState.show)

    text = render_transaction(transactions[current], Currency(user.currency_id))
    await message.answer(
        text, reply_markup=get_transaction_pagination_inline_keyboard()
    )


@router.callback_query(
    TransactionPaginationCommand.filter(F.command == PaginationCommand.NEXT),
    TransactionPaginationState.show,
)
async def handle_next_callback_query(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    user: CachedUser = data["user"]
    current: int = data["current"]
    max_transactions: int = data["max_transactions"]
    transactions: Sequence[Transaction] = data["transactions"]

    current += 1
    if len(transactions) != max_transactions and len(transactions) == current:
        await query.answer("No more transactions available.")
        return
    elif max_transactions == current:
        max_transactions *= 2
        transactions = await get_transactions(user.id, max_transactions)
        await state.update_data(
            transactions=transactions, max_transactions=max_transactions
        )
    await state.update_data(current=current)

    await answer_query(query, transactions[current], Currency(user.currency_id))


@router.callback_query(
    TransactionPaginationCommand.filter(F.command == PaginationCommand.PREV),
    TransactionPaginationState.show,
)
async def handle_prev_callback_query(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    user: CachedUser = data["user"]
    current: int = data["current"]
    transactions: Sequence[Transaction] = data["transactions"]

    if current == 0:
        await query.answer("Already at the first transaction.")
        return

    current -= 1
    await state.update_data(current=current)

    await answer_query(query, transactions[current], Currency(user.currency_id))


@router.callback_query(
    TransactionPaginationCommand.filter(F.command == PaginationCommand.DELETE),
    TransactionPaginationState.show,
)
async def handle_delete_callback_query(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TransactionPaginationState.confirm_delete)

    message = query.message
    if not message or isinstance(message, InaccessibleMessage):
        aiogram_logger.warning("Couldn't find message bound to the callback query.")
        await query.answer("If you see this message, report a bug on github.")
        return

    await query.answer()
    await message.answer(
        "⚠️ Are you sure you want to delete this transaction?",
        reply_markup=get_yes_no_keyboard(),
    )


@router.message(TransactionPaginationState.confirm_delete, F.text == YesNoAnswer.YES)
async def handle_confirm_delete_callback_query(
    message: Message, state: FSMContext
) -> None:
    data = await state.get_data()
    user: CachedUser = data["user"]
    current: int = data["current"]
    transactions: list[Transaction] = data["transactions"]
    deleted_transaction: Transaction = transactions[current]

    aiogram_logger.info(
        f"Received transaction delete command: {user.id} - {deleted_transaction.id}"
    )

    usecase = DeleteTransactionUsecase()
    await usecase.execute(cast(UUID, deleted_transaction.id))

    if len(transactions) == 1:
        await state.clear()
        await message.answer(
            text="Nothing to display ☹️", reply_markup=ReplyKeyboardRemove()
        )
        return

    transactions.pop(current)
    current -= 1 if current != 0 else 0
    await state.update_data(current=current, transactions=transactions)
    await state.set_state(TransactionPaginationState.show)
    await message.answer("👍", reply_markup=ReplyKeyboardRemove())

    text = render_transaction(transactions[current], Currency(user.currency_id))
    await message.answer(
        text, reply_markup=get_transaction_pagination_inline_keyboard()
    )


@router.message(TransactionPaginationState.confirm_delete, F.text == YesNoAnswer.NO)
async def handle_reject_delete_callback_query(
    message: Message, state: FSMContext
) -> None:
    data = await state.get_data()
    user: CachedUser = data["user"]
    current: int = data["current"]
    transactions: Sequence[Transaction] = data["transactions"]
    transaction = transactions[current]

    await state.set_state(TransactionPaginationState.show)
    await message.answer("Canceled deletion.", reply_markup=ReplyKeyboardRemove())

    text = render_transaction(transaction, Currency(user.currency_id))
    await message.answer(
        text, reply_markup=get_transaction_pagination_inline_keyboard()
    )


@router.message(TransactionPaginationState.confirm_delete)
async def handle_invalid_delete_option(message: Message) -> None:
    await message.answer(
        "Please, select a valid option.", reply_markup=get_yes_no_keyboard()
    )


@router.callback_query(
    TransactionPaginationCommand.filter(F.command == PaginationCommand.EDIT),
    TransactionPaginationState.show,
)
async def handle_edit_callback_query(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    mode: FormMode = FormMode.EDIT
    user: CachedUser = data["user"]
    transactions: Sequence[Transaction] = data["transactions"]  # type: ignore
    current: int = data["current"]
    transaction: Transaction = transactions[current]

    aiogram_logger.info(
        f"Received transaction edit command: {user.id} - {transaction.id}"
    )
    await state.clear()

    await state.set_state(TransactionForm.transaction_type)
    await state.update_data(user_id=user.id, mode=mode, transaction=transaction)

    message = query.message
    if not message or isinstance(message, InaccessibleMessage):
        aiogram_logger.warning("Couldn't find message bound to the callback query.")
        await query.answer("If you see this message, report a bug on github.")
        return

    transaction_type: str = TransactionType(transaction.transaction_type_id).readable()
    await query.answer()
    await message.answer(
        f"What's the new transaction type? (current: {transaction_type})",
        reply_markup=get_transaction_type_keyboard(skippable=True),
    )
    # see form_handler.py handlers


@router.callback_query(
    TransactionPaginationCommand.filter(F.command == PaginationCommand.EXIT),
    TransactionPaginationState.show,
)
async def handle_exit_callback_query(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.answer()

    message = query.message
    if not message or isinstance(message, InaccessibleMessage):
        aiogram_logger.warning("Couldn't find message bound to the callback query.")
        return

    await send_main_menu(message, state, "👍")
