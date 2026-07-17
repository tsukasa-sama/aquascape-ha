"""Config flow for the Aquascape integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import AquascapeApiClient, AquascapeApiError, AquascapeAuthError
from .const import (
    CONF_AUTH_KEY,
    CONF_DEVICE_TYPE,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DEVICE_TYPE_SMART_CONTROL_PLUG,
    DEVICE_TYPE_SMART_POND_THERMOMETER,
    DEVICE_TYPES,
    DOMAIN,
    MAX_SCAN_INTERVAL_MINUTES,
    MIN_SCAN_INTERVAL_MINUTES,
)

_LOGGER = logging.getLogger(__name__)

# Fallback entry titles per device type, used if the device name can't be read.
DEFAULT_TITLES = {
    DEVICE_TYPE_SMART_CONTROL_PLUG: "Smart Control Plug",
    DEVICE_TYPE_SMART_POND_THERMOMETER: "Smart Pond Thermometer",
}

# Step 1: single radio field to pick the device type.
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_TYPE): SelectSelector(
            SelectSelectorConfig(
                options=DEVICE_TYPES,
                mode=SelectSelectorMode.LIST,
                translation_key=CONF_DEVICE_TYPE,
            )
        ),
    }
)

# Step 2 (both device types): the device's auth key / token.
STEP_TOKEN_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_AUTH_KEY): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)


class AquascapeConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aquascape."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._device_type: str | None = None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> AquascapeOptionsFlow:
        """Return the options flow handler."""
        return AquascapeOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 1: pick the device type via a radio selection."""
        if user_input is not None:
            self._device_type = user_input[CONF_DEVICE_TYPE]
            if self._device_type == DEVICE_TYPE_SMART_CONTROL_PLUG:
                return await self.async_step_smart_control_plug()
            if self._device_type == DEVICE_TYPE_SMART_POND_THERMOMETER:
                return await self.async_step_smart_pond_thermometer()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA
        )

    async def async_step_smart_control_plug(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: configure a Smart Control Plug."""
        return await self._async_token_step("smart_control_plug", user_input)

    async def async_step_smart_pond_thermometer(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: configure a Smart Pond Thermometer."""
        return await self._async_token_step("smart_pond_thermometer", user_input)

    async def _async_token_step(
        self, step_id: str, user_input: dict[str, Any] | None
    ) -> ConfigFlowResult:
        """Shared token-entry step: validate the token and create the entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            client = AquascapeApiClient(
                auth_key=user_input[CONF_AUTH_KEY],
                session=async_get_clientsession(self.hass),
            )
            try:
                name = await client.async_get_device_name()
            except AquascapeAuthError:
                errors["base"] = "invalid_auth"
            except AquascapeApiError as err:
                _LOGGER.error("Cannot connect to Aquascape: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error validating Aquascape auth key")
                errors["base"] = "unknown"
            else:
                # Each device has its own token, so it identifies the device.
                # Prevents adding the same device twice.
                await self.async_set_unique_id(user_input[CONF_AUTH_KEY])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name or DEFAULT_TITLES.get(self._device_type, "Aquascape"),
                    data={CONF_DEVICE_TYPE: self._device_type, **user_input},
                )

        return self.async_show_form(
            step_id=step_id, data_schema=STEP_TOKEN_SCHEMA, errors=errors
        )


class AquascapeOptionsFlow(OptionsFlow):
    """Handle Aquascape options (polling interval)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the polling interval option."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_MINUTES
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL_MINUTES,
                        max=MAX_SCAN_INTERVAL_MINUTES,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
