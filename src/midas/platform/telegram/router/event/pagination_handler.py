from typing import Any, Callable, override
from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from midas.loggers import aiogram_logger
from midas.service.user_caching import CachedUser

from midas.db.schemas.event import Event
from midas.usecase.event import DeleteEventUsecase, GetEventsUsecase
from midas.util.enums import Currency, EventFrequency, TransactionType

from midas.platform.telegram.keyboard.transaction import get_transaction_type_keyboard
from midas.platform.telegram.keyboard.inline.event import (
    EventPaginationCommand,
    Command as PaginationCommand,
    get_event_pagination_inline_keyboard,
)
from midas.platform.telegram.state import FormMode
from midas.platform.telegram.state.event import EventForm, EventPaginationState
from midas.platform.telegram.validator import YesNoAnswer
from midas.platform.telegram.util.menu.options import EventMenuOption
from midas.platform.telegram.util.rendering import Pager


router = Router(name=__name__)


class EventPager(Pager[Event]):
    @override
    def _render_item(self, item: Event, currency: Currency) -> str:
        frequency = EventFrequency(item.interval).name.capitalize()
        type_ = TransactionType(item.transaction_type_id).readable()
        description = item.description
        last_run_date = item.last_run_on.strftime("%d/%m/%Y")

        text = (
            f"{html.bold("EVENT")}\n"
            f"Last time occured on {last_run_date}\n"
            f"Runs {html.italic(frequency)}\n"
            f"📌 {item.title}\n"
            f"💳 {type_}\n"
            f"📝 {description if description else html.italic("No description provided")}\n"
            f"💰 {currency.name} {item.amount}"
        )
        return text

    @override
    async def handle_edit_callback_query(
        self, query: CallbackQuery, state: FSMContext
    ) -> None:
        data = await state.get_data()
        mode: FormMode = FormMode.EDIT
        user: CachedUser = data["user"]
        items: list[Event] = data["items"]
        current: int = data["current"]
        item = items[current]

        aiogram_logger.info(f"Received event edit command: {user.id} - {item.id}")
        await state.clear()

        await state.set_state(EventForm.transaction_type)
        await state.update_data(user_id=user.id, mode=mode, event=item)

        try:
            message = await self._get_message_from_query(query)
        except ValueError:
            return

        transaction_type: str = TransactionType(item.transaction_type_id).readable()
        await query.answer()
        await message.answer(
            f"Enter new transaction type. (current: {transaction_type})",
            reply_markup=get_transaction_type_keyboard(skippable=True),
        )
        # see form_handler.py handlers

    @override
    def _handler_rules(self) -> list[Callable[..., Any]]:
        return [
            # /events command
            lambda r: r.message(Command("events"))(self.handle_init_pagination_command),
            lambda r: r.message(F.text == EventMenuOption.VIEW)(
                self.handle_init_pagination_command
            ),
            # next button
            lambda r: r.callback_query(
                EventPaginationCommand.filter(F.command == PaginationCommand.NEXT),
                self.states_group.show,
            )(self.handle_next_callback_query),
            # prev button
            lambda r: r.callback_query(
                EventPaginationCommand.filter(F.command == PaginationCommand.PREV),
                self.states_group.show,
            )(self.handle_prev_callback_query),
            # delete button
            lambda r: r.callback_query(
                EventPaginationCommand.filter(F.command == PaginationCommand.DELETE),
                self.states_group.show,
            )(self.handle_delete_callback_query),
            lambda r: r.message(
                self.states_group.confirm_delete, F.text == YesNoAnswer.YES
            )(self.handle_confirm_delete),
            lambda r: r.message(
                self.states_group.confirm_delete, F.text == YesNoAnswer.NO
            )(self.handle_reject_delete),
            lambda r: r.message(self.states_group.confirm_delete)(
                self.handle_invalid_delete_option
            ),
            # edit button
            lambda r: r.callback_query(
                EventPaginationCommand.filter(F.command == PaginationCommand.EDIT),
                self.states_group.show,
            )(self.handle_edit_callback_query),
            # exit button
            lambda r: r.callback_query(
                EventPaginationCommand.filter(F.command == PaginationCommand.EXIT),
                self.states_group.show,
            )(self.handle_exit_callback_query),
        ]


pager = EventPager(
    GetEventsUsecase(),
    DeleteEventUsecase(),
    get_event_pagination_inline_keyboard(),
    EventPaginationState,
)
pager.register_handlers(router)
