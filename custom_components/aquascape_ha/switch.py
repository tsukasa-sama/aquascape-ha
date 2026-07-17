"""Switch platform for the Aquascape integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_DEVICE_TYPE, DEVICE_TYPE_SMART_CONTROL_PLUG
from .coordinator import AquascapeConfigEntry, AquascapeDataUpdateCoordinator
from .entity import AquascapeEntity


@dataclass(frozen=True, kw_only=True)
class AquascapeSwitchDescription(SwitchEntityDescription):
    """Describes an Aquascape switch."""

    switch_id: int


SWITCHES: tuple[AquascapeSwitchDescription, ...] = (
    AquascapeSwitchDescription(
        key="switch_1", translation_key="switch_1", switch_id=1
    ),
    AquascapeSwitchDescription(
        key="switch_2", translation_key="switch_2", switch_id=2
    ),
    AquascapeSwitchDescription(
        key="switch_3", translation_key="switch_3", switch_id=3
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AquascapeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Aquascape switches from a config entry."""
    if entry.data.get(CONF_DEVICE_TYPE) != DEVICE_TYPE_SMART_CONTROL_PLUG:
        return
    coordinator = entry.runtime_data
    async_add_entities(
        AquascapeSwitch(coordinator, description) for description in SWITCHES
    )


class AquascapeSwitch(AquascapeEntity, SwitchEntity):
    """Representation of an Aquascape switch (v1/v2/v3)."""

    entity_description: AquascapeSwitchDescription

    def __init__(
        self,
        coordinator: AquascapeDataUpdateCoordinator,
        description: AquascapeSwitchDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def _state_key(self) -> str:
        """The getAll key backing this switch (v1/v2/v3)."""
        return f"v{self.entity_description.switch_id}"

    @property
    def is_on(self) -> bool | None:
        """Return True if the switch is on."""
        value = self.coordinator.data.get(self._state_key)
        if value is None:
            return None
        return value == 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._async_set(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._async_set(False)

    async def _async_set(self, on: bool) -> None:
        """Send the command and optimistically update local state.

        The next scheduled poll confirms the real state; we skip an immediate
        refresh so the UI doesn't briefly snap back if the device lags.
        """
        await self.coordinator.client.async_set_switch(
            self.entity_description.switch_id, on
        )
        self.coordinator.data[self._state_key] = 1 if on else 0
        self.async_write_ha_state()
