"""Test chrono helpers (pure functions, no Home Assistant import)."""

import importlib.util
import os
from datetime import time

import pytest

_CHRONO_PATH = os.path.join(
    os.path.dirname(__file__), "..", "custom_components", "aguaiot", "chrono.py"
)
_spec = importlib.util.spec_from_file_location("chrono_module", _CHRONO_PATH)
chrono = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chrono)


class TestStepsToTime:
    @pytest.mark.parametrize(
        "steps,expected",
        [
            (0, time(0, 0)),
            (1, time(0, 10)),
            (36, time(6, 0)),
            (51, time(8, 30)),
            (138, time(23, 0)),
            (143, time(23, 50)),
        ],
    )
    def test_valid_steps(self, steps, expected):
        assert chrono.steps_to_time(steps) == expected

    @pytest.mark.parametrize("steps", [144, 200, 255, 32768, -1, None])
    def test_inactive_or_invalid_steps(self, steps):
        assert chrono.steps_to_time(steps) is None

    def test_float_steps(self):
        assert chrono.steps_to_time(36.0) == time(6, 0)


class TestTimeToSteps:
    @pytest.mark.parametrize(
        "value,expected",
        [
            (time(0, 0), 0),
            (time(6, 0), 36),
            (time(8, 30), 51),
            (time(23, 50), 143),
        ],
    )
    def test_exact_steps(self, value, expected):
        assert chrono.time_to_steps(value) == expected

    def test_rounds_down_to_ten_minutes(self):
        assert chrono.time_to_steps(time(6, 9)) == 36
        assert chrono.time_to_steps(time(23, 59)) == 143

    def test_round_trip(self):
        for steps in range(chrono.CHRONO_STEPS_PER_DAY):
            assert chrono.time_to_steps(chrono.steps_to_time(steps)) == steps


class TestKeys:
    def test_field_key(self):
        assert chrono.chrono_key(1, "start") == "chrono_p1_start_set"
        assert chrono.chrono_key(4, "temperature") == "chrono_p4_temperature_set"

    def test_day_key(self):
        assert chrono.chrono_day_key(2, "monday") == "chrono_p2_day_monday_set"

    def test_weekdays(self):
        assert len(chrono.WEEKDAYS) == 7
        assert chrono.WEEKDAYS[0] == "monday"
        assert chrono.WEEKDAYS[6] == "sunday"
