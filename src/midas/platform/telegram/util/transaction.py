from midas.util.enums import TransactionType


def get_transaction_type_list() -> list[str]:
    """
    Get displayed transaction type list.

    This list is made of emojis corrisponding to the
    `TransactionType` enum elements.

    :return: list of displayable transaction types.
    :rtype: list[str]
    """
    type_map = {
        TransactionType.INCOME: "💵",
        TransactionType.GROCERIES: "🛒",
        TransactionType.TRANSPORTATION: "🚍",
        TransactionType.ENTERTAINMENT: "🎮",
        TransactionType.SHOPPING: "🛍️",
        TransactionType.GIFTS: "🎁",
        TransactionType.BILLS_AND_FEES: "🧾",
        TransactionType.HEALTHCARE: "🧑‍⚕️",
        TransactionType.TRAVEL: "✈️",
        TransactionType.OTHER: "👾",
        TransactionType.SAVING: "💰",
    }
    return [f"{type_map[type_]} {type_.readable()}" for type_ in TransactionType]
