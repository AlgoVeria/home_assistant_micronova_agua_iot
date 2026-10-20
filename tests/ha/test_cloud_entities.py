"""Test the cloud register entities and the chrono program service."""

from datetime import timedelta

import pytest
import voluptuous as vol
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    EntityCategory,
)
from homeassistant.core import State
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_registry import RegistryEntryDisabler
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    mock_restore_cache_with_extra_data,
)

from custom_components.aguaiot.const import DOMAIN

from .conftest import DEVICE_ID, load_register_map

pytestmark = pytest.mark.asyncio

WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)
PROGRAMS = (1, 2, 3, 4)

EXPECTED_ENTITIES = (
    [
        ("button", "allarm_reset_set"),
        ("button", "load_pellet_set"),
        ("switch", "chrono_general_enable_set"),
        ("switch", "chrono_week_enable_set"),
        ("number", "load_pellet_duration"),
        ("number", "probe_correct_set"),
        ("sensor", "load_pellet_get"),
        ("sensor", "load_pellet_max"),
        ("sensor", "clock_drift"),
        ("binary_sensor", "w_p_braciere_get"),
        ("binary_sensor", "w_spegnimento_get"),
    ]
    + [("time", f"chrono_p{p}_start_set") for p in PROGRAMS]
    + [("time", f"chrono_p{p}_stop_set") for p in PROGRAMS]
    + [("select", f"chrono_p{p}_power_set") for p in PROGRAMS]
    + [("number", f"chrono_p{p}_temperature_set") for p in PROGRAMS]
    + [("switch", f"chrono_p{p}_day_{d}_set") for p in PROGRAMS for d in WEEKDAYS]
)

NEW_KEY_PREFIXES = (
    "allarm_reset_",
    "load_pellet_",
    "chrono_",
    "cleaning_brazier_",
    "w_p_braciere_",
    "w_spegnimento_",
    "probe_correct_",
    "clock_",
    "calendar_",
)


def entity_id(hass, platform, key):
    registry = er.async_get(hass)
    return registry.async_get_entity_id(platform, DOMAIN, f"{DEVICE_ID}_{key}")


def climate_id(hass):
    return er.async_get(hass).async_get_entity_id("climate", DOMAIN, DEVICE_ID)


def bcd(value):
    return int(str(value), 16)


@pytest.fixture
def register_map():
    return load_register_map("jollymec_wood")


# Conditional creation


async def test_all_entities_created(hass, setup_integration, register_map):
    await setup_integration(register_map)
    missing = [
        (platform, key)
        for platform, key in EXPECTED_ENTITIES
        if entity_id(hass, platform, key) is None
    ]
    assert missing == []


async def test_no_entity_when_keys_missing(hass, setup_integration, register_map):
    stripped = {
        key: reg
        for key, reg in register_map.items()
        if not key.startswith(NEW_KEY_PREFIXES)
    }
    entry, _ = await setup_integration(stripped)
    assert entry.state.value == "loaded"
    created = [
        (platform, key)
        for platform, key in EXPECTED_ENTITIES
        if entity_id(hass, platform, key) is not None
    ]
    assert created == []
    # The stove itself is still there
    assert climate_id(hass) is not None


async def test_partial_chrono_map(hass, setup_integration, register_map):
    """Only the programs present in the map get entities."""
    partial = {
        key: reg
        for key, reg in register_map.items()
        if not key.startswith(("chrono_p3_", "chrono_p4_"))
    }
    await setup_integration(partial)
    assert entity_id(hass, "time", "chrono_p2_start_set") is not None
    assert entity_id(hass, "time", "chrono_p3_start_set") is None
    assert entity_id(hass, "number", "chrono_p4_temperature_set") is None


async def test_day_switches_disabled_by_default(hass, setup_integration, register_map):
    await setup_integration(register_map)
    registry = er.async_get(hass)
    entry = registry.async_get(entity_id(hass, "switch", "chrono_p1_day_monday_set"))
    assert entry.disabled_by is RegistryEntryDisabler.INTEGRATION
    assert entry.entity_category is EntityCategory.CONFIG

    entry = registry.async_get(entity_id(hass, "switch", "chrono_general_enable_set"))
    assert entry.disabled_by is None


async def test_entity_categories(hass, setup_integration, register_map):
    await setup_integration(register_map)
    registry = er.async_get(hass)
    for platform, key, category in (
        ("number", "probe_correct_set", EntityCategory.CONFIG),
        ("time", "chrono_p1_start_set", EntityCategory.CONFIG),
        ("select", "chrono_p1_power_set", EntityCategory.CONFIG),
        ("number", "chrono_p1_temperature_set", EntityCategory.CONFIG),
        ("sensor", "load_pellet_max", EntityCategory.DIAGNOSTIC),
        ("sensor", "clock_drift", EntityCategory.DIAGNOSTIC),
    ):
        entry = registry.async_get(entity_id(hass, platform, key))
        assert entry.entity_category is category, key


