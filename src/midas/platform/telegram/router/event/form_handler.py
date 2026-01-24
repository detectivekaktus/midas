from decimal import Decimal
from typing import Optional
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from midas.loggers import aiogram_logger
from midas.service.user_caching import CachedUser

from midas.usecase.event import CreateEventUsecase
from midas.util.enums import EventFrequency, TransactionType

from midas.platform.telegram.router.util import skipped_unskippable
from midas.platform.telegram.keyboard import get_skip_keyboard
from midas.platform.telegram.keyboard.event import get_event_frequency_keyboard
from midas.platform.telegram.keyboard.transaction import get_transaction_type_keyboard
from midas.platform.telegram.state import FormMode
from midas.platform.telegram.state.event import EventForm
from midas.platform.telegram.validator import SkipAnswer, amount_filter
from midas.platform.telegram.validator.event import valid_event_frequency_filter
from midas.platform.telegram.validator.transaction import valid_transaction_type_filter
from midas.platform.telegram.util.menu.events import remove_menu, send_events_menu
from midas.platform.telegram.util.menu.options import EventMenuOption


router = Router(name=__name__)


async def create_event(message: Message, state: FSMContext) -> None:
    data = {k: v for k, v in (await state.get_data()).items() if k not in ("mode")}
    await state.clear()

    try:
        usecase = CreateEventUsecase()
        await usecase.execute(**data)
        await send_events_menu(message, state, "👍", set_state=True)
    except Exception as e:
        aiogram_logger.error(f"Event creation failed: {data}")
        aiogram_logger.error(f"The problem to this was the following exception: {e}")
        await send_events_menu(
            message, state, "Failed. Something went wrong.", set_state=True
        )


@router.message(Command("add_event"))
@router.message(F.text == EventMenuOption.ADD)
async def handle_add_event_command(
    message: Message, state: FSMContext, user: CachedUser
) -> None:
    aiogram_logger.info(f"Received `/add_event` command: {user.id}")

    await remove_menu(message, state)

    mode = FormMode.CREATE
    await state.update_data(user_id=user.id, mode=mode)
    await state.set_state(EventForm.transaction_type)
    await message.answer(
        "Enter event's transaction type.", reply_markup=get_transaction_type_keyboard()
    )


@router.message(EventForm.transaction_type, valid_transaction_type_filter)
@router.message(EventForm.transaction_type, F.text == SkipAnswer.SKIP)
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
            "Enter the event title. It will be set as title for all subsequent transactions created under this event.",
            reply_markup=ReplyKeyboardRemove(),
        )

    await state.set_state(EventForm.title)


@router.message(EventForm.transaction_type)
async def handle_invalid_type(message: Message) -> None:
    await message.answer(
        "Incorrect transaction type.", reply_markup=get_transaction_type_keyboard()
    )


@router.message(EventForm.title, F.text.len() <= 64)
async def handle_valid_title(message: Message, state: FSMContext) -> None:
    mode: FormMode = await state.get_value("mode")  # type: ignore
    if await skipped_unskippable(message, mode):
        return

    if mode == FormMode.CREATE:
        await state.update_data(title=message.text)
        await message.answer(
            "Optional: add a description", reply_markup=get_skip_keyboard()
        )

    await state.set_state(EventForm.description)


@router.message(EventForm.title, F.text.len() > 64)
async def handle_invalid_title(message: Message) -> None:
    await message.answer("The title must be at most 64 characters.")


@router.message(EventForm.description, F.text.len() <= 256)
async def handle_valid_description(message: Message, state: FSMContext) -> None:
    mode: FormMode = await state.get_value("mode")  # type: ignore

    if message.text != SkipAnswer.SKIP:
        await state.update_data(description=message.text)

    if mode == FormMode.CREATE:
        await message.answer(
            "Enter the transaction amount.", reply_markup=ReplyKeyboardRemove()
        )

    await state.set_state(EventForm.amount)


@router.message(EventForm.description, F.text.len() > 256)
async def handle_invalid_description(message: Message) -> None:
    await message.answer(
        "The description must be at most 256 characters.",
        reply_markup=get_skip_keyboard(),
    )


@router.message(EventForm.amount, amount_filter)
@router.message(EventForm.amount, F.text == SkipAnswer.SKIP)
async def handle_valid_amount(
    message: Message, state: FSMContext, amount: Optional[Decimal] = None
) -> None:
    mode: FormMode = await state.get_value("mode")  # type: ignore
    if await skipped_unskippable(message, mode, amount):
        return

    if mode == FormMode.CREATE:
        await state.update_data(amount=amount)
        await message.answer(
            "How often should the event occur?",
            reply_markup=get_event_frequency_keyboard(),
        )

    await state.set_state(EventForm.frequency)


@router.message(EventForm.amount)
async def handle_invalid_amount(message: Message) -> None:
    await message.answer("Please, enter a valid amount. Use a dot for decimal numbers.")


@router.message(EventForm.frequency, valid_event_frequency_filter)
@router.message(EventForm.frequency, F.text == SkipAnswer.SKIP)
async def handle_valid_frequency(
    message: Message, state: FSMContext, frequency: Optional[EventFrequency] = None
) -> None:
    mode: FormMode = await state.get_value("mode")  # type: ignore
    if await skipped_unskippable(
        message, mode, frequency, get_event_frequency_keyboard()
    ):
        return

    if mode == FormMode.CREATE:
        aiogram_logger.info(
            f"Confirm event creation: {await state.get_value("user_id")}"
        )
        await state.update_data(frequency=frequency)
        await create_event(message, state)


@router.message(EventForm.frequency)
async def handle_invalid_frequency(message: Message) -> None:
    await message.answer(
        "Please, enter a valid frequency.", reply_markup=get_event_frequency_keyboard()
    )
