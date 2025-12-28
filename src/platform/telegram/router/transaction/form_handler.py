from decimal import Decimal
from typing import Any, Optional
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.loggers import aiogram_logger
from src.service.user_caching import CachedUser

from src.db.schemas.transaction import Transaction
from src.usecase.transaction import CreateTransactionUsecase, EditTransactionUsecase
from src.util.enums import TransactionType
from src.util.errors import NoChangesDetectedException

from src.platform.telegram.keyboard import get_skip_keyboard
from src.platform.telegram.keyboard.transaction import get_transaction_type_keyboard
from src.platform.telegram.state import FormMode
from src.platform.telegram.state.transaction import TransactionForm
from src.platform.telegram.validator import SkipAnswer, amount_filter
from src.platform.telegram.validator.transaction import valid_transaction_type_filter
from src.platform.telegram.util.menu.events import remove_menu, send_transactions_menu
from src.platform.telegram.util.menu.options import TransactionsMenuOption


router = Router(name=__name__)


async def skipped_unskippable(
    message: Message,
    mode: FormMode,
    injected: Optional[Any] = object(),
    reply_markup: Optional[ReplyKeyboardMarkup] = None,
) -> bool:
    """
    Check if user input in `create` mode is skipped or invalid
    by specifying `injected` argument.

    If this condition is met, an error message is sent to the user.

    :param message: telegram message
    :type message: Message
    :param mode: current form mode
    :type mode: FormMode
    :param injected: injected field by the filter
    :type injected: Optional[Any]
    :param reply_markup: telegram keyboard
    :type reply_markup: Optional[ReplyKeyboardMarkup]
    :return: `True` if input is valid, `False` otherwise
    :rtype: bool
    """
    if mode == FormMode.CREATE and (
        injected is None or message.text == SkipAnswer.SKIP
    ):
        await message.answer("You can't skip this option.", reply_markup=reply_markup)
        return True

    return False


async def create_transaction(message: Message, state: FSMContext) -> None:
    data = {k: v for k, v in (await state.get_data()).items() if k not in ("mode")}
    await state.clear()

    try:
        usecase = CreateTransactionUsecase()
        await usecase.execute(**data)
        await send_transactions_menu(message, state, "👍", set_state=True)
    except Exception as e:
        # Should be unreachable.
        aiogram_logger.error(f"Transaction creation failed: {data}")
        aiogram_logger.error(f"The problem to this was the following exception:\n{e}")
        await send_transactions_menu(
            message, state, "Failed. Something wrong happened.", set_state=True
        )


async def edit_transaction(message: Message, state: FSMContext) -> None:
    data = {
        k: v
        for k, v in (await state.get_data()).items()
        if k not in ("user_id", "mode", "transaction")
    }
    await state.clear()

    try:
        usecase = EditTransactionUsecase()
        await usecase.execute(**data)
        await send_transactions_menu(message, state, "👍", set_state=True)
    except NoChangesDetectedException:
        aiogram_logger.info(
            f"Transaction edit failed due to insufficient fields: {data.get("user_id")}"
        )
        await send_transactions_menu(
            message, state, "Failed. You must specify at least 1 field.", set_state=True
        )
    except Exception as e:
        aiogram_logger.error(f"Transaction edit failed: {data}")
        aiogram_logger.error(f"The problem to this was the following exception:\n{e}")
        await send_transactions_menu(
            message, state, "Failed. Something wrong happened.", set_state=True
        )


@router.message(Command("add_transaction"))
@router.message(F.text == TransactionsMenuOption.ADD)
async def handle_add_transaction_command(
    message: Message, state: FSMContext, user: CachedUser
) -> None:
    aiogram_logger.info(f"Received `/add_transaction` command: {user.id}")

    await remove_menu(message, state)

    mode = FormMode.CREATE
    await state.update_data(user_id=user.id, mode=mode)
    await state.set_state(TransactionForm.transaction_type)
    await message.answer(
        "What's the transaction type?", reply_markup=get_transaction_type_keyboard()
    )


