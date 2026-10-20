import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .aguaiot import AguaIOTError
from .const import BUTTONS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = config_entry.runtime_data
    agua = coordinator.agua

    buttons = []
    for device in agua.devices:
        for button in BUTTONS:
            # Enable registers of buttons depend on the stove state, so they
            # drive availability instead of creation.
            if button.key in device.registers:
                buttons.append(AguaIOTHeatingButton(coordinator, device, button))

    async_add_entities(buttons, True)


class AguaIOTHeatingButton(CoordinatorEntity, ButtonEntity):
    """Button entity"""

    _attr_has_entity_name = True

    def __init__(self, coordinator, device, description):
        """Initialize the button."""
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

    def _status_allowed(self):
        status_values = self.entity_description.status_values
        if status_values is None:
            return True
        if "status_get" not in self._device.registers:
            return False
        if self._device.is_register_read_error("status_get"):
            return False
        return self._device.get_register_value("status_get") in status_values

    def _alarm_active(self):
        if not self.entity_description.alarm_required:
            return True

        if (
            "alarms_get" in self._device.registers
            and not self._device.is_register_read_error("alarms_get")
            and self._device.get_register_value("alarms_get")
        ):
            return True

        if (
            "status_get" in self._device.registers
            and not self._device.is_register_read_error("status_get")
        ):
            description = self._device.get_register_value_description(
                key="status_get", language="ENG"
            )
            description = str(description).strip().upper()
            return "ALARM" in description or "ALLARM" in description

        return False

    @property
    def available(self):
        """Only available when the stove accepts the command."""
        key = self.entity_description.key
        enable_key = key.rsplit("_", 1)[0] + "_enable"
        if enable_key in self._device.registers and (
            self._device.is_register_read_error(enable_key)
        ):
            return False

        return (
            super().available
            and self._device.get_register_enabled(key)
            and self._status_allowed()
            and self._alarm_active()
        )

    async def async_press(self):
        """Press the button."""
        if not self.available:
            raise HomeAssistantError(
                f"{self.entity_description.name} is not available in the current stove state"
            )

        try:
            await self._device.set_register_value(
                self.entity_description.key, self.entity_description.press_value
            )
            await self.coordinator.async_request_refresh()
        except (ValueError, AguaIOTError) as err:
            _LOGGER.error(
                "Failed to press '%s', error: %s", self.entity_description.name, err
            )
