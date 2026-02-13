from abc import ABC
from typing import Any, override
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from midas.loggers import aiogram_logger
from midas.service.user_caching import CachedUser

from midas.util.enums import Currency

from midas.platform.telegram.keyboard import get_yes_no_keyboard
from midas.platform.telegram.util.rendering.abstract_pager import AbstractPager
from midas.platform.telegram.util.menu.events import remove_menu, send_main_menu


class Pager[T: Any](AbstractPager[T], ABC):
    """
    Added abstraction layer above `AbstractPager`. This class contains basic
    algorithms for generic pagination routines.

    Please, consider that `render()` and `handle_edit_callback_query()` methods
    need to be overriden in the concrete pager implementation.
    """

    @override
    async def handle_init_pagination_command(
        self, message: Message, state: FSMContext, user: CachedUser
    ) -> None:
        aiogram_logger.info(f"Received init pagination command: {self=}")

        current = 0
        max_items = 16
        items: list[T] = await self.get_usecase.execute(user.id, max_items)

        if len(items) == 0:
            await state.clear()
            await send_main_menu(message, state, "Nothing to display ☹️")
            return

        await remove_menu(message, state)
        await state.update_data(
            user=user, items=items, currnet=current, max_items=max_items
        )
        await state.set_state(self.states_group.show)

        item = items[current]
        text = self._render_item(item, Currency(user.currency_id))
        await message.answer(text, reply_markup=self.markup)

    @override
    async def handle_next_callback_query(
        self, query: CallbackQuery, state: FSMContext
    ) -> None:
        data = await state.get_data()
        user: CachedUser = data["user"]
        current: int = data["current"]
        max_items: int = data["max_items"]
        items: list[T] = data["items"]

        current += 1
        if current >= len(items):
            max_items *= 2
            items = await self.get_usecase.execute(user.id, max_items)
            # if after refetch the initial condition is still met, there are
            # no new items to display.
            if current >= len(items):
                await query.answer("No more transactions available.")
                return

            await state.update_data(max_items=max_items, items=items)
        await state.update_data(current=current)

        item = items[current]
        await self.answer_query(query, item, Currency(user.currency_id))

    @override
    async def handle_prev_callback_query(
        self, query: CallbackQuery, state: FSMContext
    ) -> None:
        data = await state.get_data()
        user: CachedUser = data["user"]
        current: int = data["current"]
        items: list[T] = data["items"]

        if current == 0:
            await query.answer("Already at the first item.")
            return

        current -= 1
        await state.update_data(current=current)

        item = items[current]
        await self.answer_query(query, item, Currency(user.currency_id))

    @override
    async def handle_delete_callback_query(
        self, query: CallbackQuery, state: FSMContext
    ) -> None:
        await state.set_state(self.states_group.confirm_delete)

        try:
            message = await self._get_message_from_query(query)
        except ValueError:
            return

        await query.answer()
        await message.answer(
            "⚠️ Are you sure you want to delete this item?",
            reply_markup=get_yes_no_keyboard(),
        )

    @override
    async def handle_confirm_delete(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        user: CachedUser = data["user"]
        current: int = data["current"]
        items: list[T] = data["items"]
        deleted_item = items[current]

        aiogram_logger.info(f"Received item delete command: {user.id} - {deleted_item}")
        await self.delete_usecase.execute(getattr(deleted_item, "id"))

        if len(items) == 1:
            await state.clear()
            await send_main_menu(message, state, "Nothing to display ☹️")
            return

        items.pop(current)
        current -= 1 if current != 0 else 0
        await state.update_data(current=current, items=items)
        await state.set_state(self.states_group.show)
        await message.answer("👍", reply_markup=ReplyKeyboardRemove())

        item = items[current]
        text = self._render_item(item, Currency(user.currency_id))
        await message.answer(text, reply_markup=self.markup)

    @override
    async def handle_reject_delete(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        user: CachedUser = data["user"]
        current: int = data["current"]
        items: list[T] = data["items"]

        await state.set_state(self.states_group.show)
        await message.answer("Canceled deletion.", reply_markup=ReplyKeyboardRemove())

        item = items[current]
        text = self._render_item(item, Currency(user.currency_id))
        await message.answer(text, reply_markup=self.markup)

    @override
    async def handle_invalid_delete_option(self, message: Message) -> None:
        await message.answer(
            "Please, select a valid option.", reply_markup=get_yes_no_keyboard()
        )

    @override
    async def handle_exit_callback_query(
        self, query: CallbackQuery, state: FSMContext
    ) -> None:
        await state.clear()
        await query.answer()

        try:
            message = await self._get_message_from_query(query)
        except ValueError:
            return
        await send_main_menu(message, state, "👍")
