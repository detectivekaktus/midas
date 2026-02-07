# TODO: This logic as well as platform/telegram/router/transaction/pagination_handler.py
# is 90% identical. This whole structure could be refactored into an abstract pagination
# handler which would require `get_displayee()`, `render()` , and `answer_query()` methods
# implemented as well as inject `aiogram.Router` object as dependency.
#
# This way I could eliminate the repetitiveness of the codebase and speed up the development
# process of the new features.
from typing import Sequence
from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message,
    ReplyKeyboardRemove,
)

from midas.loggers import aiogram_logger
from midas.service.user_caching import CachedUser

from midas.db.schemas.event import Event
from midas.usecase.event import DeleteEventUsecase, GetEventsUsecase
from midas.util.enums import Currency, EventFrequency, TransactionType

from midas.platform.telegram.keyboard import get_yes_no_keyboard
from midas.platform.telegram.keyboard.transaction import get_transaction_type_keyboard
from midas.platform.telegram.keyboard.inline.event import (
    EventPaginationCommand,
    Command as PaginationCommand,
    get_event_pagination_inline_keyboard,
)
from midas.platform.telegram.state import FormMode
from midas.platform.telegram.state.event import EventForm, EventPaginationState
from midas.platform.telegram.validator import YesNoAnswer
from midas.platform.telegram.util.menu.events import remove_menu, send_main_menu
from midas.platform.telegram.util.menu.options import EventMenuOption


router = Router(name=__name__)


def render_event(event: Event, currency: Currency) -> str:
    """
    Render event to the end user.

    :param event: event to be rendered
    :type event: Event
    :return: rendered event
    :rtype: str
    """
    frequency = EventFrequency(event.interval).name.capitalize()
    type_ = TransactionType(event.transaction_type_id).readable()
    description = event.description
    last_run_date = event.last_run_on.strftime("%d/%m/%Y")

    text = (
        f"{html.bold("EVENT")}\n"
        f"Last time occured on {last_run_date}\n"
        f"Runs {html.italic(frequency)}\n"
        f"📌 {event.title}\n"
        f"💳 {type_}\n"
        f"📝 {description if description else html.italic("No description provided")}\n"
        f"💰 {currency.name} {event.amount}"
    )
    return text


async def get_events(user_id: int, count: int) -> Sequence[Event]:
    """
    Wrapper for `GetEventsUsecase.execute()` method.

    :param user_id: user's telegram id.
    :type user_id: int
    :param max_events: number of events to retrieve.
    :type max_events: int
    :return: user's events or empty list if `user_id` is invalid.
    :rtype: Sequence[Event]
    """
    usecase = GetEventsUsecase()
    events = await usecase.execute(user_id, count)
    return events


async def answer_query(query: CallbackQuery, event: Event, currency: Currency) -> None:
    """
    Answer callback query, render and send back event page.
    """
    message = query.message
    if not message or isinstance(message, InaccessibleMessage):
        aiogram_logger.warning("Couldn't find message bound to the callback query.")
        await query.answer("If you see this message, report a bug on github.")
        return

    await query.answer()
    text = render_event(event, currency)
    await message.edit_text(text, reply_markup=get_event_pagination_inline_keyboard())


@router.message(Command("events"))
@router.message(F.text == EventMenuOption.VIEW)
async def handle_events_command(
    message: Message, state: FSMContext, user: CachedUser
) -> None:
    aiogram_logger.info(f"Recieved `/events` command: {user.id}")

    current = 0
    max_events = 16
    events = await get_events(user.id, max_events)

    if len(events) == 0:
        await state.clear()
        await send_main_menu(message, state, "Nothing to display ☹️")
        return
    event = events[current]

    await remove_menu(message, state)

    await state.update_data(
        user=user, events=events, current=current, max_events=max_events
    )
    await state.set_state(EventPaginationState.show)

    text = render_event(event, Currency(user.currency_id))
    await message.answer(text, reply_markup=get_event_pagination_inline_keyboard())


