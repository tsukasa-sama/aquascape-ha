# Aquascape — Home Assistant integration

A custom Home Assistant integration for aquascape/aquarium hardware.

> Status: scaffold. The API client (`api.py`) is stubbed — wire it up to your
> real device or service to bring the entities to life.

## Features

- UI config flow (Settings → Devices & Services → Add Integration → Aquascape)
- `DataUpdateCoordinator` polling with a pluggable async API client
- Platforms: `sensor`, `switch`,

## Installation

### HACS (custom repository)

1. HACS → Integrations → ⋮ → Custom repositories.
2. Add `https://github.com/travis-phillips/aquascape-ha` as an **Integration**.
3. Install **Aquascape**, then restart Home Assistant.

### Manual

Copy `custom_components/aquascape_ha` into your Home Assistant
`config/custom_components/` directory and restart.

## Configuration

Add the integration from the UI and provide the device API key.

## Development

The following are the pieces you'll flesh out from the stubs:

| File | What to implement |
| --- | --- |
| `api.py` | Real connection/auth check and data fetch/commands |
| `coordinator.py` | Adjust the poll interval / data shape if needed |
| `sensor.py` / `switch.py` / `light.py` | Add or rename entities to match your device |
| `strings.json` + `translations/en.json` | Friendly names and flow copy |
