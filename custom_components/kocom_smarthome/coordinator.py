"""Polling of the monthly metering figures."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import KocomClient, KocomError
from .const import (
    CONF_ENERGY_INTERVAL,
    DEFAULT_ENERGY_INTERVAL,
    DOMAIN,
    ENERGY_META,
    LOGGER,
    mask,
)
from .models import EnergyReading, Pair, Session

type ReadingsByKind = dict[str, dict[bool, EnergyReading]]


class KocomEnergyCoordinator(DataUpdateCoordinator[ReadingsByKind]):
    """Keeps one month of metering fresh for every energy kind."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: KocomClient,
        session: Session,
        pair: Pair,
    ) -> None:
        interval = entry.options.get(
            CONF_ENERGY_INTERVAL,
            entry.data.get(CONF_ENERGY_INTERVAL, DEFAULT_ENERGY_INTERVAL),
        )
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(hours=interval),
        )
        self.client = client
        self.session = session
        self.pair = pair
        self.last_sync: datetime | None = None

        # The previous implementation aimed at svrip; the app uses apiurl then
        # apiip. Log all three once so a failure here is diagnosable without
        # another round of guessing.
        LOGGER.debug(
            "Apartment server: using %s (apiurl=%s apiip=%s svrip=%s)",
            mask(pair.base_url, keep=0),
            mask(pair.api_url, keep=0),
            mask(pair.api_ip, keep=0),
            mask(pair.svr_ip, keep=0),
        )

    async def _async_update_data(self) -> ReadingsByKind:
        month = dt_util.now().strftime("%Y%m")
        try:
            readings = await self.client.energy_readings(
                self.session, self.pair, month
            )
        except KocomError as err:
            raise UpdateFailed(str(err)) from err

        by_kind: ReadingsByKind = {}
        for reading in readings:
            if reading.energy not in ENERGY_META:
                LOGGER.debug("Ignoring unknown energy kind %s", reading.energy)
                continue
            previous = reading.is_previous_month(month)
            by_kind.setdefault(reading.energy, {})[previous] = reading

        if not by_kind:
            raise UpdateFailed(
                f"No usable metering rows for {month}; "
                f"received {len(readings)} entries"
            )

        self.last_sync = dt_util.now()
        return by_kind

    def reading_for(self, energy: str, previous: bool) -> EnergyReading | None:
        """Resolve the row backing one sensor.

        A current-month sensor falls back to the previous month's row when the
        apartment server has not finalised this month yet, so the history does
        not develop a gap (README "전월 데이터 폴백").
        """
        rows = (self.data or {}).get(energy, {})
        if previous in rows:
            return rows[previous]
        if not previous:
            return rows.get(True)
        return None
