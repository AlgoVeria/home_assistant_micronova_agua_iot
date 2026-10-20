"""Test the Device class using fixture data as simulated API responses."""

import pytest

from tests.helpers import AguaIOTError, build_device_from_fixture


class TestGetRegister:
    def test_all_registers_accessible(self, devices_from_fixtures, fixture_data):
        for name, reg_map in fixture_data.items():
            device = devices_from_fixtures[name]
            for reg_key in reg_map:
                register = reg_map[reg_key]
                if register.get("offset") is None:
                    continue
                reg = device.get_register(reg_key)
                assert reg is not None, f"{name}/{reg_key}: register not found"
                assert "value_raw" in reg, f"{name}/{reg_key}: missing value_raw"
                assert "value" in reg, f"{name}/{reg_key}: missing value"

    def test_computed_value_matches_fixture(self, devices_from_fixtures, fixture_data):
        for name, reg_map in fixture_data.items():
            device = devices_from_fixtures[name]
            for reg_key, expected in reg_map.items():
                if expected.get("offset") is None:
                    continue
                reg = device.get_register(reg_key)
                assert reg["value_raw"] == expected["value_raw"], (
                    f"{name}/{reg_key}: expected value_raw={expected['value_raw']}, "
                    f"got {reg['value_raw']}"
                )
                assert abs(float(reg["value"]) - float(expected["value"])) < 0.01, (
                    f"{name}/{reg_key}: expected value={expected['value']}, "
                    f"got {reg['value']}"
                )

    def test_register_with_division_formula(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        reg = device.get_register("temp_air_get")
        assert reg["value_raw"] == "33"
        assert reg["value"] == 16.5

        reg = device.get_register("temp_air_set")
        assert reg["value_raw"] == "44"
        assert reg["value"] == 22.0

    def test_register_with_offset_formula(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        reg = device.get_register("temp_gas_flue_get")
        assert reg["value_raw"] == "0"
        assert reg["value"] == 30

    def test_year_formula(self, devices_from_fixtures):
        device = devices_from_fixtures["alfaplam"]
        reg = device.get_register("calendar_year_set")
        assert reg["value_raw"] == "36"
        assert reg["value"] == 2036

    def test_registers_with_same_offset(self, devices_from_fixtures, fixture_data):
        device = devices_from_fixtures["go_heat"]
        reg1 = device.get_register("alarms_enable")
        reg2 = device.get_register("status_get")
        assert reg1["value_raw"] == reg2["value_raw"]


class TestGetRegisterValue:
    def test_returns_value(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        val = device.get_register_value("temp_air_get")
        assert val == 16.5

    def test_air_temp_fix_drops_high_values(self, aguaiot_mock):
        aguaiot_mock.air_temp_fix = True
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "temp_air_get": {
                    "reg_key": "temp_air_get",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "200",
                    "value": 200,
                }
            },
        )
        val = device.get_register_value("temp_air_get")
        assert val is None

    def test_air_temp_fix_keeps_normal_values(self, aguaiot_mock):
        aguaiot_mock.air_temp_fix = True
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "temp_air_get": {
                    "reg_key": "temp_air_get",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "50",
                    "value": 50,
                }
            },
        )
        val = device.get_register_value("temp_air_get")
        assert val == 50

    def test_reading_error_fix(self, aguaiot_mock):
        aguaiot_mock.reading_error_fix = True
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "status_get": {
                    "reg_key": "status_get",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "32768",
                    "value": 32768,
                }
            },
        )
        val = device.get_register_value("status_get")
        assert val is None

    @pytest.mark.parametrize(
        "formula,mask,formatted",
        [
            ("#", 65535, 32768),
            ("#/2", 65535, 16384),
            ("#+30", 65535, 32798),
            ("#", 255, 0),
        ],
    )
    def test_reading_error_fix_uses_raw_word(
        self, aguaiot_mock, formula, mask, formatted
    ):
        register_map = {
            "temp_get": {
                "reg_key": "temp_get",
                "offset": 1,
                "mask": mask,
                "formula": formula,
                "formula_inverse": "#",
            }
        }
        device = build_device_from_fixture(aguaiot_mock, "test", register_map)
        device._Device__register_dict = device._Device__build_register_dict({1: 32768})
        assert device.get_register("temp_get")["value"] == formatted

        # Without the fix the failed read is exposed as is
        assert device.get_register_value("temp_get") == formatted

        aguaiot_mock.reading_error_fix = True
        assert device.get_register_value("temp_get") is None

    def test_reading_error_fix_keeps_valid_masked_values(self, aguaiot_mock):
        aguaiot_mock.reading_error_fix = True
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "status_get": {
                    "reg_key": "status_get",
                    "offset": 1,
                    "mask": 255,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "0",
                    "value": 0,
                }
            },
        )
        assert device.get_register_value("status_get") == 0

    def test_air_temp_fix_only_affects_air_keys(self, aguaiot_mock):
        aguaiot_mock.air_temp_fix = True
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "temp_gas_flue_get": {
                    "reg_key": "temp_gas_flue_get",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "200",
                    "value": 200,
                }
            },
        )
        val = device.get_register_value("temp_gas_flue_get")
        assert val == 200


