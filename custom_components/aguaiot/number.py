import logging

from homeassistant.components.number import NumberEntity, RestoreNumber
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .aguaiot import AguaIOTError
from .const import DOMAIN, LOAD_PELLET_DURATION, NUMBERS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = config_entry.runtime_data
    agua = coordinator.agua

    numbers = []
    for device in agua.devices:
        hybrid = "power_wood_set" in device.registers

        for number in NUMBERS:
            if (
                number.key in device.registers
                and (number.force_enabled or device.get_register_enabled(number.key))
                and (
                    (number.hybrid_only and hybrid)
                    or (number.hybrid_exclude and not hybrid)
                    or (not number.hybrid_only and not number.hybrid_exclude)
                )
            ):
                numbers.append(AguaIOTHeatingNumber(coordinator, device, number))

        if "load_pellet_set" in device.registers:
            numbers.append(
                AguaIOTLoadPelletDurationNumber(
                    coordinator, device, LOAD_PELLET_DURATION
                )
            )

    async_add_entities(numbers, True)


class AguaIOTHeatingNumber(CoordinatorEntity, NumberEntity):
    """Number entity"""

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
        return self._device.get_register_value(self.entity_description.key)

    @property
    def native_step(self):
        if self.entity_description.native_step is not None:
            return self.entity_description.native_step
        return self._device.get_register_value_step(self.entity_description.key)

    @property
    def native_min_value(self):
        return self._device.get_register_value_min(self.entity_description.key)

    @property
    def native_max_value(self):
        return self._device.get_register_value_max(self.entity_description.key)

    async def async_set_native_value(self, value):
        try:
            await self._device.set_register_value(self.entity_description.key, value)
            await self.coordinator.async_request_refresh()
        except (ValueError, AguaIOTError) as err:
            _LOGGER.error("Failed to set value, error: %s", err)


class AguaIOTLoadPelletDurationNumber(AguaIOTHeatingNumber, RestoreNumber):
    """Pellet load duration, stored in Home Assistant only.

    The "Load Pellets" button writes it to load_pellet_set when pressed.
    """

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last_data = await self.async_get_last_number_data()
        if last_data and last_data.native_value is not None:
            self._store(last_data.native_value)

    def _store(self, value):
        value = min(max(value, self.native_min_value), self.native_max_value)
        self.coordinator.load_pellet_duration[self._device.id_device] = int(value)

    @property
    def native_value(self):
        return self.coordinator.load_pellet_duration.get(
            self._device.id_device, self.native_max_value
        )

    @property
    def native_min_value(self):
        return self.entity_description.native_min_value

    @property
    def native_max_value(self):
        # Limit of the register written by the button, see LOAD_PELLET_DURATION
        return self._device.get_register_value_max("load_pellet_set")

    async def async_set_native_value(self, value):
        self._store(value)
        self.async_write_ha_state()
