"""Agua IOT chrono (weekly program) helpers."""

from datetime import time

# Chrono start/stop registers count 10-minute steps since midnight.
# 144 (24:00) and above means the slot is not set.
CHRONO_STEP_MINUTES = 10
CHRONO_STEPS_PER_DAY = 144

WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


def chrono_key(program, field):
    return f"chrono_p{program}_{field}_set"


def chrono_day_key(program, day):
    return f"chrono_p{program}_day_{day}_set"


def steps_to_time(steps):
    """Convert a 10-minute step count to a time, None when not set."""
    if steps is None:
        return None
    steps = int(steps)
    if not 0 <= steps < CHRONO_STEPS_PER_DAY:
        return None
    minutes = steps * CHRONO_STEP_MINUTES
    return time(minutes // 60, minutes % 60)


def time_to_steps(value):
    """Convert a time to a 10-minute step count, rounding down."""
    return (value.hour * 60 + value.minute) // CHRONO_STEP_MINUTES
