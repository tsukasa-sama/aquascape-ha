"""The Aquascape integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AquascapeApiClient
from .const import CONF_AUTH_KEY
from .coordinator import AquascapeConfigEntry, AquascapeDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(
    hass: HomeAssistant, entry: AquascapeConfigEntry
) -> bool:
    """Set up Aquascape from a config entry."""
    client = AquascapeApiClient(
        auth_key=entry.data[CONF_AUTH_KEY],
        session=async_get_clientsession(hass),
    )

    coordinator = AquascapeDataUpdateCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: AquascapeConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
