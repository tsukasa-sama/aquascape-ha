"""Sensor platform for the Aquascape integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import KEY_AC_VOLTAGE, KEY_ACTIVE_POWER, KEY_CURRENT
from .coordinator import AquascapeConfigEntry, AquascapeDataUpdateCoordinator
from .entity import AquascapeEntity


@dataclass(frozen=True, kw_only=True)
class AquascapeSensorDescription(SensorEntityDescription):
    """Describes an Aquascape sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSORS: tuple[AquascapeSensorDescription, ...] = (
    AquascapeSensorDescription(
        key="ac_voltage",
        translation_key="ac_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        value_fn=lambda data: data.get(KEY_AC_VOLTAGE),
    ),
    AquascapeSensorDescription(
        key="current",
        translation_key="current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=3,
        value_fn=lambda data: data.get(KEY_CURRENT),
    ),
    AquascapeSensorDescription(
        key="active_power",
        translation_key="active_power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        value_fn=lambda data: data.get(KEY_ACTIVE_POWER),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AquascapeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Aquascape sensors from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        AquascapeSensor(coordinator, description) for description in SENSORS
    )


class AquascapeSensor(AquascapeEntity, SensorEntity):
    """Representation of an Aquascape sensor."""

    entity_description: AquascapeSensorDescription

    def __init__(
        self,
        coordinator: AquascapeDataUpdateCoordinator,
        description: AquascapeSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the current sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