class TestGetRegisterValueDescription:
    def test_known_value_returns_description(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "status_managed_get": {
                    "reg_key": "status_managed_get",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "85",
                    "value": 85,
                    "enc_val": [
                        {"value": 85, "lang": "ENG", "description": "ON"},
                        {"value": 170, "lang": "ENG", "description": "OFF"},
                    ],
                }
            },
        )
        desc = device.get_register_value_description("status_managed_get", "ENG")
        assert desc == "ON"

    def test_unknown_value_returns_raw_value(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        desc = device.get_register_value_description("alarms_get")
        assert desc is not None

    def test_no_enc_val_returns_raw_value(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        desc = device.get_register_value_description("power_set")
        assert desc is not None

    def test_different_languages_same_value(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "status_managed_get": {
                    "reg_key": "status_managed_get",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "85",
                    "value": 85,
                    "enc_val": [
                        {"value": 85, "lang": "ENG", "description": "ON"},
                        {"value": 85, "lang": "ITA", "description": "ON"},
                        {"value": 170, "lang": "ENG", "description": "OFF"},
                    ],
                }
            },
        )
        desc_eng = device.get_register_value_description("status_managed_get", "ENG")
        desc_ita = device.get_register_value_description("status_managed_get", "ITA")
        assert desc_eng == desc_ita


class TestGetRegisterValueOptions:
    def test_returns_value_to_description_mapping(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        options = device.get_register_value_options("status_managed_get", "ENG")
        assert options[85] == "ON"
        assert options[170] == "OFF"

    def test_empty_when_no_enc_val(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        options = device.get_register_value_options("power_set")
        assert options == {}

    def test_returns_languages(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        langs = device.get_register_value_options_languages("status_managed_get")
        assert "ENG" in langs
        assert "ITA" in langs

    def test_empty_languages_when_no_enc_val(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        langs = device.get_register_value_options_languages("power_set")
        assert langs == set()

    def test_fallback_to_eng_when_language_missing(self, aguaiot_mock):
        aguaiot_mock.language = "XYZ"
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "status_get": {
                    "reg_key": "status_get",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "85",
                    "value": 85,
                    "enc_val": [
                        {"value": 85, "lang": "ENG", "description": "ON"},
                        {"value": 85, "lang": "ITA", "description": "ON"},
                        {"value": 170, "lang": "ENG", "description": "OFF"},
                        {"value": 170, "lang": "ITA", "description": "OFF"},
                    ],
                }
            },
        )
        options = device.get_register_value_options("status_get", "XYZ")
        del options
        desc = device.get_register_value_description("status_get", "XYZ")
        assert desc == "ON"


class TestGetRegisterEnabled:
    def test_disabled_when_value_not_in_enable_val(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        assert device.get_register_enabled("alarms_enable") is False

    def test_no_enable_key_returns_true(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        assert device.get_register_enabled("power_set") is True

    def test_enabled_with_single_enable_val(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "test_enable": {
                    "reg_key": "test_enable",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "0",
                    "value": 0,
                    "reg_type": "ENABLE",
                    "enable_val": [{"value": 0}],
                }
            },
        )
        assert device.get_register_enabled("test_enable") is True

    def test_enabled_with_matching_value(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "test_enable": {
                    "reg_key": "test_enable",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "3",
                    "value": 3,
                    "reg_type": "ENABLE",
                    "enable_val": [{"value": 1}, {"value": 2}, {"value": 3}],
                }
            },
        )
        assert device.get_register_enabled("test_enable") is True

    def test_disabled_when_no_match(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "test_enable": {
                    "reg_key": "test_enable",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "5",
                    "value": 5,
                    "reg_type": "ENABLE",
                    "enable_val": [{"value": 1}, {"value": 2}],
                }
            },
        )
        assert device.get_register_enabled("test_enable") is False

    def test_non_enable_reg_type_raises(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "test_set": {
                    "reg_key": "test_set",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "1",
                    "value": 1,
                    "reg_type": "SET",
                },
                "test_enable": {
                    "reg_key": "test_enable",
                    "offset": 2,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "value_raw": "1",
                    "value": 1,
                    "reg_type": "GET",
                },
            },
        )
        with pytest.raises(AguaIOTError):
            device.get_register_enabled("test_set")


class TestGetRegisterMinMax:
    def test_set_min_max(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        assert device.get_register_value_min("power_set") == 1
        assert device.get_register_value_max("power_set") == 5

    def test_temperature_min_max(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        assert device.get_register_value_min("temp_air_set") == 7
        assert device.get_register_value_max("temp_air_set") == 41


class TestPrepareValueForWriting:
    def test_identity(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "power_set": {
                    "reg_key": "power_set",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "set_min": 1,
                    "set_max": 5,
                    "is_hex": False,
                }
            },
        )
        assert device._Device__prepare_value_for_writing("power_set", 3) == 3

    def test_inverse_division(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "temp_air_set": {
                    "reg_key": "temp_air_set",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#/2",
                    "formula_inverse": "#*2",
                    "set_min": 0,
                    "set_max": 255,
                    "is_hex": False,
                }
            },
        )
        assert device._Device__prepare_value_for_writing("temp_air_set", 22) == 44

    def test_year_inverse(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "calendar_year_set": {
                    "reg_key": "calendar_year_set",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#+2000",
                    "formula_inverse": "#-2000",
                    "set_min": 2000,
                    "set_max": 2100,
                    "is_hex": False,
                }
            },
        )
        assert (
            device._Device__prepare_value_for_writing("calendar_year_set", 2023) == 23
        )

    def test_temperature_offset_inverse(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "temp_gas_flue_get": {
                    "reg_key": "temp_gas_flue_get",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#+30",
                    "formula_inverse": "#-30",
                    "set_min": 0,
                    "set_max": 255,
                    "is_hex": False,
                }
            },
        )
        assert device._Device__prepare_value_for_writing("temp_gas_flue_get", 50) == 20

    def test_out_of_range_raises(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "power_set": {
                    "reg_key": "power_set",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "set_min": 1,
                    "set_max": 5,
                    "is_hex": False,
                }
            },
        )
        with pytest.raises(ValueError):
            device._Device__prepare_value_for_writing("power_set", 99)

    def test_hex_conversion(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "calendar_day_set": {
                    "reg_key": "calendar_day_set",
                    "offset": 1,
                    "mask": 65535,
                    "formula": "#",
                    "formula_inverse": "#",
                    "set_min": 1,
                    "set_max": 31,
                    "is_hex": True,
                }
            },
        )
        assert device._Device__prepare_value_for_writing("calendar_day_set", 8) == int(
            "0x8", 16
        )


