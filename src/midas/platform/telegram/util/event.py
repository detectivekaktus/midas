from midas.util.enums import EventFrequency


def get_event_frequencies_list() -> list[str]:
    """
    Get displayed event frequency list.

    This list is made of emojis corrisponding to the
    `EventFrequencyu` enum elements.

    :return: list of displayable event frequencies.
    :rtype: list[str]
    """
    type_map = {
        EventFrequency.DAILY: "🌞",
        EventFrequency.WEEKLY: "🪂",
        EventFrequency.MONTHLY: "📅",
    }
    return [f"{type_map[type_]} {type_.name.capitalize()}" for type_ in EventFrequency]
