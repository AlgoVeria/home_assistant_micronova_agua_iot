"""Agua IOT constants."""

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.button import ButtonEntityDescription
from homeassistant.components.climate import (
    ClimateEntityDescription,
)
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntityDescription,
)
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntityDescription,
)
from homeassistant.components.time import TimeEntityDescription
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
    Platform,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)

from .chrono import WEEKDAYS


@dataclass
class AguaIOTBinarySensorEntityDescription(BinarySensorEntityDescription):
    force_enabled: bool = False
    hybrid_only: bool = False
    icon_on: str | None = None


@dataclass
class AguaIOTSensorEntityDescription(SensorEntityDescription):
    force_enabled: bool = False
    hybrid_only: bool = False
    hybrid_exclude: bool = False
    raw_value: bool = False


@dataclass
class AguaIOTNumberEntityDescription(NumberEntityDescription):
    force_enabled: bool = False
    hybrid_only: bool = False
    hybrid_exclude: bool = False


@dataclass
class AguaIOTSwitchEntityDescription(SwitchEntityDescription):
    force_enabled: bool = False


@dataclass
class AguaIOTButtonEntityDescription(ButtonEntityDescription):
    press_value: int = 0
    # Stove states (status_get values) in which the button can be pressed
    status_values: tuple[int, ...] | None = None
    alarm_required: bool = False


@dataclass
class AguaIOTCanalizationEntityDescription(ClimateEntityDescription):
    key_temp_set: str | None = None
    key_temp_get: str | None = None
    key_temp2_get: str | None = None
    key_vent_set: str | None = None
    key_enable: str | None = None
    key2_enable: str | None = None


DOMAIN = "aguaiot"
CONF_API_URL = "api_url"
CONF_CUSTOMER_CODE = "customer_code"
CONF_LOGIN_API_URL = "login_api_url"
CONF_UUID = "uuid"
CONF_ENDPOINT = "endpoint"
CONF_BRAND_ID = "brand_id"
CONF_BRAND = "brand"
CONF_LANGUAGE = "language"
CONF_AIR_TEMP_FIX = "air_temp_fix"
CONF_READING_ERROR_FIX = "reading_error_fix"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_HTTP_TIMEOUT = "http_timeout"
CONF_BUFFER_READ_TIMEOUT = "buffer_read_timeout"
CONF_CONNECTION_MODE = "connection_mode"
CONF_BLE_BOOTSTRAP_DEVICES = "ble_bootstrap_devices"
CONF_BLE_SERVICE_UUID = "ble_service_uuid"
CONF_BLE_CHAR_UUID = "ble_char_uuid"

CONNECTION_MODE_CLOUD = "connection_cloud"
CONNECTION_MODE_BLUETOOTH = "connection_bluetooth"

AIR_VARIANTS = ["air", "air2", "air3", "air_palm"]
WATER_VARIANTS = ["water", "water_boiler", "water_puffer", "h2o", "h2o_mandata"]

MODE_WOOD = "Wood"
MODE_PELLETS = "Pellet"

STATUS_OFF = ["OFF", "FINAL CLEANING", "STOP", "SHUT OFF", "0", "6"]
STATUS_IDLE = [
    "ECO STOP",
    "STANDBY",
    "STAND BY",
    "STAND-BY",
    "ALARM",
    "MEMORY ALARM",
    "ALARM MEMORY",
    "MEM.ALM",
    "MEM. ALARM",
    "7",
    "8",
    "9",
]

PLATFORMS = [
    Platform.CLIMATE,
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.BUTTON,
    Platform.TIME,
]

# Highest chrono program number found in the cloud register maps
CHRONO_PROGRAMS = range(1, 7)

