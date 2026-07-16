"""Base entity for the Aquascape integration."""

from __future__ import annotations

from homeassistant.helpers.device_info import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import AquascapeDataUpdateCoordinator


class AquascapeEntity(CoordinatorEntity[AquascapeDataUpdateCoordinator]):
    """Base class that ties entities to the coordinator and a device."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: AquascapeDataUpdateCoordinator, key: str
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._key = key
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
        )
