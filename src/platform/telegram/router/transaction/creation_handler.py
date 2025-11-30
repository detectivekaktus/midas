from decimal import Decimal
from logging import error
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from src.usecase.transaction import CreateTransactionUsecase
from src.util.enums import TransactionType

from src.platform.telegram.keyboard import get_skip_keyboard
from src.platform.telegram.keyboard.transaction import get_transaction_type_keyboard
from src.platform.telegram.state.transaction import CreateTransactionForm
from src.platform.telegram.validator import SkipAnswer, amount_filter
from src.platform.telegram.validator.transaction import valid_transaction_type_filter


router = Router(name=__name__)


@router.message(Command("add_transaction"))
async def handle_add_transaction(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    user_id = message.from_user.id

    await state.update_data(user_id=user_id)
    await state.set_state(CreateTransactionForm.transaction_type)
    await message.answer(
        "What's the transaction type?", reply_markup=get_transaction_type_keyboard()
    )


@router.message(CreateTransactionForm.transaction_type, valid_transaction_type_filter)
async def handle_valid_type(
    message: Message, state: FSMContext, transaction_type: TransactionType
) -> None:
    await state.update_data(transaction_type=transaction_type)
    await state.set_state(CreateTransactionForm.title)
    await message.answer(
        "Enter the transaction title.", reply_markup=ReplyKeyboardRemove()
    )


@router.message(CreateTransactionForm.transaction_type)
async def handle_invalid_type(message: Message) -> None:
    await message.answer(
        "Incorrect transaction type.", reply_markup=get_transaction_type_keyboard()
    )


@router.message(CreateTransactionForm.title, F.text.len() <= 64)
async def handle_valid_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(CreateTransactionForm.description)
    await message.answer(
        "Optional: add a description.", reply_markup=get_skip_keyboard()
    )


@router.message(CreateTransactionForm.title, F.text.len() > 64)
async def handle_invalid_title(message: Message) -> None:
    await message.answer("The title must be at most 64 characters.")


@router.message(CreateTransactionForm.description, F.text.len() <= 256)
async def handle_valid_description(message: Message, state: FSMContext) -> None:
    if message.text != SkipAnswer.SKIP:
        await state.update_data(description=message.text)

    await state.set_state(CreateTransactionForm.amount)
    await message.answer(
        "Enter the transaction amount.", reply_markup=ReplyKeyboardRemove()
    )


@router.message(CreateTransactionForm.description, F.text.len() > 256)
async def handle_invalid_description(message: Message) -> None:
    await message.answer(
        "The description must be at most 256 characters.",
        reply_markup=get_skip_keyboard(),
    )


@router.message(CreateTransactionForm.amount, amount_filter)
async def handle_valid_amount(
    message: Message, state: FSMContext, amount: Decimal
) -> None:
    data = await state.update_data(amount=amount)
    await state.clear()

    try:
        usecase = CreateTransactionUsecase()
        await usecase.execute(**data)
        await message.answer("👍")
    except:
        # Should be unreachable.
        error(f"Transaction creation failed: {data}")
        await message.answer("Failed. An error has occured.")


@router.message(CreateTransactionForm.amount)
async def handle_invalid_amount(message: Message) -> None:
    await message.answer("Please, enter a valid amount. Use a dot for decimal numbers.")