# Conversions


async def test_time_entity_ten_minute_steps(hass, setup_integration, register_map):
    _, fake = await setup_integration(
        register_map,
        raw={"chrono_p1_start_set": 36, "chrono_p1_stop_set": 138},
    )
    assert hass.states.get(entity_id(hass, "time", "chrono_p1_start_set")).state == (
        "06:00:00"
    )
    assert hass.states.get(entity_id(hass, "time", "chrono_p1_stop_set")).state == (
        "23:00:00"
    )

    await hass.services.async_call(
        "time",
        "set_value",
        {
            ATTR_ENTITY_ID: entity_id(hass, "time", "chrono_p1_start_set"),
            "time": "08:35:00",
        },
        blocking=True,
    )
    assert fake.writes == [{"chrono_p1_start_set": 51}]


@pytest.mark.parametrize("word", [144, 255, 0x8000])
async def test_time_entity_inactive_or_unread(
    hass, setup_integration, register_map, word
):
    await setup_integration(register_map, raw={"chrono_p1_start_set": word})
    state = hass.states.get(entity_id(hass, "time", "chrono_p1_start_set"))
    assert state.state == STATE_UNKNOWN


async def test_temperature_half_degree(hass, setup_integration, register_map):
    _, fake = await setup_integration(
        register_map, raw={"chrono_p1_temperature_set": 41}
    )
    eid = entity_id(hass, "number", "chrono_p1_temperature_set")
    state = hass.states.get(eid)
    assert float(state.state) == 20.5
    assert state.attributes["step"] == 0.5
    assert state.attributes["min"] == 7
    assert state.attributes["max"] == 40

    await hass.services.async_call(
        "number",
        "set_value",
        {ATTR_ENTITY_ID: eid, "value": 19},
        blocking=True,
    )
    assert fake.writes == [{"chrono_p1_temperature_set": 38}]


async def test_power_silent(hass, setup_integration, register_map):
    _, fake = await setup_integration(register_map, raw={"chrono_p1_power_set": 0})
    eid = entity_id(hass, "select", "chrono_p1_power_set")
    state = hass.states.get(eid)
    assert state.state == "SIL"
    assert state.attributes["options"] == ["SIL", "P1", "P2", "P3", "P4", "P5"]

    await hass.services.async_call(
        "select",
        "select_option",
        {ATTR_ENTITY_ID: eid, "option": "P4"},
        blocking=True,
    )
    assert fake.writes == [{"chrono_p1_power_set": 4}]


async def test_day_switch_read_error_is_unknown(hass, setup_integration, register_map):
    await setup_integration(
        register_map,
        raw={"chrono_general_enable_set": 0x8000, "chrono_week_enable_set": 1},
    )
    state = hass.states.get(entity_id(hass, "switch", "chrono_general_enable_set"))
    assert state.state == STATE_UNKNOWN
    state = hass.states.get(entity_id(hass, "switch", "chrono_week_enable_set"))
    assert state.state == STATE_ON


async def test_probe_correction(hass, setup_integration, register_map):
    _, fake = await setup_integration(register_map, raw={"probe_correct_set": 9})
    eid = entity_id(hass, "number", "probe_correct_set")
    state = hass.states.get(eid)
    assert float(state.state) == 0
    assert state.attributes["min"] == -4.5
    assert state.attributes["max"] == 4.5
    assert state.attributes["step"] == 0.5

    await hass.services.async_call(
        "number",
        "set_value",
        {ATTR_ENTITY_ID: eid, "value": -1.5},
        blocking=True,
    )
    assert fake.writes == [{"probe_correct_set": 6}]


async def test_brazier_flags(hass, setup_integration, register_map):
    # Bit 2 (mask 4): brazier cleaning, bit 3 (mask 8): waiting for shutdown
    await setup_integration(register_map, raw={"w_p_braciere_get": 4})
    assert (
        hass.states.get(entity_id(hass, "binary_sensor", "w_p_braciere_get")).state
        == STATE_ON
    )
    assert (
        hass.states.get(entity_id(hass, "binary_sensor", "w_spegnimento_get")).state
        == STATE_OFF
    )


async def test_load_pellet_sensors(hass, setup_integration, register_map):
    await setup_integration(
        register_map,
        raw={"load_pellet_get": 40, "load_pellet_max": 200, "status_get": 7},
    )
    # Created even when the stove is running (enable register is status based)
    state = hass.states.get(entity_id(hass, "sensor", "load_pellet_get"))
    assert state.state == "40"
    assert state.attributes["unit_of_measurement"] == "s"
    assert hass.states.get(entity_id(hass, "sensor", "load_pellet_max")).state == "200"


