"""Async API client for the Aquascape integration.

Talks to the Aquascape Smart Control cloud API. The device's auth key is
passed as the `token` query parameter.

Endpoints used:
- `/external/api/device/meta?token=<token>&<index>` — typed metadata records
  (1 = DeviceName, 2 = DeviceOwner).
- `/external/api/getAll?token=<token>` — current device state (v1..v3 switches,
  v10 voltage, v11 current, v12 active power, plus others we ignore).
"""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import quote

from aiohttp import ClientError, ClientSession

from .const import (
    API_BASE_URL,
    API_GETALL_PATH,
    API_HW_CONNECTED_PATH,
    API_META_PATH,
    API_UPDATE_PATH,
    META_INDEX_DEVICE_NAME,
    META_INDEX_DEVICE_OWNER,
)

REQUEST_TIMEOUT = 10


class AquascapeApiError(Exception):
    """Raised when the API returns an error."""


class AquascapeAuthError(AquascapeApiError):
    """Raised when authentication fails."""


class AquascapeApiClient:
    """Minimal async client for the Aquascape Smart Control API."""

    def __init__(self, auth_key: str, session: ClientSession) -> None:
        """Initialize the client."""
        self._auth_key = auth_key
        self._session = session

    async def _async_request(self, url: str) -> Any:
        """Perform a GET request and return the decoded JSON body.

        On an HTTP error the API returns `{"error": {"message": ...}}`. An
        invalid token comes back as HTTP 400 with message "Invalid token.",
        which is surfaced as an auth error.
        """
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                async with self._session.get(url) as resp:
                    try:
                        body = await resp.json(content_type=None)
                    except ValueError:
                        body = None

                    if resp.status >= 400:
                        message = None
                        if isinstance(body, dict) and isinstance(
                            body.get("error"), dict
                        ):
                            message = body["error"].get("message")
                        detail = message or f"HTTP {resp.status}"
                        if resp.status in (401, 403) or (
                            message and "token" in message.lower()
                        ):
                            raise AquascapeAuthError(detail)
                        raise AquascapeApiError(detail)

                    return body
        except AquascapeApiError:
            raise
        except (ClientError, asyncio.TimeoutError) as err:
            raise AquascapeApiError(
                f"Error communicating with Aquascape: {err}"
            ) from err

    def _url(self, path: str, extra: str = "") -> str:
        """Build an API URL with the token query parameter."""
        return f"{API_BASE_URL}{path}?token={quote(self._auth_key, safe='')}{extra}"

    async def _async_get_meta(self, index: int) -> dict[str, Any]:
        """Fetch a single metadata record by field id.

        The endpoint requires a `metaFieldId` query parameter (1 = DeviceName,
        2 = DeviceOwner).
        """
        return await self._async_request(
            self._url(API_META_PATH, f"&metaFieldId={index}")
        )

    async def async_validate_connection(self) -> None:
        """Validate that the auth key works by fetching device metadata.

        Raises AquascapeAuthError on a bad token and AquascapeApiError on
        connection problems.
        """
        await self._async_get_meta(META_INDEX_DEVICE_NAME)

    async def async_get_device_name(self) -> str | None:
        """Return the device's name (meta index 1)."""
        data = await self._async_get_meta(META_INDEX_DEVICE_NAME)
        return data.get("value")

    async def async_get_owner(self) -> dict[str, Any]:
        """Return the device owner's email and user id (meta index 2)."""
        data = await self._async_get_meta(META_INDEX_DEVICE_OWNER)
        return {"email": data.get("value"), "user_id": data.get("userId")}

    async def async_get_data(self) -> dict[str, Any]:
        """Fetch the current device state via getAll.

        Returns the raw response dict (keys v1..v32); entities read the keys
        they care about.
        """
        return await self._async_request(self._url(API_GETALL_PATH))

    async def async_get_hardware_connected(self) -> bool:
        """Return whether the device is actively online and communicating."""
        result = await self._async_request(self._url(API_HW_CONNECTED_PATH))
        return result is True

    async def async_set_switch(self, switch_id: int, on: bool) -> None:
        """Turn a switch (1, 2, or 3) on or off.

        Calls `/external/api/update?token=<token>&v<id>=<0|1>`.
        """
        pin = f"v{switch_id}"
        value = 1 if on else 0
        await self._async_request(self._url(API_UPDATE_PATH, f"&{pin}={value}"))
