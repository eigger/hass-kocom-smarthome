"""Config and options flow."""

from __future__ import annotations

import re
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import KocomAuthError, KocomClient, KocomError, KocomResponseError
from .const import (
    CONF_BRANCH_ZONE_ID,
    CONF_ENERGY_INTERVAL,
    CONF_PAIR,
    CONF_PASSWORD,
    CONF_PHONE_NUMBER,
    CONF_WALLPAD_NUMBER,
    DEFAULT_ENERGY_INTERVAL,
    DOMAIN,
    LOGGER,
    mask,
)
from .models import Pair, Session

PHONE_RE = re.compile(r"^01\d{8,9}$")
WALLPAD_RE = re.compile(r"^\d{8}$")

OPTIONS_SCHEMA = vol.Schema(
    {vol.Required(CONF_ENERGY_INTERVAL, default=DEFAULT_ENERGY_INTERVAL): cv.positive_int}
)


class KocomConfigFlow(ConfigFlow, domain=DOMAIN):
    """Walk the user through phone login and wallpad pairing."""

    VERSION = 2

    def __init__(self) -> None:
        # Per-instance, so an abandoned flow does not leak into the next one.
        self._phone_number: str = ""
        self._session: Session | None = None
        self._client: KocomClient | None = None
        self._pair: Pair | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Log in with the phone number registered on the wallpad."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._phone_number = user_input[CONF_PHONE_NUMBER].strip()
            if not PHONE_RE.match(self._phone_number):
                errors["base"] = "invalid_phone_number"
            else:
                self._client = KocomClient(async_get_clientsession(self.hass))
                try:
                    self._session = await self._client.login(self._phone_number)
                except KocomAuthError:
                    errors["base"] = "auth_failed"
                except KocomError as err:
                    LOGGER.error("sphone login failed: %s", err)
                    errors["base"] = "network_error"

            if not errors and self._session is not None:
                await self.async_set_unique_id(self._session.zone_id)
                self._abort_if_unique_id_configured()
                LOGGER.debug(
                    "Logged in as zone %s", mask(self._session.zone_id)
                )
                return await self._async_continue_after_login()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_PHONE_NUMBER): cv.string}),
            errors=errors,
        )

    async def _async_continue_after_login(self) -> ConfigFlowResult:
        """Skip wallpad pairing when this household is already registered."""
        assert self._client and self._session
        try:
            pairs = await self._client.pairs(self._session)
        except KocomError as err:
            LOGGER.error("pairlist failed: %s", err)
            return self.async_abort(reason="cannot_connect")

        if pairs:
            self._pair = pairs[0]
            return await self.async_step_options()
        return await self.async_step_wallpad()

    async def async_step_wallpad(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Claim the household with the code shown on the wallpad."""
        assert self._client and self._session
        errors: dict[str, str] = {}

        if user_input is not None:
            wallpad_number = user_input[CONF_WALLPAD_NUMBER].strip()
            if not WALLPAD_RE.match(wallpad_number):
                errors["base"] = "invalid_auth_number"
            else:
                try:
                    await self._client.register_wallpad(
                        self._session, wallpad_number
                    )
                except (KocomAuthError, KocomResponseError):
                    errors["base"] = "wallpad_auth_failure"
                except KocomError as err:
                    LOGGER.error("pairnum failed: %s", err)
                    errors["base"] = "network_error"

            if not errors:
                try:
                    pairs = await self._client.pairs(self._session)
                except KocomError as err:
                    LOGGER.error("pairlist failed after pairing: %s", err)
                    return self.async_abort(reason="cannot_connect")

                if not pairs:
                    return self.async_abort(reason="registration_failed")
                self._pair = pairs[0]
                return await self.async_step_options()

        return self.async_show_form(
            step_id="wallpad",
            data_schema=vol.Schema({vol.Required(CONF_WALLPAD_NUMBER): cv.string}),
            errors=errors,
        )

    async def async_step_options(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick the polling interval and finish."""
        if user_input is not None:
            assert self._session and self._pair
            return self.async_create_entry(
                title=self._pair.alias or self._phone_number,
                data={
                    CONF_PHONE_NUMBER: self._phone_number,
                    CONF_PASSWORD: self._session.password,
                    CONF_BRANCH_ZONE_ID: self._session.zone_id,
                    CONF_PAIR: self._pair.as_dict(),
                },
                options={CONF_ENERGY_INTERVAL: user_input[CONF_ENERGY_INTERVAL]},
            )

        return self.async_show_form(step_id="options", data_schema=OPTIONS_SCHEMA)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlowWithReload:
        """Get the options flow for this handler."""
        return KocomOptionsFlow()


class KocomOptionsFlow(OptionsFlowWithReload):
    """Adjust the polling interval after setup."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.options
            ),
        )
