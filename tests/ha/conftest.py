"""Fixtures for tests running inside Home Assistant.

These tests need `pytest-homeassistant-custom-component`, which only runs on
Linux/macOS. They are skipped (not collected) when it is not installed.
"""

import copy
import json
import os
from unittest.mock import patch

import pytest
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.aguaiot.aguaiot import Device
from custom_components.aguaiot.const import (
    CONF_API_URL,
    CONF_CUSTOMER_CODE,
    CONF_UUID,
    DOMAIN,
)
from tests.helpers import compute_information_dict

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")
DEVICE_ID = "stove-1"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


def load_register_map(name):
    with open(os.path.join(FIXTURES_DIR, f"{name}.json")) as f:
        return json.load(f)


class FakeAgua:
    """Stand-in for the cloud client: serves a register map, records writes."""

    def __init__(self, register_map, **kwargs):
        self.register_map = copy.deepcopy(register_map)
        self.raw_data = compute_information_dict(self.register_map)
        self.reading_error_fix = kwargs.get("reading_error_fix", False)
        self.air_temp_fix = kwargs.get("air_temp_fix", False)
        self.language = "ENG"
        self.devices = []
        self.writes = []

    async def connect(self):
        self.devices = [
            Device(
                id=1,
                id_device=DEVICE_ID,
                id_product=1,
                product_serial="SERIAL",
                name="Stove",
                is_online=True,
                name_product="Test stove",
                id_registers_map=1,
                aguaiot=self,
                register_map=self.register_map,
            )
        ]
        self.rebuild()

    async def update(self):
        self.rebuild()

    async def _request_writing(self, device, items):
        self.writes.append(dict(items))

    def rebuild(self):
        for device in self.devices:
            device._Device__register_dict = device._Device__build_register_dict(
                self.raw_data
            )

    def set_raw(self, key, word):
        """Set the full word stored at the offset of a register."""
        self.raw_data[self.register_map[key]["offset"]] = word
        self.rebuild()


@pytest.fixture
def setup_integration(hass):
    """Return a coroutine setting up the integration with a register map."""

    async def _setup(register_map, raw=None):
        fake = FakeAgua(register_map)
        for key, word in (raw or {}).items():
            fake.raw_data[register_map[key]["offset"]] = word

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_API_URL: "https://example.invalid",
                CONF_CUSTOMER_CODE: "000000",
                CONF_EMAIL: "user@example.invalid",
                CONF_PASSWORD: "secret",
                CONF_UUID: "test-uuid",
            },
            options={},
        )
        entry.add_to_hass(hass)
        with patch("custom_components.aguaiot.coordinator.aguaiot", return_value=fake):
            assert await hass.config_entries.async_setup(entry.entry_id)
            await hass.async_block_till_done()
        return entry, fake

    return _setup
