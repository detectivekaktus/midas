from aiogram.types import Message

from src.util.enums import Currency


def validate_currency(text: str) -> Currency:
    """
    Check if text is an element inside currency list from
    `src.platform.telegram.util.currency` module.

    :return: currency enum element.
    :rtype: Currency

    :raise ValueError: if text is not an element of the list.
    """
    try:
        # "🇪🇺 EUR".split(" ")[1] = "EUR"
        currency_code = text.split(" ")[1]
        return Currency[currency_code]
    except (IndexError, KeyError) as e:
        raise ValueError(f"{text} is not a valid currency") from e


def valid_currency_filter(message: Message) -> dict[str, Currency] | None:
    """
    Aiogram filter for currencies.
    """
    try:
        text = message.text
        if not text:
            return None

        currency = validate_currency(text)
    except ValueError:
        return None

    return {"currency": currency}
