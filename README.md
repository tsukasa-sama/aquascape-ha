# Aquascape — Home Assistant integration

A custom Home Assistant integration for [Aquascape](https://smartcontrol.aquascapeinc.com)
devices. Add your devices from the UI with their auth key and control/monitor them directly in Home Assistant.

## Supported devices

| Device | Entities |
| --- | --- |
| **Smart Control Plug** | 3 switches (Switch 1–3), AC voltage, Current, Active power, Connectivity |
| **Smart Pond Thermometer** | Temperature, Connectivity |

Every device also gets a **Connectivity** binary sensor reporting whether the
hardware is actively online and communicating.

## Installation

### HACS (custom repository)

1. HACS → Integrations → ⋮ → Custom repositories.
2. Add `https://github.com/travis-phillips/aquascape-ha` as an **Integration**.
3. Install **Aquascape**, then restart Home Assistant.

### Manual

Copy `custom_components/aquascape_ha` into your Home Assistant
`config/custom_components/` directory and restart.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration → Aquascape**.
2. Choose the device type (Smart Control Plug or Smart Pond Thermometer).
3. Enter the device's **auth key** (token). It's validated against the API and
   the device is named automatically.

Each device is identified by its own token, so the same device can't be added
twice.

### Options

Use the integration's **Configure** button to set the **polling interval**
(1–60 minutes, default 1). Changing it reloads the device and takes effect
immediately.

## How it works

- On each poll the integration first calls `isHardwareConnected`. If the device
  is offline it **skips the full state fetch**, saving API calls; the
  Connectivity sensor reports "off" and the other entities show as unknown.
- When online, it fetches the full device state and updates all entities.
- Switch toggles are **optimistic** — the UI updates immediately and the next
  poll confirms the real state.