ENDPOINTS = {
    "Alfapalm": {
        CONF_CUSTOMER_CODE: "862148",
        CONF_API_URL: "https://alfaplam.agua-iot.com",
    },
    "APP-O BIOEN": {
        CONF_CUSTOMER_CODE: "289982",
        CONF_API_URL: "https://unical.agua-iot.com",
    },
    "Boreal Home": {
        CONF_CUSTOMER_CODE: "173118",
        CONF_API_URL: "https://boreal.agua-iot.com",
    },
    "Bronpi Home": {
        CONF_CUSTOMER_CODE: "164873",
        CONF_API_URL: "https://bronpi.agua-iot.com",
    },
    "Darwin Evolution": {
        CONF_CUSTOMER_CODE: "475219",
        CONF_API_URL: "https://cola.agua-iot.com",
    },
    "Easy Connect": {
        CONF_CUSTOMER_CODE: "354924",
        CONF_API_URL: "https://remote.mcz.it",
    },
    "Easy Connect Plus": {
        CONF_CUSTOMER_CODE: "746318",
        CONF_API_URL: "https://remote.mcz.it",
    },
    "Easy Connect Poêle": {
        CONF_CUSTOMER_CODE: "354925",
        CONF_API_URL: "https://remote.mcz.it",
    },
    "Elcofire Pellet Home": {
        CONF_CUSTOMER_CODE: "132679",
        CONF_API_URL: "https://elcofire.agua-iot.com",
    },
    "Elfire Wifi": {
        CONF_CUSTOMER_CODE: "402762",
        CONF_API_URL: "https://elfire.agua-iot.com",
    },
    "EOSS Wifi": {
        CONF_CUSTOMER_CODE: "326495",
        CONF_API_URL: "https://solartecnik.agua-iot.com",
    },
    "EvaCalòr - PuntoFuoco": {
        CONF_CUSTOMER_CODE: "635987",
        CONF_API_URL: "https://evastampaggi.agua-iot.com",
    },
    "Fontana Forni": {
        CONF_CUSTOMER_CODE: "505912",
        CONF_API_URL: "https://fontanaforni.agua-iot.com",
    },
    "Fonte Flamme contrôle 1": {
        CONF_CUSTOMER_CODE: "848324",
        CONF_API_URL: "https://fonteflame.agua-iot.com",
    },
    "Globe-fire": {
        CONF_CUSTOMER_CODE: "634876",
        CONF_API_URL: "https://globefire.agua-iot.com",
    },
    "GO HEAT": {
        CONF_CUSTOMER_CODE: "859435",
        CONF_API_URL: "https://amg.agua-iot.com",
    },
    "Jolly Mec Wi Fi": {
        CONF_CUSTOMER_CODE: "732584",
        CONF_API_URL: "https://jollymec.agua-iot.com",
    },
    "Karmek Wifi": {
        CONF_CUSTOMER_CODE: "403873",
        CONF_API_URL: "https://karmekone.agua-iot.com",
    },
    "Klover Home": {
        CONF_CUSTOMER_CODE: "143789",
        CONF_API_URL: "https://klover.agua-iot.com",
    },
    "LAMINOX Remote Control (2.0)": {
        CONF_CUSTOMER_CODE: "352678",
        CONF_API_URL: "https://laminox.agua-iot.com",
    },
    "Lorflam Home": {
        CONF_CUSTOMER_CODE: "121567",
        CONF_API_URL: "https://lorflam.agua-iot.com",
    },
    "Moretti design": {
        CONF_CUSTOMER_CODE: "624813",
        CONF_API_URL: "https://moretti.agua-iot.com",
    },
    "My Corisit": {
        CONF_CUSTOMER_CODE: "101427",
        CONF_API_URL: "https://mycorisit.agua-iot.com",
    },
    "MyPiazzetta": {
        CONF_CUSTOMER_CODE: "458632",
        CONF_API_URL: "https://piazzetta.agua-iot.com",
        CONF_LOGIN_API_URL: "https://piazzetta-iot.app2cloud.it/api/bridge/endpoint/",
    },
    "MySuperior": {
        CONF_CUSTOMER_CODE: "458632",
        CONF_API_URL: "https://piazzetta.agua-iot.com",
        CONF_LOGIN_API_URL: "https://piazzetta-iot.app2cloud.it/api/bridge/endpoint/",
        CONF_BRAND_ID: "2",
        CONF_BRAND: "superior",
    },
    "Nina": {
        CONF_CUSTOMER_CODE: "999999",
        CONF_API_URL: "https://micronova.agua-iot.com",
    },
    "Nobis-Fi": {
        CONF_CUSTOMER_CODE: "700700",
        CONF_API_URL: "https://nobis.agua-iot.com",
    },
    "Nordic Fire 2.0": {
        CONF_CUSTOMER_CODE: "132678",
        CONF_API_URL: "https://nordicfire.agua-iot.com",
    },
    "Ravelli Wi-Fi": {
        CONF_CUSTOMER_CODE: "953712",
        CONF_API_URL: "https://ravelli.agua-iot.com",
    },
    "Stufe a pellet Italia": {
        CONF_CUSTOMER_CODE: "015142",
        CONF_API_URL: "https://stufepelletitalia.agua-iot.com",
    },
    "Thermoflux": {
        CONF_CUSTOMER_CODE: "391278",
        CONF_API_URL: "https://thermoflux.agua-iot.com",
    },
    "Total Control 3.0 (Extraflame)": {
        CONF_CUSTOMER_CODE: "195764",
        CONF_API_URL: "https://extraflame.agua-iot.com/",
    },
    "TS Smart": {
        CONF_CUSTOMER_CODE: "046629",
        CONF_API_URL: "https://timsistem.agua-iot.com",
    },
    "TurboFonte": {
        CONF_CUSTOMER_CODE: "354924",
        CONF_API_URL: "https://remote.mcz.it",
        CONF_BRAND_ID: "2",
        CONF_BRAND: "turbofonte",
    },
    "Wi-Phire": {
        CONF_CUSTOMER_CODE: "521228",
        CONF_API_URL: "https://lineavz.agua-iot.com",
    },
}

