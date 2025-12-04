from typing import Sequence
from aiogram import Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.loggers import aiogram_logger

from src.usecase.transaction import GetTransactionsUsecase
from src.util.enums import TransactionType

from src.db.schemas.transaction import Transaction
from src.platform.telegram.keyboard.inline.transaction import (
    get_transaction_pagination_inline_keyboard,
)
from src.platform.telegram.state.transaction import TransactionPaginationState


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


def render_transaction(transaction: Transaction) -> str:
    """
    Render transaction to the end user.

    :param transaction: transaction to be rendered.
    :type transaction: Transaction
    :return: rendered transaction
    :rtype: str
    """
    type_ = TransactionType(transaction.transaction_type_id).readable()
    description = transaction.description
    date = transaction.created_at.strftime("%d/%m/%Y")  # 25/12/2025

    text = (
        f"📅 {date}\n"
        f"📌 {transaction.title}\n"
        f"💳 {type_}\n"
        f"📝 {description if description else html.italic("No description provided")}\n"
        f"💰 {transaction.amount}"
    )
    return text


@router.message(Command("transactions"))
async def handle_transactions_command(message: Message, state: FSMContext) -> None:
    user = message.from_user
    if not user:
        aiogram_logger.warning(
            "Received `/transactions` command but couldn't get the user"
        )
        return

    aiogram_logger.info(f"Received `/transactions` command: {user.id}")

    user_id = user.id
    current = 0
    max_transactions = 16
    transactions = await get_transactions(user_id, max_transactions)

    if len(transactions) == 0:
        message.answer("Nothing to display ☹️")
        return

    await state.update_data(user_id=user_id)
    await state.update_data(transactions=transactions)
    await state.update_data(current=current)
    await state.update_data(max_transactions=max_transactions)
    await state.set_state(TransactionPaginationState.show)

    text = render_transaction(transactions[current])
    await message.answer(
        text, reply_markup=get_transaction_pagination_inline_keyboard()
    )
