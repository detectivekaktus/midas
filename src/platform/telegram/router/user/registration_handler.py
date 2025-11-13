from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.db.schemas.storage import Storage
from src.db.schemas.account import Account
from src.db.schemas.user import User
from src.query import Repository
from src.util.enums import Currency
from src.usecase.user import RegisterUserUsecase

from src.platform.telegram.validator.currency import valid_currency_filter
from src.platform.telegram.keyboard.currency import get_currency_keyboard
from src.platform.telegram.state.user import UserRegistrationForm


router = Router(name=__name__)


@router.message(Command("start"))
async def handle_start_command(message: Message, state: FSMContext) -> None:
    await state.set_state(UserRegistrationForm.currency)
    await message.answer(
        "Hello 👋 Let's start tracking your expenses.\n"
        "What's your preferred currency?",
        reply_markup=get_currency_keyboard(),
    )


@router.message(UserRegistrationForm.currency, valid_currency_filter)
async def handle_registation_currency(
    message: Message, state: FSMContext, currency: Currency
) -> None:
    await state.clear()

    user_repo = Repository[User, int](User)
    account_repo = Repository[Account, int](Account)
    storage_repo = Repository[Storage, int](Storage)
    usecase = RegisterUserUsecase(user_repo, account_repo, storage_repo)

    try:
        if not message.from_user:
            return

        user_id = message.from_user.id
        usecase.execute(user_id, currency)
        await message.answer(
            "You've been successfully registered 🥳", reply_markup=ReplyKeyboardRemove()
        )
    except KeyError:
        await message.answer(
            "You're already registered 🚫", reply_markup=ReplyKeyboardRemove()
        )


@router.message(UserRegistrationForm.currency)
async def handle_invalid_registration_currency(message: Message) -> None:
    await message.answer(
        "Please, specify a valid currency.", reply_markup=get_currency_keyboard()
    )
