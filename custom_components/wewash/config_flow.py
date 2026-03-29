import voluptuous as vol
import requests
from homeassistant import config_entries
from . import DOMAIN


class WeWashConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            ww_refresh = user_input["ww_refresh"].strip()
            try:
                tokens = await self.hass.async_add_executor_job(
                    self._try_refresh, ww_refresh
                )
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                # Store the validated tokens and create the entry
                return self.async_create_entry(
                    title="WeWash",
                    data=tokens,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ww_refresh"): str,
            }),
            errors=errors,
        )

    def _try_refresh(self, ww_refresh: str) -> dict:
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