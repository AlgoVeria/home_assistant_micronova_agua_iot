import json
import os

import pytest

from tests.helpers import aguaiot, build_device_from_fixture

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")


def load_all_fixtures():
    fixtures = {}
    for fname in sorted(os.listdir(FIXTURES_DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(FIXTURES_DIR, fname)
        with open(path) as f:
            fixtures[fname.replace(".json", "")] = json.load(f)
    return fixtures


@pytest.fixture(scope="session")
def fixture_data():
    return load_all_fixtures()


@pytest.fixture
def fixture_names(fixture_data):
    return sorted(fixture_data.keys())


@pytest.fixture
def aguaiot_mock():
    inst = aguaiot(
        api_url="https://example.com",
        customer_code="000000",
        email="test@example.com",
        password="test",
        unique_id="test-uuid",
    )
    return inst


@pytest.fixture
def devices_from_fixtures(aguaiot_mock, fixture_data):
    devices = {}
    for name, reg_map in fixture_data.items():
        devices[name] = build_device_from_fixture(aguaiot_mock, name, reg_map)
    return devices


try:
    import pytest_homeassistant_custom_component  # noqa: F401
except ImportError:
    # Home Assistant tests need pytest-homeassistant-custom-component (Linux/macOS)
    collect_ignore = ["ha"]