BINARY_SENSORS = (
    AguaIOTBinarySensorEntityDescription(
        key="ris_pellet_ris_get",
        name="Pellets Depleted",
        icon="mdi:fire",
        icon_on="mdi:fire-alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    AguaIOTBinarySensorEntityDescription(
        key="popup_riserva_wood_get",
        name="Wood Reserve",
        icon="mdi:fire",
        icon_on="mdi:fire-alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        force_enabled=True,
    ),
    AguaIOTBinarySensorEntityDescription(
        key="thermostat_contact_get",
        name="External Thermostat",
        icon="mdi:electric-switch",
        icon_on="mdi:electric-switch-closed",
    ),
    AguaIOTBinarySensorEntityDescription(
        key="thermostat_contact_rear_get",
        name="External Thermostat Rear",
        icon="mdi:electric-switch",
        icon_on="mdi:electric-switch-closed",
    ),
    # The enable registers of these flags mirror the flag itself
    AguaIOTBinarySensorEntityDescription(
        key="w_p_braciere_get",
        name="Brazier Cleaning Warning",
        icon="mdi:fire",
        icon_on="mdi:fire-alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        force_enabled=True,
    ),
    AguaIOTBinarySensorEntityDescription(
        key="w_spegnimento_get",
        name="Waiting For Shutdown",
        icon="mdi:power-sleep",
        force_enabled=True,
    ),
)