class TestRegistersProperty:
    def test_returns_all_register_keys(self, devices_from_fixtures, fixture_data):
        for name, reg_map in fixture_data.items():
            device = devices_from_fixtures[name]
            keys = device.registers
            assert len(keys) == len(reg_map)
            for key in reg_map:
                assert key in keys


class TestExportMethods:
    def test_export_register_map(self, devices_from_fixtures, fixture_data):
        for name, reg_map in fixture_data.items():
            device = devices_from_fixtures[name]
            exported = device.export_register_map()
            assert len(exported) == len(reg_map)
            for key in reg_map:
                assert key in exported

    def test_export_cache_contains_all_fields(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        cache = device.export_cache()
        assert cache["id_device"] == "go_heat"
        assert cache["name"] == "go_heat"
        assert "register_map" in cache
        assert "device_info" in cache
        assert "id" in cache
        assert cache["is_online"] is True


class TestDeviceInfoProperties:
    def test_ble_mac_returns_none_when_not_set(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        assert device.ble_mac is None

    def test_ble_security_code_returns_none(self, devices_from_fixtures):
        device = devices_from_fixtures["go_heat"]
        assert device.ble_security_code is None


def _register(key, value_raw, formula="#", formula_inverse="#", **extra):
    reg = {
        "reg_key": key,
        "offset": extra.pop("offset", 1),
        "mask": 65535,
        "formula": formula,
        "formula_inverse": formula_inverse,
        "set_min": 0,
        "set_max": 65535,
        "is_hex": False,
        "value_raw": str(value_raw),
    }
    reg.update(extra)
    return reg


class TestIsRegisterReadError:
    def test_read_error_detected_without_option(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {"chrono_p1_start_set": _register("chrono_p1_start_set", 32768)},
        )
        assert aguaiot_mock.reading_error_fix is False
        assert device.is_register_read_error("chrono_p1_start_set") is True

    def test_valid_read(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {"chrono_p1_start_set": _register("chrono_p1_start_set", 36)},
        )
        assert device.is_register_read_error("chrono_p1_start_set") is False

    def test_unknown_register(self, aguaiot_mock):
        device = build_device_from_fixture(aguaiot_mock, "test", {})
        assert device.is_register_read_error("chrono_p1_start_set") is False


class TestGetRegisterValueBcd:
    def test_hour(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {"clock_hour_set": _register("clock_hour_set", 0x19, is_hex=True)},
        )
        # Plain value is not decoded
        assert device.get_register_value("clock_hour_set") == 25
        assert device.get_register_value_bcd("clock_hour_set") == 19

    def test_year_formula_applied_after_decoding(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "calendar_year_set": _register(
                    "calendar_year_set",
                    0x26,
                    formula="#+2000",
                    formula_inverse="#-2000",
                    is_hex=True,
                )
            },
        )
        assert device.get_register_value_bcd("calendar_year_set") == 2026

    def test_not_hex_register(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {"calendar_day_week_set": _register("calendar_day_week_set", 2)},
        )
        assert device.get_register_value_bcd("calendar_day_week_set") == 2

    def test_read_error(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {"clock_hour_set": _register("clock_hour_set", 32768, is_hex=True)},
        )
        assert device.get_register_value_bcd("clock_hour_set") is None

    def test_invalid_bcd_digit(self, aguaiot_mock):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {"clock_hour_set": _register("clock_hour_set", 0x1A, is_hex=True)},
        )
        assert device.get_register_value_bcd("clock_hour_set") is None

    def test_missing_register(self, aguaiot_mock):
        device = build_device_from_fixture(aguaiot_mock, "test", {})
        assert device.get_register_value_bcd("clock_hour_set") is None


