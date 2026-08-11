"""Constants for the KOCOM Smart Home+ energy integration."""

from __future__ import annotations

import logging
from typing import Final

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import Platform, UnitOfEnergy, UnitOfVolume

LOGGER = logging.getLogger(__package__)

DOMAIN: Final = "kocom_smarthome"

# Energy metering is the whole of the current scope. Control (lights, outlets,
# heating, ventilation) is deferred rather than ruled out.
PLATFORMS: Final = [Platform.SENSOR]

MANUFACTURER: Final = "Kocom Co., Ltd."
# Device names are not run through the translation files, so this stays a
# brand name rather than a localised phrase.
DEFAULT_DEVICE_NAME: Final = "KOCOM Smart Home+"

# --- Protocol constants -----------------------------------------------------

BRANCH_BASE_URL: Final = "https://homenet.kocomsmart.com/kbranch"
DIGEST_REALM: Final = "kbranch"

# Fixed protocol-level credentials. Which of the two ikod values the server
# honours is not verified, so the client tries them in order.
DIGEST_IKODS: Final = ("Android!1000002", "Android!1000001")
DIGEST_MEMBERSHIP: Final = "4990e9e16a532aa9010403b01e0ee52a"

# The sphone request body carries the legacy ikod as its "type" field.
SPHONE_TYPE: Final = "Android!1000001"

CONNECT_TIMEOUT: Final = 10
READ_TIMEOUT: Final = 30

# --- Config entry keys -----------------------------------------------------

CONF_PHONE_NUMBER: Final = "phone_number"
CONF_WALLPAD_NUMBER: Final = "wallpad_number"
CONF_ENERGY_INTERVAL: Final = "energy_interval"

CONF_PASSWORD: Final = "password"
CONF_BRANCH_ZONE_ID: Final = "branch_zone_id"
CONF_PAIR: Final = "pair"

DEFAULT_ENERGY_INTERVAL: Final = 24

# --- Energy metadata ---------------------------------------------------------


class EnergyMeta:
    """How one metered energy kind is presented.

    Display names are not here — they come from ``entity.sensor.<key>.name`` in
    the translation files, keyed by ``SensorSpec.translation_key``. Icons come
    from ``icons.json`` the same way. What remains is the part Home Assistant
    needs as real values rather than text.
    """

    __slots__ = ("device_class", "state_class", "unit")

    def __init__(
        self,
        unit: str,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
    ) -> None:
        self.unit = unit
        self.device_class = device_class
        self.state_class = state_class


CUBIC_METERS = UnitOfVolume.CUBIC_METERS

ENERGY_META: Final[dict[str, EnergyMeta]] = {
    "elec": EnergyMeta(
        UnitOfEnergy.KILO_WATT_HOUR,
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
    ),
    "heat": EnergyMeta(CUBIC_METERS, None, None),
    "hotwater": EnergyMeta(CUBIC_METERS, None, None),
    "gas": EnergyMeta(
        CUBIC_METERS, SensorDeviceClass.GAS, SensorStateClass.TOTAL_INCREASING
    ),
    "water": EnergyMeta(
        CUBIC_METERS, SensorDeviceClass.WATER, SensorStateClass.TOTAL_INCREASING
    ),
}

# A plain ISO 4217 currency code, not a rate — the "예상 요금" figure is a total
# for the reporting period, matching HA's monetary device class.
PRICE_UNIT: Final = "KRW"


def mask(value: object, keep: int = 4) -> str:
    """Redact all but the last few characters of an identifier.

    Debug logs carry phone numbers, household ids and apartment server
    addresses; they must not be readable when a user pastes a log into a
    public issue.
    """
    text = str(value)
    if keep <= 0 or len(text) <= keep:
        return "*" * len(text)
    return "*" * (len(text) - keep) + text[-keep:]