@router.message(TransactionForm.transaction_type, valid_transaction_type_filter)
@router.message(TransactionForm.transaction_type, F.text == SkipAnswer.SKIP)
async def handle_valid_type(
    message: Message,
    state: FSMContext,
    transaction_type: Optional[TransactionType] = None,
) -> None:
    mode: FormMode = await state.get_value("mode")  # type: ignore
    if await skipped_unskippable(
        message, mode, transaction_type, get_transaction_type_keyboard()
    ):
        return

    if mode == FormMode.CREATE:
        await state.update_data(transaction_type=transaction_type)
        await message.answer(
            "Enter the transaction title.", reply_markup=ReplyKeyboardRemove()
        )
    else:
        if transaction_type is not None and message.text != SkipAnswer.SKIP:
            await state.update_data(transaction_type=transaction_type)

        transaction: Transaction = await state.get_value("transaction")  # type: ignore
        await message.answer(
            f"Enter new transaction title. (current: {transaction.title})",
            reply_markup=get_skip_keyboard(),
        )

    await state.set_state(TransactionForm.title)


@router.message(TransactionForm.transaction_type)
async def handle_invalid_type(message: Message) -> None:
    await message.answer(
        "Incorrect transaction type.", reply_markup=get_transaction_type_keyboard()
    )


@router.message(TransactionForm.title, F.text.len() <= 64)
async def handle_valid_title(message: Message, state: FSMContext) -> None:
    mode: FormMode = await state.get_value("mode")  # type: ignore
    if await skipped_unskippable(message, mode):
        return

    if mode == FormMode.CREATE:
        await state.update_data(title=message.text)
        await message.answer(
            "Optional: add a description.", reply_markup=get_skip_keyboard()
        )
    else:
        if message.text != SkipAnswer.SKIP:
            await state.update_data(title=message.text)

        transaction: Transaction = await state.get_value("transaction")  # type: ignore
        await message.answer(
            f"Add new description. (current: {transaction.description})",
            reply_markup=get_skip_keyboard(),
        )

    await state.set_state(TransactionForm.description)


@router.message(TransactionForm.title, F.text.len() > 64)
async def handle_invalid_title(message: Message) -> None:
    await message.answer("The title must be at most 64 characters.")


@router.message(TransactionForm.description, F.text.len() <= 256)
async def handle_valid_description(message: Message, state: FSMContext) -> None:
    mode: FormMode = await state.get_value("mode")  # type: ignore

    if message.text != SkipAnswer.SKIP:
        await state.update_data(description=message.text)

    if mode == FormMode.CREATE:
        await message.answer(
            "Enter the transaction amount.", reply_markup=ReplyKeyboardRemove()
        )
    else:
        transaction: Transaction = await state.get_value("transaction")  # type: ignore
        await message.answer(
            f"Enter new transaction amount. (current: {transaction.amount})",
            reply_markup=get_skip_keyboard(),
        )

    await state.set_state(TransactionForm.amount)


@router.message(TransactionForm.description, F.text.len() > 256)
async def handle_invalid_description(message: Message) -> None:
    await message.answer(
        "The description must be at most 256 characters.",
        reply_markup=get_skip_keyboard(),
    )


@router.message(TransactionForm.amount, amount_filter)
@router.message(TransactionForm.amount, F.text == SkipAnswer.SKIP)
async def handle_valid_amount(
    message: Message, state: FSMContext, amount: Optional[Decimal] = None
) -> None:
    mode: FormMode = await state.get_value("mode")  # type: ignore
    if await skipped_unskippable(message, mode, amount):
        return

    if mode == FormMode.CREATE:
        aiogram_logger.info(
            f"Confirm transaction creation: {await state.get_value("user_id")}"
        )
        await state.update_data(amount=amount)
        await create_transaction(message, state)
    else:
        aiogram_logger.info(
            f"Confirm transaction editing: {await state.get_value("user_id")}"
        )

        if amount is not None and message.text != SkipAnswer.SKIP:
            await state.update_data(amount=amount)

        transaction: Transaction = await state.get_value("transaction")  # type: ignore
        await state.update_data(id=transaction.id)

        await edit_transaction(message, state)


@router.message(TransactionForm.amount)
async def handle_invalid_amount(message: Message) -> None:
    await message.answer("Please, enter a valid amount. Use a dot for decimal numbers.")
