from abc import ABC, abstractmethod
from typing import Any, Callable
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    InlineKeyboardMarkup,
    Message,
)

from midas.loggers import aiogram_logger
from midas.service.user_caching import CachedUser

from midas.usecase.abstract_usecase import AbstractUsecase
from midas.util.enums import Currency


class PagerStatesGroup(StatesGroup):
    show = State()
    confirm_delete = State()


class AbstractPager[T: Any](ABC):
    """
    Pager class. This class is responsible for providing a set of
    pagination algorithm schemas for telegram user interface. Via this
    class you as developer can easily create paginations for any domain
    object that has get and delete usecases.

    This is the base class of `Pager` class. If you want to find out the
    real pagination algorithms, please see `Pager` class.
    """

    def __init__(
        self,
        get_usecase: AbstractUsecase,
        delete_usecase: AbstractUsecase,
        markup: InlineKeyboardMarkup,
        states_group: type[PagerStatesGroup],
    ) -> None:
        """
        Instantiate a new pager.

        :param get_usecase: get usecase for the `T` type
        :type get_usecase: AbstractUsecase
        :param delete_usecase: delete usecase for the `T` type
        :type delete_usecase: AbstractUsecase
        :param markup: telegram inline keyboard to attach to each page
        :type markup: InlineKeyboardMarkup
        :param states_group: `PagerStatesGroup` type defined for the exact pager.
        :type states_group: PagerStatesGroup
        """
        self.get_usecase = get_usecase
        self.delete_usecase = delete_usecase
        self.markup = markup
        self.states_group = states_group

    @abstractmethod
    def _handler_rules(self) -> list[Callable]:
        """
        Get list of handler rules to apply to the router instance.

        This is an example of a rule that bounds /items command to the
        init pagination handler. Notice that the r argument in the lambda
        function is supposed to be a router.
        lambda r: r.message(Command("items"))(self.handle_init_pagination_command)

        This method is private and is meant to be run automatically in
        `register_handlers()` method.

        :return: list of rules
        :rtype: list[Callable[..., Any]]
        """
        pass

    def register_handlers(self, router: Router) -> None:
        for rule in self._handler_rules():
            rule(router)

    async def _get_message_from_query(self, query: CallbackQuery) -> Message:
        """
        Wrapper for `query.message` field.

        If no message is found or it's inaccessible, a ValueError is returned and
        an error message is sent to user.

        :param query: telegram callback query
        :type query: CallbackQuery
        :return: `query.message` field
        :rtype: Message
        :raise ValueError: if `query.message` is None or is inaccessible.
        """
        message = query.message
        if not message or isinstance(message, InaccessibleMessage):
            aiogram_logger.warning("Couldn't find message bound to the callback query.")
            await query.answer("If you see this message, report a bug on github.")
            raise ValueError("No message bound to query")
        return message

    @abstractmethod
    def _render_item(self, item: T, currency: Currency) -> str:
        """
        Render one item.

        :return: rendered item.
        :rtype: str
        """
        pass

    async def answer_query(
        self, query: CallbackQuery, item: T, currency: Currency
    ) -> None:
        """
        Answer callback query, render and send back item page.

        :param query: telegram callback query
        :type query: CallbackQuery
        :param item: item to be rendered.
        :type item: T
        :param currency: currency
        :type currency: Currency
        """
        try:
            message = await self._get_message_from_query(query)
        except ValueError:
            return

        await query.answer()
        text = self._render_item(item, currency)
        await message.edit_text(text, reply_markup=self.markup)

    @abstractmethod
    async def handle_init_pagination_command(
        self, message: Message, state: FSMContext, user: CachedUser
    ) -> None:
        """
        Aiogram handler for `/items` command.
        """
        pass

    @abstractmethod
    async def handle_next_callback_query(
        self, query: CallbackQuery, state: FSMContext
    ) -> None:
        """
        Aiogram handler for next command inside pagination.
        """
        pass

    @abstractmethod
    async def handle_prev_callback_query(
        self, query: CallbackQuery, state: FSMContext
    ) -> None:
        """
        Aiogram handler for previous command inside pagination.
        """
        pass

    @abstractmethod
    async def handle_delete_callback_query(
        self, query: CallbackQuery, state: FSMContext
    ) -> None:
        """
        Aiogram handler for delete command inside pagination.
        """
        pass

    @abstractmethod
    async def handle_confirm_delete(self, message: Message, state: FSMContext) -> None:
        """
        Aiogram handler for confirming deletion command inside pagination.
        """
        pass

    @abstractmethod
    async def handle_reject_delete(self, message: Message, state: FSMContext) -> None:
        """
        Aiogram handler for rejecting deletion command inside pagination.
        """
        pass

    @abstractmethod
    async def handle_invalid_delete_option(self, message: Message) -> None:
        """
        Aiogram handler for rejecting deletion command inside pagination.
        """
        pass

    @abstractmethod
    async def handle_edit_callback_query(
        self, query: CallbackQuery, state: FSMContext
    ) -> None:
        """
        Aiogram handler for edit command inside pagination.
        """
        pass

    @abstractmethod
    async def handle_exit_callback_query(
        self, query: CallbackQuery, state: FSMContext
    ) -> None:
        """
        Aiogram handler for exit command inside pagination.
        """
        pass