async def test_clock_drift(hass, setup_integration, register_map):
    stove = dt_util.now() + timedelta(minutes=11)
    await setup_integration(
        register_map,
        raw={
            "clock_hour_set": bcd(stove.hour),
            "clock_minute_set": bcd(stove.minute),
            "calendar_day_set": bcd(stove.day),
            "calendar_month_set": bcd(stove.month),
            "calendar_year_set": bcd(stove.year - 2000),
        },
    )
    state = hass.states.get(entity_id(hass, "sensor", "clock_drift"))
    assert int(state.state) in (10, 11)


async def test_clock_drift_read_error(hass, setup_integration, register_map):
    await setup_integration(register_map, raw={"clock_hour_set": 0x8000})
    state = hass.states.get(entity_id(hass, "sensor", "clock_drift"))
    assert state.state == STATE_UNKNOWN


# Button guards


async def test_alarm_reset_only_when_alarm(hass, setup_integration, register_map):
    _, fake = await setup_integration(
        register_map, raw={"status_get": 7, "alarms_get": 0}
    )
    eid = entity_id(hass, "button", "allarm_reset_set")
    assert hass.states.get(eid).state == STATE_UNAVAILABLE

    await hass.services.async_call(
        "button", "press", {ATTR_ENTITY_ID: eid}, blocking=True
    )
    assert fake.writes == []

    fake.set_raw("status_get", 12)
    fake.set_raw("alarms_get", 6)
    await hass.config_entries.async_entries(DOMAIN)[0].runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(eid).state != STATE_UNAVAILABLE

    await hass.services.async_call(
        "button", "press", {ATTR_ENTITY_ID: eid}, blocking=True
    )
    assert fake.writes == [{"allarm_reset_set": 0}]


async def test_alarm_reset_unavailable_on_read_error(
    hass, setup_integration, register_map
):
    await setup_integration(register_map, raw={"status_get": 0x8000})
    eid = entity_id(hass, "button", "allarm_reset_set")
    assert hass.states.get(eid).state == STATE_UNAVAILABLE


async def test_load_pellets_only_when_off(hass, setup_integration, register_map):
    _, fake = await setup_integration(register_map, raw={"status_get": 7})
    eid = entity_id(hass, "button", "load_pellet_set")
    assert hass.states.get(eid).state == STATE_UNAVAILABLE

    await hass.services.async_call(
        "button", "press", {ATTR_ENTITY_ID: eid}, blocking=True
    )
    assert fake.writes == []

    fake.set_raw("status_get", 0)
    await hass.config_entries.async_entries(DOMAIN)[0].runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(eid).state != STATE_UNAVAILABLE

    await hass.services.async_call(
        "button", "press", {ATTR_ENTITY_ID: eid}, blocking=True
    )
    # Default duration: the register map maximum
    assert fake.writes == [{"load_pellet_set": 100}]


async def test_load_pellets_unavailable_on_read_error(
    hass, setup_integration, register_map
):
    await setup_integration(register_map, raw={"status_get": 0x8000})
    eid = entity_id(hass, "button", "load_pellet_set")
    assert hass.states.get(eid).state == STATE_UNAVAILABLE


# Chrono program service


async def test_set_chrono_program_single_request(hass, setup_integration, register_map):
    _, fake = await setup_integration(register_map)
    await hass.services.async_call(
        DOMAIN,
        "set_chrono_program",
        {
            ATTR_ENTITY_ID: climate_id(hass),
            "program": 2,
            "start": "07:00:00",
            "stop": "23:50:00",
            "power": 0,
            "temperature": 19.5,
            "days": ["saturday", "sunday"],
        },
        blocking=True,
    )
    assert len(fake.writes) == 1
    assert fake.writes[0] == {
        "chrono_p2_start_set": 42,
        "chrono_p2_stop_set": 143,
        "chrono_p2_power_set": 0,
        "chrono_p2_temperature_set": 39,
        "chrono_p2_day_monday_set": 0,
        "chrono_p2_day_tuesday_set": 0,
        "chrono_p2_day_wednesday_set": 0,
        "chrono_p2_day_thursday_set": 0,
        "chrono_p2_day_friday_set": 0,
        "chrono_p2_day_saturday_set": 1,
        "chrono_p2_day_sunday_set": 1,
    }


