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
    BTC = 4
    ETH = 5


class TransactionType(IntEnum):
    """
    Transaction type enum. Each element corrisponds to the `id`
    column inside `transaction_types` table.

    Note that in case of adding more seed values you must update
    this enumeration.
    """
    INCOME          = 1
    GROCERIES       = 2
    TRANSPORTATION  = 3
    ENTERTAINMENT   = 4
    SHOPPING        = 5
    GIFTS           = 6
    BILLS_AND_FEES  = 7
    HEALTHCARE      = 8
    TRAVEL          = 9
    OTHER           = 10
