from typing import Any, Callable, override
from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from midas.loggers import aiogram_logger
from midas.service.user_caching import CachedUser

from midas.db.schemas.transaction import Transaction
from midas.usecase.transaction import DeleteTransactionUsecase, GetTransactionsUsecase
from midas.util.enums import Currency, TransactionType

from midas.platform.telegram.keyboard.transaction import get_transaction_type_keyboard
from midas.platform.telegram.keyboard.inline.transaction import (
    Command as PaginationCommand,
    TransactionPaginationCommand,
    get_transaction_pagination_inline_keyboard,
)
from midas.platform.telegram.state import FormMode
from midas.platform.telegram.state.transaction import (
    TransactionForm,
    TransactionPaginationState,
)
from midas.platform.telegram.validator import YesNoAnswer
from midas.platform.telegram.util.menu.options import TransactionsMenuOption
from midas.platform.telegram.util.rendering import Pager


router = Router(name=__name__)


class TransactionPager(Pager[Transaction]):
    @override
    def _render_item(self, item: Transaction, currency: Currency) -> str:
        type_ = TransactionType(item.transaction_type_id).readable()
        description = item.description
        creation_date = item.created_at.strftime("%d/%m/%Y")  # 25/12/2025

        text = (
            f"📅 {creation_date}{html.italic(" - Edited") if item.updated_at is not None else ""}\n"
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
        items: list[Transaction] = data["items"]
        current: int = data["current"]
        item = items[current]

        aiogram_logger.info(f"Received transaction edit command: {user.id} - {item.id}")
        await state.clear()

        await state.set_state(TransactionForm.transaction_type)
        await state.update_data(user_id=user.id, mode=mode, transaction=item)

        try:
            message = await self._get_message_from_query(query)
        except ValueError:
            return

        transaction_type: str = TransactionType(item.transaction_type_id).readable()
        await query.answer()
        await message.answer(
            f"What's the new transaction type? (current: {transaction_type})",
            reply_markup=get_transaction_type_keyboard(skippable=True),
        )
        # see form_handler.py handlers

    @override
    def _handler_rules(self) -> list[Callable[..., Any]]:
        return [
            # /transactions command
            lambda r: r.message(Command("transactions"))(
                self.handle_init_pagination_command
            ),
            lambda r: r.message(F.text == TransactionsMenuOption.VIEW)(
                self.handle_init_pagination_command
            ),
            # next button
            lambda r: r.callback_query(
                TransactionPaginationCommand.filter(
                    F.command == PaginationCommand.NEXT
                ),
                self.states_group.show,
            )(self.handle_next_callback_query),
            # prev button
            lambda r: r.callback_query(
                TransactionPaginationCommand.filter(
                    F.command == PaginationCommand.PREV
                ),
                self.states_group.show,
            )(self.handle_prev_callback_query),
            # delete button
            lambda r: r.callback_query(
                TransactionPaginationCommand.filter(
                    F.command == PaginationCommand.DELETE
                ),
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
                TransactionPaginationCommand.filter(
                    F.command == PaginationCommand.EDIT
                ),
                self.states_group.show,
            )(self.handle_edit_callback_query),
            # exit button
            lambda r: r.callback_query(
                TransactionPaginationCommand.filter(
                    F.command == PaginationCommand.EXIT
                ),
                self.states_group.show,
            )(self.handle_exit_callback_query),
        ]


pager = TransactionPager(
    GetTransactionsUsecase(),
    DeleteTransactionUsecase(),
    get_transaction_pagination_inline_keyboard(),
    TransactionPaginationState,
)
pager.register_handlers(router)
