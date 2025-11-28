from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Optional
from aiogram.types import Message


class YesNoAnswer(StrEnum):
    YES = "✅ Yes"
    NO  = "🚫 No"


class SkipAnswer(StrEnum):
    SKIP = "⏭️ Skip"


def validate_amount(text: str) -> Decimal:
    """
    Check if amount corrisponds to database Numeric(12, 2) definition. I.e.
    12 digits total 2 of which are decimal.

    :param text: amount to check
    :type text: str
    :return: decimal representation of the amount
    :rtype: Decimal
    """
    # if text has decimal part and its length is greater than 13
    # or if text has no decimal part and its length is greater than 10
    if ("." in text and len(text) > 13) or ("." not in text and len(text) > 10):
        raise ValueError(f"{text} does not corrispond to Numeric(12, 2) definition")
    
    if "." in text:
        decimal_part = text.split(".")[1]
        if len(decimal_part) > 2:
            raise ValueError(f"{text} decimal part contains more than 2 digits.")
        
    return Decimal(text)


def amount_filter(message: Message) -> Optional[dict[str, Decimal]]:
    """
    Aiogram amount filter.
    """
    try:
        text = message.text
        if not text:
            return None
        
        amount = validate_amount(text)
    except (InvalidOperation, ValueError):
        return None
    
    return {"amount": amount}
