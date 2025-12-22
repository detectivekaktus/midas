from enum import StrEnum


class MainMenuOption(StrEnum):
    PROFILE = "👤 Profile"
    TRANSACTIONS = "🗂 Transactions"


class BackOption(StrEnum):
    """
    Universal BACK option.
    """

    BACK = "◀️ Back"


class ProfileMenuOption(StrEnum):
    CHANGE_PROFILE = "✏️ Change profile"
    DELETE_PROFILE = "🚫 Delete profile"


class TransactionsMenuOption(StrEnum):
    ADD = "✏️ Add new transaction"
    VIEW = "👀 View transactions"
