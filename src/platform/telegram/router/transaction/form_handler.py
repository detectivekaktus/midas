from decimal import Decimal
from typing import Any, Optional
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.loggers import aiogram_logger

from src.db.schemas.user import User
from src.usecase.transaction import CreateTransactionUsecase
from src.util.enums import TransactionType

from src.platform.telegram.keyboard import get_skip_keyboard
from src.platform.telegram.keyboard.transaction import get_transaction_type_keyboard
from src.platform.telegram.state import FormMode
from src.platform.telegram.state.transaction import TransactionForm
from src.platform.telegram.validator import SkipAnswer, amount_filter
from src.platform.telegram.validator.transaction import valid_transaction_type_filter


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
    if mode == "create" and (injected is None or message.text == SkipAnswer.SKIP):
        await message.answer("You can't skip this option.", reply_markup=reply_markup)
        return True

    return False


@router.message(Command("add_transaction"))
async def handle_add_transaction_command(
    message: Message, state: FSMContext, user: User
) -> None:
    aiogram_logger.info(f"Received `/add_transaction` command: {user.id}")

    mode: FormMode = "create"
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

    if mode == "create":
        await state.update_data(transaction_type=transaction_type)
        await message.answer(
            "Enter the transaction title.", reply_markup=ReplyKeyboardRemove()
        )
    else:
        ...

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

    if mode == "create":
        await state.update_data(title=message.text)
        await message.answer(
            "Optional: add a description.", reply_markup=get_skip_keyboard()
        )
    else:
        ...

    await state.set_state(TransactionForm.description)


@router.message(TransactionForm.title, F.text.len() > 64)
async def handle_invalid_title(message: Message) -> None:
    await message.answer("The title must be at most 64 characters.")


@router.message(TransactionForm.description, F.text.len() <= 256)
async def handle_valid_description(message: Message, state: FSMContext) -> None:
    mode: FormMode = await state.get_value("mode")  # type: ignore

    if message.text != SkipAnswer.SKIP:
        await state.update_data(description=message.text)

    if mode == "create":
        await message.answer(
            "Enter the transaction amount.", reply_markup=ReplyKeyboardRemove()
        )
    else:
        ...

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

    if mode == "create":
        await state.update_data(amount=amount)
        data = {k: v for k, v in (await state.get_data()).items() if k not in ("mode")}

        aiogram_logger.info(f"Confirm transaction creation: {data.get("user_id")}")

        try:
            usecase = CreateTransactionUsecase()
            await usecase.execute(**data)
            await message.answer("👍")
        except Exception as e:
            # Should be unreachable.
            aiogram_logger.error(f"Transaction creation failed: {data}")
            aiogram_logger.error(
                f"The problem to this was the following exception:\n{e}"
            )
            await message.answer("Failed. An error has occured.")
    else:
        ...

    await state.clear()


@router.message(TransactionForm.amount)
async def handle_invalid_amount(message: Message) -> None:
    await message.answer("Please, enter a valid amount. Use a dot for decimal numbers.")
