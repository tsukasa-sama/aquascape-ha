"""Constants for the Aquascape integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "aquascape_ha"

# Config entry keys
CONF_DEVICE_TYPE: Final = "device_type"
CONF_AUTH_KEY: Final = "auth_key"

# Options keys
CONF_SCAN_INTERVAL: Final = "scan_interval"  # minutes

# Device types offered on the first config-flow step (radio selection).
# Add new device types here; each should have a matching async_step_<type>
# handler in config_flow.py and an entry in strings.json.
DEVICE_TYPE_SMART_CONTROL_PLUG: Final = "smart_control_plug"
DEVICE_TYPE_SMART_POND_THERMOMETER: Final = "smart_pond_thermometer"

DEVICE_TYPES: Final = [
    DEVICE_TYPE_SMART_CONTROL_PLUG,
    DEVICE_TYPE_SMART_POND_THERMOMETER,
]

# API
API_BASE_URL: Final = "https://smartcontrol.aquascapeinc.com"
API_META_PATH: Final = "/external/api/device/meta"
API_GETALL_PATH: Final = "/external/api/getAll"
API_UPDATE_PATH: Final = "/external/api/update"
API_HW_CONNECTED_PATH: Final = "/external/api/isHardwareConnected"

# Meta indices (meta?token=...&<index>)
META_INDEX_DEVICE_NAME: Final = 1
META_INDEX_DEVICE_OWNER: Final = 2

# getAll response keys used by entities.
# NOTE: keys are reused across device types with different meanings. For the
# Smart Control Plug v11 is current (amps); for the Smart Pond Thermometer v11
# is the temperature (°F).
KEY_SWITCH_1: Final = "v1"
KEY_SWITCH_2: Final = "v2"
KEY_SWITCH_3: Final = "v3"
KEY_AC_VOLTAGE: Final = "v10"
KEY_CURRENT: Final = "v11"
KEY_ACTIVE_POWER: Final = "v12"
KEY_TEMPERATURE: Final = "v11"

# Synthetic key: hardware-connected state merged into coordinator data.
KEY_CONNECTED: Final = "connected"

# Polling interval (minutes)
DEFAULT_SCAN_INTERVAL_MINUTES: Final = 1
MIN_SCAN_INTERVAL_MINUTES: Final = 1
MAX_SCAN_INTERVAL_MINUTES: Final = 60

# Manufacturer / model info surfaced on the device registry entry
MANUFACTURER: Final = "Aquascape"
