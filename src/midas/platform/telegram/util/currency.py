from midas.util.enums import Currency


def get_currency_list() -> list[str]:
    """
    Get displayed currency list.

    This list is made of emojis corrisponding to the
    `Currency` enum elements.

    :return: list of displayable currencies.
    :rtype: list[str]
    """
    currency_map = {
        Currency.EUR: "🇪🇺",
        Currency.USD: "🇺🇸",
        Currency.UAH: "🇺🇦",
    }
    return [f"{currency_map[currency]} {currency.name}" for currency in Currency]
