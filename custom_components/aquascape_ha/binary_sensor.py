"""Binary sensor platform for the Aquascape integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import KEY_CONNECTED
from .coordinator import AquascapeConfigEntry, AquascapeDataUpdateCoordinator
from .entity import AquascapeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AquascapeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the connectivity binary sensor (all device types)."""
    async_add_entities([AquascapeConnectivitySensor(entry.runtime_data)])


class AquascapeConnectivitySensor(AquascapeEntity, BinarySensorEntity):
    """Reports whether the device is actively online and communicating."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "hardware_connected"

    def __init__(self, coordinator: AquascapeDataUpdateCoordinator) -> None:
        """Initialize the connectivity sensor."""
        super().__init__(coordinator, "hardware_connected")

    @property
    def is_on(self) -> bool | None:
        """Return True when the device reports it is connected."""
        return self.coordinator.data.get(KEY_CONNECTED)
