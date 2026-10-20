import numbers
from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.util import dt

from .const import CLOCK_DRIFT_SENSOR, CLOCK_KEYS, DOMAIN, SENSORS


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = config_entry.runtime_data
    agua = coordinator.agua

    sensors = []
    for device in agua.devices:
        hybrid = "power_wood_set" in device.registers

        for sensor in SENSORS:
            if (
                sensor.key in device.registers
                and (sensor.force_enabled or device.get_register_enabled(sensor.key))
                and (
                    (sensor.hybrid_only and hybrid)
                    or (sensor.hybrid_exclude and not hybrid)
                    or (not sensor.hybrid_only and not sensor.hybrid_exclude)
                )
            ):
                sensors.append(AguaIOTHeatingSensor(coordinator, device, sensor))

        if all(key in device.registers for key in CLOCK_KEYS):
            sensors.append(
                AguaIOTClockDriftSensor(coordinator, device, CLOCK_DRIFT_SENSOR)
            )

    async_add_entities(sensors, True)


class AguaIOTHeatingSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity"""

    _attr_has_entity_name = True

    def __init__(self, coordinator, device, description):
        """Initialize the thermostat."""
        super().__init__(coordinator)
        self._device = device
        self.entity_description = description

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._device.id_device}_{self.entity_description.key}"

    @property
    def name(self):
        """Return the name of the device, if any."""
        return self.entity_description.name

    @property
    def device_info(self):
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.id_device)},
            name=self._device.name,
            manufacturer="Micronova",
            model=self._device.name_product,
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.entity_description.raw_value:
            return self._device.get_register_value(self.entity_description.key)
        else:
            value = self._device.get_register_value_description(
                self.entity_description.key
            )
            # Do not return a description if the sensor expects a number
            if not self.entity_description.native_unit_of_measurement or isinstance(
                value, numbers.Number
            ):
                return value

    @property
    def extra_state_attributes(self):
        """Expose plain value as extra attribute when needed."""
        if (
            not self.entity_description.raw_value
            and self._device.get_register_value_options(self.entity_description.key)
        ):
            return {
                "raw_value": self._device.get_register_value(
                    self.entity_description.key
                ),
            }

    @property
    def options(self):
        if self.entity_description.device_class == SensorDeviceClass.ENUM:
            options = sorted(
                set(
                    self._device.get_register_value_options(
                        self.entity_description.key
                    ).values()
                )
            )
            cur_value = self._device.get_register_value_description(
                self.entity_description.key
            )
            if cur_value not in options:
                options.append(cur_value)

            return options


class AguaIOTClockDriftSensor(AguaIOTHeatingSensor):
    """Difference between the stove clock and the Home Assistant clock"""

    @property
    def native_value(self):
        """Return the stove clock drift in minutes."""
        hour, minute, day, month, year = (
            self._device.get_register_value_bcd(key) for key in CLOCK_KEYS
        )
        if None in (hour, minute, day, month, year):
            return None

        now = dt.now()
        try:
            stove_time = datetime(
                int(year),
                int(month),
                int(day),
                int(hour),
                int(minute),
                tzinfo=now.tzinfo,
            )
        except ValueError:
            return None

        return round(
            (stove_time - now.replace(second=0, microsecond=0)).total_seconds() / 60
        )

    @property
    def extra_state_attributes(self):
        return None
