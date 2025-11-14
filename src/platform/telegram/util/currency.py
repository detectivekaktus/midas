from src.util.enums import StrCurrency


def get_currency_list() -> list[str]:
    """
    Get displayed currency list.

    This list is made of emojis corrisponding to the
    `StrCurrency` enum elements.

    :return: list of displayable currencies.
    :rtype: list[str]
    """
    currency_map = {
        StrCurrency.EUR: "🇪🇺",
        StrCurrency.USD: "🇺🇸",
        StrCurrency.UAH: "🇺🇦",
        StrCurrency.BTC: "🌍",
        StrCurrency.ETH: "🌏"
    }
    return [f"{currency_map[currency]} {currency.value}" for currency in StrCurrency]
