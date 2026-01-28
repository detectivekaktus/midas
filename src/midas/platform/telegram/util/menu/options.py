from enum import StrEnum


class MainMenuOption(StrEnum):
    PROFILE = "👤 Profile"
    TRANSACTIONS = "🗂 Transactions"
    EVENTS = "🗓️ Events"
    BALANCE = "🏦 See my balance"


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


class EventMenuOption(StrEnum):
    ADD = "🔔 Add new event"
    VIEW = "👀 View events"
