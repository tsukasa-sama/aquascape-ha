"""Constants for the Aquascape integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "aquascape_ha"

# Config entry keys
CONF_DEVICE_TYPE: Final = "device_type"
CONF_AUTH_KEY: Final = "auth_key"

# Device types offered on the first config-flow step (radio selection).
# Add new device types here; each should have a matching async_step_<type>
# handler in config_flow.py and an entry in strings.json.
DEVICE_TYPE_SMART_CONTROL_PLUG: Final = "smart_control_plug"

DEVICE_TYPES: Final = [
    DEVICE_TYPE_SMART_CONTROL_PLUG,
]

# API
API_BASE_URL: Final = "https://smartcontrol.aquascapeinc.com"
API_META_PATH: Final = "/external/api/device/meta"
API_GETALL_PATH: Final = "/external/api/getAll"
API_UPDATE_PATH: Final = "/external/api/update"

# Meta indices (meta?token=...&<index>)
META_INDEX_DEVICE_NAME: Final = 1
META_INDEX_DEVICE_OWNER: Final = 2

# getAll response keys used by entities
KEY_SWITCH_1: Final = "v1"
KEY_SWITCH_2: Final = "v2"
KEY_SWITCH_3: Final = "v3"
KEY_AC_VOLTAGE: Final = "v10"
KEY_CURRENT: Final = "v11"
KEY_ACTIVE_POWER: Final = "v12"

# Defaults
DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=30)

# Manufacturer / model info surfaced on the device registry entry
MANUFACTURER: Final = "Aquascape"
