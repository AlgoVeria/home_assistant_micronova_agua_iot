import logging

from homeassistant.components.time import TimeEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .aguaiot import AguaIOTError
from .chrono import steps_to_time, time_to_steps
from .const import DOMAIN, TIMES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = config_entry.runtime_data
    agua = coordinator.agua

    times = []
    for device in agua.devices:
        for description in TIMES:
            if description.key in device.registers and device.get_register_enabled(
                description.key
            ):
                times.append(AguaIOTHeatingTime(coordinator, device, description))

    async_add_entities(times, True)


class AguaIOTHeatingTime(CoordinatorEntity, TimeEntity):
    """Time entity for chrono start/stop registers (10-minute steps)"""

    _attr_has_entity_name = True

    def __init__(self, coordinator, device, description):
        """Initialize the time entity."""
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
        """Return the time, None when the slot is not set (144 and above)."""
        if self._device.is_register_read_error(self.entity_description.key):
            return None
        return steps_to_time(
            self._device.get_register_value(self.entity_description.key)
        )

    @property
    def extra_state_attributes(self):
        return {
            "raw_value": self._device.get_register_value(self.entity_description.key)
        }

    async def async_set_value(self, value):
        try:
            await self._device.set_register_value(
                self.entity_description.key, time_to_steps(value)
            )
            await self.coordinator.async_request_refresh()
        except (ValueError, AguaIOTError) as err:
            _LOGGER.error("Failed to set value, error: %s", err)
