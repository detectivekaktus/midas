from typing import Optional
from aiogram.types import Message

from src.util.enums import TransactionType


def validate_transaction_type(text: str) -> TransactionType:
    """
    Check if text is a readable form of `TransactionType` enum value instance.

    :return: transaction type enum instance
    :rtype: TransactionType
    :raise ValueError: if text is not a valid readable form of transaction type.
    """
    try:
        return TransactionType.from_readable(text)
    except KeyError as e:
        raise ValueError(f"{text} is not a valid transaction type") from e
    

def valid_transaction_type_filter(message: Message) -> Optional[dict[str, TransactionType]]:
    """
    Aiogram transaction type filter.
    """
    try:
        text  = message.text
        if not text:
            return None
        
        type_ = validate_transaction_type(text)
    except ValueError:
        return None
    
    return {"transaction_type": type_}