SENSORS = (
    AguaIOTSensorEntityDescription(
        key="status_get",
        name="Status",
        icon="mdi:fire",
        native_unit_of_measurement=None,
        state_class=None,
        device_class=SensorDeviceClass.ENUM,
    ),
    AguaIOTSensorEntityDescription(
        key="alarms_get",
        name="Alarm",
        icon="mdi:alert-outline",
        native_unit_of_measurement=None,
        state_class=None,
        device_class=SensorDeviceClass.ENUM,
        force_enabled=True,
    ),
    AguaIOTSensorEntityDescription(
        key="real_power_get",
        name="Real Power",
        icon="mdi:gauge",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        force_enabled=True,
        raw_value=True,
        hybrid_exclude=True,
    ),
    AguaIOTSensorEntityDescription(
        key="real_power_get",
        name="Real Pellet Power",
        icon="mdi:gauge",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        force_enabled=True,
        raw_value=True,
        hybrid_only=True,
    ),
    AguaIOTSensorEntityDescription(
        key="real_power_wood_get",
        name="Real Wood Power",
        icon="mdi:gauge",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        force_enabled=True,
        hybrid_only=True,
        raw_value=True,
    ),
    AguaIOTSensorEntityDescription(
        key="vent_front2_get",
        name="Real Vent Front",
        icon="mdi:fan",
        native_unit_of_measurement=None,
        state_class=None,
        device_class=SensorDeviceClass.ENUM,
    ),
    AguaIOTSensorEntityDescription(
        key="vent_rear2_get",
        name="Real Vent Rear",
        icon="mdi:fan",
        native_unit_of_measurement=None,
        state_class=None,
        device_class=SensorDeviceClass.ENUM,
    ),
    AguaIOTSensorEntityDescription(
        key="type_combustible_get",
        name="Fuel",
        icon="mdi:gas-burner",
        native_unit_of_measurement=None,
        state_class=None,
        device_class=SensorDeviceClass.ENUM,
    ),
    AguaIOTSensorEntityDescription(
        key="pres_h2o_get",
        name="Water Pressure",
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
    ),
    AguaIOTSensorEntityDescription(
        key="pascal_get",
        name="Brazier Pressure",
        native_unit_of_measurement=UnitOfPressure.PA,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PRESSURE,
    ),
    AguaIOTSensorEntityDescription(
        key="giri_estrattore_get",
        name="Extractor Fan",
        icon="mdi:fan",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=None,
    ),
    AguaIOTSensorEntityDescription(
        key="pomp_h2o_get",
        name="Water Pump",
        icon="mdi:pump",
        native_unit_of_measurement=None,
        state_class=None,
        device_class=None,
    ),
    # Temperature sensors
    AguaIOTSensorEntityDescription(
        key="temp_gas_flue_get",
        name="Smoke Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_probe_k_get",
        name="Flame Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_air_get",
        name="Air Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_air2_get",
        name="Air Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_air3_get",
        name="Air Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_air_palm_get",
        name="Remote Air Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_rear2_get",
        name="Vent Rear Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_front2_get",
        name="Vent Front Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_water_get",
        name="Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_water_boiler_get",
        name="Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_water_puffer_get",
        name="Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_h2o_mandata_get",
        name="Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_h2o_get",
        name="Water Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="temp_legna_get",
        name="Wood Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    AguaIOTSensorEntityDescription(
        key="pellet_level_get",
        name="Pellet Level",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:percent",
    ),
    AguaIOTSensorEntityDescription(
        key="p_quality_p12_get",
        name="Pellet Quality",
        icon="mdi:quality-high",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=None,
    ),
    AguaIOTSensorEntityDescription(
        key="c_quality_p12_get",
        name="Combustion Quality",
        icon="mdi:fire-circle",
        native_unit_of_measurement=None,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=None,
    ),
    AguaIOTSensorEntityDescription(
        key="ore_lavoro_tot_get",
        name="Total Hours",
        icon="mdi:clock-outline",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.DURATION,
    ),
    AguaIOTSensorEntityDescription(
        key="ore_lavoro_par_get",
        name="Partial Hours",
        icon="mdi:clock-outline",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.DURATION,
    ),
    AguaIOTSensorEntityDescription(
        key="ore_service_get",
        name="Service Hours",
        icon="mdi:wrench-clock",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.DURATION,
    ),
    AguaIOTSensorEntityDescription(
        key="ore_service_soglia_get",
        name="Threshold Service Hours",
        icon="mdi:wrench-clock",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
    ),
    # The load pellet enable register depends on the stove state
    AguaIOTSensorEntityDescription(
        key="load_pellet_get",
        name="Pellet Load Progress",
        icon="mdi:progress-download",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        force_enabled=True,
        raw_value=True,
    ),
    AguaIOTSensorEntityDescription(
        key="load_pellet_max",
        name="Pellet Load Maximum",
        icon="mdi:progress-download",
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        force_enabled=True,
        raw_value=True,
    ),
)

# Keys needed for the stove clock drift sensor
CLOCK_KEYS = (
    "clock_hour_set",
    "clock_minute_set",
    "calendar_day_set",
    "calendar_month_set",
    "calendar_year_set",
)