async def test_set_chrono_program_partial(hass, setup_integration, register_map):
    """Fields left out are not written, so no read value is ever written back."""
    _, fake = await setup_integration(
        register_map,
        raw={"chrono_p1_start_set": 0x8000, "chrono_p1_day_monday_set": 0x8000},
    )
    await hass.services.async_call(
        DOMAIN,
        "set_chrono_program",
        {ATTR_ENTITY_ID: climate_id(hass), "program": 1, "temperature": 21},
        blocking=True,
    )
    assert fake.writes == [{"chrono_p1_temperature_set": 42}]


async def test_set_chrono_program_empty_days(hass, setup_integration, register_map):
    _, fake = await setup_integration(register_map)
    await hass.services.async_call(
        DOMAIN,
        "set_chrono_program",
        {ATTR_ENTITY_ID: climate_id(hass), "program": 3, "days": []},
        blocking=True,
    )
    assert fake.writes == [{f"chrono_p3_day_{d}_set": 0 for d in WEEKDAYS}]


@pytest.mark.parametrize(
    "fields",
    [
        {"program": 1, "temperature": 40.5},
        {"program": 1, "temperature": 6.5},
        {"program": 1, "power": 6},
        {"program": 1, "power": -1},
        {"program": 5, "temperature": 20},
        {"program": 1, "days": ["funday"]},
        {"program": 1},
    ],
)
async def test_set_chrono_program_rejected(
    hass, setup_integration, register_map, fields
):
    _, fake = await setup_integration(register_map)
    with pytest.raises((HomeAssistantError, vol.Invalid)):
        await hass.services.async_call(
            DOMAIN,
            "set_chrono_program",
            {ATTR_ENTITY_ID: climate_id(hass), **fields},
            blocking=True,
        )
    assert fake.writes == []


async def test_set_chrono_program_missing_map(hass, setup_integration, register_map):
    stripped = {k: r for k, r in register_map.items() if not k.startswith("chrono_")}
    _, fake = await setup_integration(stripped)
    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            "set_chrono_program",
            {ATTR_ENTITY_ID: climate_id(hass), "program": 1, "temperature": 20},
            blocking=True,
        )
    assert fake.writes == []


# Pellet load duration


async def test_no_brazier_cleaning_switch(hass, setup_integration, register_map):
    """The stove sets the flag back on its own: it is not a command."""
    await setup_integration(register_map)
    assert entity_id(hass, "switch", "cleaning_brazier_set") is None
    assert entity_id(hass, "binary_sensor", "w_p_braciere_get") is not None


async def test_load_duration_bounds(hass, setup_integration, register_map):
    await setup_integration(register_map, raw={"load_pellet_max": 200})
    eid = entity_id(hass, "number", "load_pellet_duration")
    state = hass.states.get(eid)
    # Bounded by load_pellet_set (0-100), not by load_pellet_max (200)
    assert state.attributes["min"] == 1
    assert state.attributes["max"] == 100
    assert float(state.state) == 100
    assert state.attributes["unit_of_measurement"] == "s"

    er_entry = er.async_get(hass).async_get(eid)
    assert er_entry.entity_category is EntityCategory.CONFIG

    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "number",
            "set_value",
            {ATTR_ENTITY_ID: eid, "value": 200},
            blocking=True,
        )


async def test_load_duration_not_written_until_press(
    hass, setup_integration, register_map
):
    _, fake = await setup_integration(register_map, raw={"status_get": 0})
    eid = entity_id(hass, "number", "load_pellet_duration")
    await hass.services.async_call(
        "number",
        "set_value",
        {ATTR_ENTITY_ID: eid, "value": 60},
        blocking=True,
    )
    assert float(hass.states.get(eid).state) == 60
    assert fake.writes == []

    await hass.services.async_call(
        "button",
        "press",
        {ATTR_ENTITY_ID: entity_id(hass, "button", "load_pellet_set")},
        blocking=True,
    )
    assert fake.writes == [{"load_pellet_set": 60}]


async def test_load_duration_restored(hass, setup_integration, register_map):
    mock_restore_cache_with_extra_data(
        hass,
        (
            (
                State("number.stove_pellet_load_duration", "45"),
                {
                    "native_value": 45,
                    "native_min_value": 1,
                    "native_max_value": 100,
                    "native_step": 1,
                    "native_unit_of_measurement": "s",
                },
            ),
        ),
    )
    _, fake = await setup_integration(register_map, raw={"status_get": 0})
    eid = entity_id(hass, "number", "load_pellet_duration")
    assert eid == "number.stove_pellet_load_duration"
    assert float(hass.states.get(eid).state) == 45

    await hass.services.async_call(
        "button",
        "press",
        {ATTR_ENTITY_ID: entity_id(hass, "button", "load_pellet_set")},
        blocking=True,
    )
    assert fake.writes == [{"load_pellet_set": 45}]
