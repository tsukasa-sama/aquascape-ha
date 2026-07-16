"""Config flow for the Aquascape integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
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
    DEVICE_TYPE_SMART_CONTROL_PLUG,
    DEVICE_TYPES,
    DOMAIN,
)

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

# Step 2 (Smart Control Plug): the device's auth key.
STEP_SMART_CONTROL_PLUG_SCHEMA = vol.Schema(
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

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 1: pick the device type via a radio selection."""
        if user_input is not None:
            self._device_type = user_input[CONF_DEVICE_TYPE]
            if self._device_type == DEVICE_TYPE_SMART_CONTROL_PLUG:
                return await self.async_step_smart_control_plug()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA
        )

    async def async_step_smart_control_plug(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: configure a Smart Control Plug."""
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
            except AquascapeApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                # Each Smart Control Plug has its own token, so it identifies
                # the device. Prevents adding the same plug twice.
                await self.async_set_unique_id(user_input[CONF_AUTH_KEY])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name or "Smart Control Plug",
                    data={CONF_DEVICE_TYPE: self._device_type, **user_input},
                )

        return self.async_show_form(
            step_id="smart_control_plug",
            data_schema=STEP_SMART_CONTROL_PLUG_SCHEMA,
            errors=errors,
        )
