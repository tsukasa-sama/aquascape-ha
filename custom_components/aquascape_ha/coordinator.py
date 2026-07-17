"""DataUpdateCoordinator for the Aquascape integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AquascapeApiClient, AquascapeApiError
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
    KEY_CONNECTED,
)

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
        minutes = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=minutes),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch connectivity first; only poll full state when online.

        Skipping getAll while the device is offline avoids hammering the API
        for data it can't provide.
        """
        try:
            connected = await self.client.async_get_hardware_connected()
            if not connected:
                return {KEY_CONNECTED: False}
            data = await self.client.async_get_data()
        except AquascapeApiError as err:
            raise UpdateFailed(f"Error communicating with Aquascape: {err}") from err
        data[KEY_CONNECTED] = True
        return data
