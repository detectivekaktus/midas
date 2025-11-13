from src.util.enums import StrCurrency


def get_currency_list() -> list[str]:
    """
    Get displayed currency list.

    This list is made of emojis corrisponding to the
    `StrCurrency` enum elements.

    :return: list of displayable currencies.
    :rtype: list[str]
    """
    emojis = ["🇪🇺", "🇺🇸", "🇺🇦", "🌍", "🌏"]
    return [f"{emoji} {currency}" for emoji, currency in zip(emojis, StrCurrency)]
