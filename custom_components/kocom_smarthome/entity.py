"""Common base for every entity this integration creates.

Only sensors exist today, but the wallpad a coordinator is bound to — and the
device it maps onto in Home Assistant — is not a metering concept. Anything
added later attaches to the same device through this base.
"""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DEFAULT_DEVICE_NAME, DOMAIN, MANUFACTURER
from .models import Pair


def build_device_info(entry_id: str, pair: Pair) -> DeviceInfo:
    """One Home Assistant device per paired wallpad.

    Named after the alias the user gave the wallpad in the KOCOM app, which is
    already how they think of it. Device names are not translated by Home
    Assistant, so the fallback is the brand rather than a localised phrase.
    """
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name=pair.alias or DEFAULT_DEVICE_NAME,
        manufacturer=MANUFACTURER,
        model=pair.alias or None,
    )


class KocomEntity(CoordinatorEntity[DataUpdateCoordinator]):
    """Ties an entity to the paired wallpad it belongs to.

    Entities name themselves relative to that device, so the household is said
    once (by the device) rather than repeated in every entity name.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator: DataUpdateCoordinator, pair: Pair) -> None:
        super().__init__(coordinator)
        self._pair = pair
        self._attr_device_info = build_device_info(
            coordinator.config_entry.entry_id, pair
        )
