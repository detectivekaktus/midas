from typing import Optional
from aiogram.types import Message

from midas.util.enums import EventFrequency


def validate_event_frequency(text: str) -> EventFrequency:
    """
    Check if text is a readable form of `EventFrequency` enum.

    :return: event frequency enum instance
    :rtype: EventFrequency
    :raise ValueError: if text is not a valid event frequency
    """
    try:
        frequency = text.split(" ", 1)[-1].upper()
        return EventFrequency[frequency]
    except (IndexError, KeyError) as e:
        raise ValueError(f"`{text}` is not a valid event frequency") from e


def valid_event_frequency_filter(
    message: Message,
) -> Optional[dict[str, EventFrequency]]:
    """
    Aiogram filter for frequencies.
    """
    try:
        text = message.text
        if not text:
            return None

        frequency = validate_event_frequency(text)
    except ValueError:
        return None

    return {"frequency": frequency}
