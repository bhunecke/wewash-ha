import json
import logging
from datetime import timedelta

import requests
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.storage import Store

_LOGGER = logging.getLogger(__name__)
STORAGE_KEY = "wewash_tokens"
STORAGE_VERSION = 1


class WeWashCoordinator(DataUpdateCoordinator):
    def __init__(self, hass):
        super().__init__(
            hass,
            _LOGGER,
            name="wewash",
            update_interval=timedelta(minutes=2),
        )
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)

    async def _load_tokens(self) -> dict:
        data = await self._store.async_load()
        if not data:
            raise UpdateFailed("No WeWash tokens found. Please set up the integration first.")
        return data

    async def _save_tokens(self, tokens: dict):
        await self._store.async_save(tokens)

    def _refresh_access_token(self, ww_refresh):
        r = requests.post(
            "https://backend.we-wash.com/auth/refresh",
            headers={
                "origin": "https://app.we-wash.com",
                "referer": "https://app.we-wash.com/",
                "ww-app-version": "2.76.0",
                "ww-client": "USERAPP",
            },
            cookies={"ww_refresh": ww_refresh},
        )
        r.raise_for_status()
        return {
            "ww_access": r.cookies["ww_access"],
            "ww_refresh": r.cookies["ww_refresh"],
            "awsalb": r.cookies["AWSALB"],
        }

    async def _async_update_data(self):
        try:
            tokens = await self._load_tokens()
            new_tokens = await self.hass.async_add_executor_job(
                self._refresh_access_token, tokens["ww_refresh"]
            )
            await self._save_tokens(new_tokens)

            r = await self.hass.async_add_executor_job(
                lambda: requests.get(
                    "https://backend.we-wash.com/v3/users/me/laundry-rooms",
                    headers={
                        "accept": "application/json",
                        "origin": "https://app.we-wash.com",
                        "ww-app-version": "2.76.0",
                        "ww-client": "USERAPP",
                    },
                    cookies={"ww_access": new_tokens["ww_access"]},
                )
            )
            r.raise_for_status()
            data = r.json()
            return data["selectedLaundryRooms"]
        except Exception as e:
            raise UpdateFailed(f"WeWash update failed: {e}")