import logging

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .aguaiot import AguaIOTError
from .const import DOMAIN, SELECTS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = config_entry.runtime_data
    agua = coordinator.agua

    selects = []
    for device in agua.devices:
        for select in SELECTS:
            if select.key in device.registers and device.get_register_enabled(
                select.key
            ):
                selects.append(AguaIOTHeatingSelect(coordinator, device, select))

    async_add_entities(selects, True)


class AguaIOTHeatingSelect(CoordinatorEntity, SelectEntity):
    """Select entity"""

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
    def current_option(self):
        value = self._device.get_register_value_description(self.entity_description.key)
        if value is None:
            return None
        return str(value)

    @property
    def options(self):
        options = list(
            self._device.get_register_value_options(
                self.entity_description.key
            ).values()
        )
        if not options:
            # No descriptions in the register map: offer the plain values
            options = [
                str(x)
                for x in range(
                    int(
                        self._device.get_register_value_min(self.entity_description.key)
                    ),
                    int(
                        self._device.get_register_value_max(self.entity_description.key)
                    )
                    + 1,
                )
            ]
        return options

    async def async_select_option(self, option):
        try:
            await self._device.set_register_value_description(
                self.entity_description.key, option
            )
            await self.coordinator.async_request_refresh()
        except (ValueError, AguaIOTError) as err:
            _LOGGER.error("Failed to set value, error: %s", err)