@router.callback_query(
    EventPaginationCommand.filter(F.command == PaginationCommand.NEXT),
    EventPaginationState.show,
)
async def handle_next_callback_query(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    user: CachedUser = data["user"]
    current: int = data["current"]
    max_events: int = data["max_events"]
    events: Sequence[Event] = data["events"]

    current += 1
    # refactor this monstrosity
    if len(events) != max_events and len(events) == current:
        await query.answer("No more events available.")
        return
    elif max_events == current:
        max_events *= 2
        events = await get_events(user.id, max_events)
        await state.update_data(events=events, max_events=max_events)
        # if number of events after refetch remained the same
        if len(events) == max_events / 2:
            await query.answer("No more events available.")
            return
    await state.update_data(current=current)

    await answer_query(query, events[current], Currency(user.currency_id))


@router.callback_query(
    EventPaginationCommand.filter(F.command == PaginationCommand.PREV),
    EventPaginationState.show,
)
async def handle_prev_callback_query(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    user: CachedUser = data["user"]
    current: int = data["current"]
    events: Sequence[Event] = data["events"]

    if current == 0:
        await query.answer("Already at the first transaction.")
        return

    current -= 1
    await state.update_data(current=current)

    await answer_query(query, events[current], Currency(user.currency_id))


@router.callback_query(
    EventPaginationCommand.filter(F.command == PaginationCommand.DELETE),
    EventPaginationState.show,
)
async def handle_delete_callback_query(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(EventPaginationState.confirm_delete)

    message = query.message
    if not message or isinstance(message, InaccessibleMessage):
        aiogram_logger.warning("Couldn't find message bound to the callback query.")
        await query.answer("If you see this message, report a bug on github.")
        return

    await query.answer()
    await message.answer(
        "⚠️ Are you sure you want to delete this event?\n"
        "Note that it won't delete the transactions produced by this event",
        reply_markup=get_yes_no_keyboard(),
    )


@router.message(EventPaginationState.confirm_delete, F.text == YesNoAnswer.YES)
async def handle_confirm_delete_callback_query(
    message: Message, state: FSMContext
) -> None:
    data = await state.get_data()
    user: CachedUser = data["user"]
    current: int = data["current"]
    events: list[Event] = data["events"]
    deleted_event: Event = events[current]

    aiogram_logger.info(
        f"Received event delete command: {user.id} - {deleted_event.id}"
    )

    usecase = DeleteEventUsecase()
    await usecase.execute(deleted_event.id)

    if len(events) == 1:
        await state.clear()
        await send_main_menu(message, state, "Nothing to display ☹️")
        return

    events.pop(current)
    current -= 1 if current != 0 else 0
    await state.update_data(current=current, events=events)
    await state.set_state(EventPaginationState.show)
    await message.answer("👍", reply_markup=ReplyKeyboardRemove())

    text = render_event(events[current], Currency(user.currency_id))
    await message.answer(text, reply_markup=get_event_pagination_inline_keyboard())


@router.message(EventPaginationState.confirm_delete, F.text == YesNoAnswer.NO)
async def handle_reject_delete_callback_query(
    message: Message, state: FSMContext
) -> None:
    data = await state.get_data()
    user: CachedUser = data["user"]
    current: int = data["current"]
    events: Sequence[Event] = data["events"]
    event = events[current]

    await state.set_state(EventPaginationState.show)
    await message.answer("Canceled deletion.", reply_markup=ReplyKeyboardRemove())

    text = render_event(event, Currency(user.currency_id))
    await message.answer(text, reply_markup=get_event_pagination_inline_keyboard())


@router.message(EventPaginationState.confirm_delete)
async def handle_invalid_delete_option(message: Message) -> None:
    await message.answer(
        "Please, select a valid option.", reply_markup=get_yes_no_keyboard()
    )


@router.callback_query(
    EventPaginationCommand.filter(F.command == PaginationCommand.EDIT),
    EventPaginationState.show,
)
async def handle_edit_callback_query(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    mode: FormMode = FormMode.EDIT
    user: CachedUser = data["user"]
    events: Sequence[Event] = data["events"]
    current: int = data["current"]
    event: Event = events[current]

    aiogram_logger.info(f"Received event edit command: {user.id} - {event.id}")
    await state.clear()

    await state.set_state(EventForm.transaction_type)
    await state.update_data(user_id=user.id, mode=mode, event=event)

    message = query.message
    if not message or isinstance(message, InaccessibleMessage):
        aiogram_logger.warning("Couldn't find message bound to the callback query.")
        await query.answer("If you see this message, report a bug on github.")
        return

    transaction_type: str = TransactionType(event.transaction_type_id).readable()
    await query.answer()
    await message.answer(
        f"Enter new transaction type. (current: {transaction_type})",
        reply_markup=get_transaction_type_keyboard(skippable=True),
    )
    # see form_handler.py handlers


@router.callback_query(
    EventPaginationCommand.filter(F.command == PaginationCommand.EXIT),
    EventPaginationState.show,
)
async def handle_exit_callback_query(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.answer()

    message = query.message
    if not message or isinstance(message, InaccessibleMessage):
        aiogram_logger.warning("Couldn't find message bound to the callback query.")
        return

    await send_main_menu(message, state, "👍")
