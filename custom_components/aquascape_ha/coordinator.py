"""DataUpdateCoordinator for the Aquascape integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AquascapeApiClient, AquascapeApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Config entry with the coordinator stored on runtime_data.
type AquascapeConfigEntry = ConfigEntry[AquascapeDataUpdateCoordinator]


class AquascapeDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the Aquascape API and shares data with entities."""

    config_entry: AquascapeConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: AquascapeConfigEntry,
        client: AquascapeApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest data from the API."""
        try:
            return await self.client.async_get_data()
        except AquascapeApiError as err:
            raise UpdateFailed(f"Error communicating with Aquascape: {err}") from err
