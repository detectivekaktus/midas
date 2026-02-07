from enum import IntEnum


class Currency(IntEnum):
    """
    Currency enum. Each element corrisponds to the `id` column
    inside `currencies` table.

    Note that in case of adding more seed values you must update
    this enumeration.
    """

    EUR = 1
    USD = 2
    UAH = 3


class TransactionType(IntEnum):
    """
    Transaction type enum. Each element corrisponds to the `id`
    column inside `transaction_types` table.

    Note that in case of adding more seed values you must update
    this enumeration.
    """

    INCOME = 1
    GROCERIES = 2
    TRANSPORTATION = 3
    ENTERTAINMENT = 4
    SHOPPING = 5
    GIFTS = 6
    BILLS_AND_FEES = 7
    HEALTHCARE = 8
    TRAVEL = 9
    OTHER = 10

    def readable(self) -> str:
        """
        Transform enum value to human-readable string.

        :return: human-readable string from enum value.
        :rtype: str
        """
        return self.name.lower().replace("_", " ").capitalize()

    @staticmethod
    def from_readable(readable: str) -> "TransactionType":
        """
        Get enum values from human-readable string.

        :return: enum value
        :rtype: TransactionType

        :raise KeyError: if `readable` is not a valid enum
        value name.
        """
        name = readable.upper().replace(" ", "_")
        return TransactionType[name]


class EventFrequency(IntEnum):
    """
    Event frequency enum. Each element represents the `interval`
    column of `events` table.

    Each element corresponds to the number of days to pass.
    For `MONTHLY`, the value is used as an identifier, and the actual
    number of days for the interval is calculated dynamically
    (see `determine_timedelta`).
    """

    DAILY = 1
    WEEKLY = 7
    MONTHLY = 30
