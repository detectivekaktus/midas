from calendar import monthrange
from datetime import date

from midas.util.enums import EventFrequency


def determine_timedelta(frequency: EventFrequency) -> int:
    today = date.today()
    delta = frequency
    # if delta is anything but monthly, leave it as it is.
    # if not, get the number of days of the month and use it as
    # delta (28, 30 and 31)
    if delta == EventFrequency.MONTHLY:
        delta = monthrange(today.year, today.month)[1]

    return delta