CLOCK_DRIFT_SENSOR = SensorEntityDescription(
    key="clock_drift",
    name="Clock Drift",
    icon="mdi:clock-alert-outline",
    native_unit_of_measurement=UnitOfTime.MINUTES,
    device_class=SensorDeviceClass.DURATION,
    state_class=SensorStateClass.MEASUREMENT,
    entity_category=EntityCategory.DIAGNOSTIC,
)

SWITCHES = (
    SwitchEntityDescription(
        key="natural_mode_manual_set",
        name="Natural Mode",
        icon="mdi:fan-off",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    SwitchEntityDescription(
        key="standby_set",
        name="Standby",
        icon="mdi:power-standby",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    SwitchEntityDescription(
        key="fun_auto_set",
        name="Auto Mode",
        icon="mdi:fan-auto",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    SwitchEntityDescription(
        key="fun_pwf_set",
        name="Powerful Mode",
        icon="mdi:speedometer",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    SwitchEntityDescription(
        key="eco_stop_set",
        name="ECO Stop",
        icon="mdi:leaf-off",
        device_class=SwitchDeviceClass.SWITCH,
    ),
    AguaIOTSwitchEntityDescription(
        key="cleaning_brazier_set",
        name="Brazier Cleaning",
        icon="mdi:broom",
        device_class=SwitchDeviceClass.SWITCH,
        # The enable register mirrors the flag itself
        force_enabled=True,
    ),
    AguaIOTSwitchEntityDescription(
        key="chrono_general_enable_set",
        name="Chrono",
        icon="mdi:calendar-clock",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
    AguaIOTSwitchEntityDescription(
        key="chrono_week_enable_set",
        name="Chrono Weekly",
        icon="mdi:calendar-week",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
    *(
        AguaIOTSwitchEntityDescription(
            key=f"chrono_p{program}_enable_set",
            name=f"Chrono P{program}",
            icon="mdi:calendar-clock",
            device_class=SwitchDeviceClass.SWITCH,
            entity_category=EntityCategory.CONFIG,
        )
        for program in CHRONO_PROGRAMS
    ),
    *(
        AguaIOTSwitchEntityDescription(
            key=f"chrono_p{program}_day_{day}_set",
            name=f"Chrono P{program} {day.capitalize()}",
            icon="mdi:calendar-today",
            device_class=SwitchDeviceClass.SWITCH,
            entity_category=EntityCategory.CONFIG,
            entity_registry_enabled_default=False,
        )
        for program in CHRONO_PROGRAMS
        for day in WEEKDAYS
    ),
)

NUMBERS = (
    AguaIOTNumberEntityDescription(
        key="es_air_start_set",
        name="Energy Saving Start",
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
    ),
    AguaIOTNumberEntityDescription(
        key="es_air_stop_set",
        name="Energy Saving Stop",
        native_step=1,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
    ),
    AguaIOTNumberEntityDescription(
        key="power_set",
        name="Power",
        icon="mdi:fire",
        native_step=1,
        force_enabled=True,
        hybrid_exclude=True,
    ),
    AguaIOTNumberEntityDescription(
        key="power_set",
        name="Pellet Power",
        icon="mdi:fire",
        native_step=1,
        force_enabled=True,
        hybrid_only=True,
    ),
    AguaIOTNumberEntityDescription(
        key="power_wood_set",
        name="Wood Power",
        icon="mdi:fire",
        native_step=1,
        hybrid_only=True,
    ),
    AguaIOTNumberEntityDescription(
        key="eco_temp_stop",
        name="ECO Stop Time",
        native_step=1,
        native_unit_of_measurement="min",
        native_min_value=0,
        native_max_value=30,
        force_enabled=True,
    ),
    AguaIOTNumberEntityDescription(
        key="p_quality_p12_set",
        name="Pellet Quality",
        icon="mdi:quality-high",
        native_step=1,
    ),
    AguaIOTNumberEntityDescription(
        key="c_quality_p12_set",
        name="Combustion Quality",
        icon="mdi:fire-circle",
        native_step=1,
    ),
    AguaIOTNumberEntityDescription(
        key="probe_correct_set",
        name="Room Probe Correction",
        icon="mdi:thermometer-plus",
        native_step=0.5,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.CONFIG,
    ),
    # Step follows the register formula (1 °C, or 0.5 °C for '#/2')
    *(
        AguaIOTNumberEntityDescription(
            key=f"chrono_p{program}_temperature_set",
            name=f"Chrono P{program} Temperature",
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=NumberDeviceClass.TEMPERATURE,
            entity_category=EntityCategory.CONFIG,
        )
        for program in CHRONO_PROGRAMS
    ),
)

CLIMATE_CANALIZATIONS = (
    AguaIOTCanalizationEntityDescription(
        name="Multifire {id}",
        key=r"multifire_(?P<id>\d+)(_\d+)?_set",
        icon="mdi:fan",
    ),
    AguaIOTCanalizationEntityDescription(
        name="Canalization {id}",
        key=r"canalization_(?P<id>[a-zA-Z0-9]+)_set",
        key_enable="canalization_{id}_enable",
        key2_enable="canalization_2{id}_enable",
        key_temp_set="canalization_{id}_temp_air_set",
        key_temp_get="canalization_{id}_temp_air_get",
        key_temp2_get="canalization_2{id}_temp_air_get",
        key_vent_set="canalization_{id}_vent_set",
        icon="mdi:fan",
    ),
    AguaIOTCanalizationEntityDescription(
        name="Canalization Single",
        key=r"canalization_single_vent_set",
        icon="mdi:fan",
    ),
    AguaIOTCanalizationEntityDescription(
        name="Vent {id}",
        key=r"vent_(?P<id>(front|rear))_set",
        key_enable="vent_{id}_enable",
        key2_enable="vent_{id}2_enable",
        key_temp_set="temp_{id}_set",
        key_temp_get="temp_{id}_get",
        key_temp2_get="temp_{id}2_get",
        icon="mdi:fan",
    ),
    AguaIOTCanalizationEntityDescription(
        name="Vent {id}",
        key=r"vent_(?!(front|rear))(?P<id>\w+)_set",
        key_temp_set="temp_{id}_set",
        key_temp_get="temp_{id}_get",
        icon="mdi:fan",
    ),
    AguaIOTCanalizationEntityDescription(
        name="Sweet Air",
        key="vent_front_sweetair_set",
        icon="mdi:fan",
    ),
    AguaIOTCanalizationEntityDescription(
        name="Sweet Air {id}",
        key=r"sweetair_(?P<id>\d+)(_\d+)?_set",
        icon="mdi:fan",
    ),
)

SELECTS = (
    SelectEntityDescription(
        key="fan_mode_set",
        name="Fan Mode",
        icon="mdi:fan",
    ),
    SelectEntityDescription(
        key="fan2_mode_set",
        name="Fan Mode",
        icon="mdi:fan",
    ),
    *(
        SelectEntityDescription(
            key=f"chrono_p{program}_power_set",
            name=f"Chrono P{program} Power",
            icon="mdi:fire",
            entity_category=EntityCategory.CONFIG,
        )
        for program in CHRONO_PROGRAMS
    ),
)

BUTTONS = (
    AguaIOTButtonEntityDescription(
        key="allarm_reset_set",
        name="Reset Alarm",
        icon="mdi:alarm-light-off-outline",
        press_value=0,
        alarm_required=True,
    ),
    AguaIOTButtonEntityDescription(
        key="load_pellet_set",
        name="Load Pellets",
        icon="mdi:arrow-down-bold-circle-outline",
        press_value=1,
        # Only when the stove is off
        status_values=(0,),
    ),
)

# Chrono start/stop registers, in 10-minute steps
TIMES = tuple(
    TimeEntityDescription(
        key=f"chrono_p{program}_{field}_set",
        name=f"Chrono P{program} {field.capitalize()}",
        icon="mdi:clock-outline",
        entity_category=EntityCategory.CONFIG,
    )
    for program in CHRONO_PROGRAMS
    for field in ("start", "stop")
)