class TestChronoWriteLimits:
    @pytest.fixture
    def device(self, aguaiot_mock):
        return build_device_from_fixture(
            aguaiot_mock,
            "test",
            {
                "chrono_p1_temperature_set": _register(
                    "chrono_p1_temperature_set",
                    40,
                    formula="#/2",
                    formula_inverse="#*2",
                    set_min=7,
                    set_max=40,
                ),
                "probe_correct_set": _register(
                    "probe_correct_set",
                    9,
                    formula="(#-9)/2",
                    formula_inverse="(#*2 )+9",
                    set_min=-4.5,
                    set_max=4.5,
                    offset=2,
                ),
            },
        )

    def test_temperature_half_degree(self, device):
        assert device.get_register_value("chrono_p1_temperature_set") == 20
        prepare = device._Device__prepare_value_for_writing
        assert prepare("chrono_p1_temperature_set", 20.5) == 41
        assert prepare("chrono_p1_temperature_set", 7) == 14

    @pytest.mark.parametrize("value", [6.5, 40.5])
    def test_temperature_out_of_range(self, device, value):
        with pytest.raises(ValueError):
            device._Device__prepare_value_for_writing(
                "chrono_p1_temperature_set", value
            )

    def test_probe_correction(self, device):
        assert device.get_register_value("probe_correct_set") == 0
        prepare = device._Device__prepare_value_for_writing
        assert prepare("probe_correct_set", -4.5) == 0
        assert prepare("probe_correct_set", 1.5) == 12
        with pytest.raises(ValueError):
            prepare("probe_correct_set", 5)


class TestGetRegisterValueStep:
    @pytest.mark.parametrize(
        "formula,expected",
        [("#", 1), ("#/2", 0.5), ("(#-9)/2", 0.5), ("#+30", 1)],
    )
    def test_step_from_formula(self, aguaiot_mock, formula, expected):
        device = build_device_from_fixture(
            aguaiot_mock,
            "test",
            {"reg_set": _register("reg_set", 40, formula=formula)},
        )
        assert device.get_register_value_step("reg_set") == expected

    def test_missing_register(self, aguaiot_mock):
        device = build_device_from_fixture(aguaiot_mock, "test", {})
        assert device.get_register_value_step("reg_set") is None
