"""The KOCOM Smart Home+ energy integration.

Every import here is local to the function that uses it, including the
`homeassistant.*` ones. Python always runs a package's __init__.py before any
of its submodules, so anything imported eagerly at this module's top level
would be required just to import digest.py or models.py — even though neither
touches Home Assistant. Keeping the module-level surface to nothing but the
docstring and `from __future__ import annotations` is what lets those two
files' tests run without Home Assistant installed (see
.github/workflows/tests.yml). Real Home Assistant is on the path by the time
any of these functions actually runs, so this changes nothing about runtime
behaviour — only import-time cost, and only trivially.

(api.py and coordinator.py still pull in Home Assistant regardless, via
const.py's module-level `SensorDeviceClass`/`SensorStateClass` import — this
file being clean does not make the whole package Home-Assistant-free.)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .runtime import KocomConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: KocomConfigEntry) -> bool:
    """Set up a config entry."""
    from homeassistant.exceptions import ConfigEntryNotReady
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    from .api import KocomClient
    from .const import CONF_BRANCH_ZONE_ID, CONF_PAIR, CONF_PASSWORD, PLATFORMS
    from .coordinator import KocomEnergyCoordinator
    from .models import Pair, Session
    from .runtime import KocomRuntimeData

    try:
        pair = Pair.parse(entry.data[CONF_PAIR])
        branch_zone_id = entry.data[CONF_BRANCH_ZONE_ID]
        session = Session(
            zone=int(branch_zone_id[:8]),
            ikod=int(branch_zone_id[8:]),
            password=entry.data[CONF_PASSWORD],
        )
    except (KeyError, TypeError, ValueError) as err:
        raise ConfigEntryNotReady(f"Stored credentials are unusable: {err}") from err

    client = KocomClient(async_get_clientsession(hass))
    energy = KocomEnergyCoordinator(hass, entry, client, session, pair)
    await energy.async_config_entry_first_refresh()

    entry.runtime_data = KocomRuntimeData(
        client=client, session=session, pair=pair, energy=energy
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: KocomConfigEntry) -> bool:
    """Unload a config entry."""
    from .const import PLATFORMS

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Bring a version 1 entry onto the flattened data layout.

    Version 1 nested everything under ``pairing_data`` and derived the
    household key with a padding rule that only held for three-digit zones,
    so the ids are recomputed here rather than carried over.
    """
    from .const import (
        CONF_BRANCH_ZONE_ID,
        CONF_ENERGY_INTERVAL,
        CONF_PAIR,
        CONF_PASSWORD,
        CONF_PHONE_NUMBER,
        DEFAULT_ENERGY_INTERVAL,
        LOGGER,
    )
    from .models import Pair, zone_id

    if entry.version > 2:
        return False
    if entry.version == 2:
        return True

    legacy = entry.data.get("pairing_data") or {}
    pairing_info = legacy.get("pairing_info") or {}
    phone_number = entry.data.get(CONF_PHONE_NUMBER)
    password = legacy.get("password")

    if not (phone_number and password and pairing_info):
        LOGGER.error(
            "Cannot migrate this entry: the stored pairing data is incomplete. "
            "Remove the integration and add it again"
        )
        return False

    try:
        pair = Pair.parse(pairing_info)
        branch_zone_id = zone_id(pairing_info["zone"], pairing_info["id"])
    except (KeyError, TypeError, ValueError) as err:
        LOGGER.error("Cannot migrate this entry: %s", err)
        return False

    hass.config_entries.async_update_entry(
        entry,
        version=2,
        unique_id=branch_zone_id,
        title=pair.alias or phone_number,
        data={
            CONF_PHONE_NUMBER: phone_number,
            CONF_PASSWORD: password,
            CONF_BRANCH_ZONE_ID: branch_zone_id,
            CONF_PAIR: pair.as_dict(),
        },
        options={
            CONF_ENERGY_INTERVAL: entry.options.get(
                CONF_ENERGY_INTERVAL,
                entry.data.get(CONF_ENERGY_INTERVAL, DEFAULT_ENERGY_INTERVAL),
            )
        },
    )
    LOGGER.info("Migrated the KOCOM config entry to version 2")
    return True
