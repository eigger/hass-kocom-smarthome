"""Energy metering sensors."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_PHONE_NUMBER, ENERGY_META, LOGGER, PRICE_UNIT
from .coordinator import KocomEnergyCoordinator
from .entity import KocomEntity
from .models import Pair, SensorSpec, build_specs
from .runtime import KocomConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KocomConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for a config entry."""
    data = entry.runtime_data
    phone_number = entry.data[CONF_PHONE_NUMBER]

    specs = build_specs(data.energy.data or {}, ENERGY_META)
    LOGGER.debug("Creating %d energy sensors", len(specs))
    async_add_entities(
        KocomEnergySensor(data.energy, data.pair, spec, phone_number)
        for spec in specs
    )


class KocomEnergySensor(KocomEntity, SensorEntity):
    """One figure from the monthly metering."""

    def __init__(
        self,
        coordinator: KocomEnergyCoordinator,
        pair: Pair,
        spec: SensorSpec,
        phone_number: str,
    ) -> None:
        super().__init__(coordinator, pair)
        self._spec = spec
        meta = ENERGY_META[spec.energy]

        self._attr_unique_id = spec.unique_id(phone_number)
        # Name and icon are resolved by Home Assistant from the translation
        # files and icons.json; setting _attr_name here would override them.
        self._attr_translation_key = spec.translation_key

        if spec.measure == "price":
            # A currency total for the period, not a rate — HA's monetary
            # device class takes any ISO 4217 code as its unit, so this is a
            # real classification rather than an ad-hoc unit string.
            self._attr_native_unit_of_measurement = PRICE_UNIT
            self._attr_device_class = SensorDeviceClass.MONETARY
            self._attr_state_class = SensorStateClass.TOTAL
        else:
            self._attr_native_unit_of_measurement = meta.unit
            self._attr_device_class = meta.device_class
            self._attr_state_class = self._state_class(meta.state_class, spec.previous)

    @staticmethod
    def _state_class(
        state_class: SensorStateClass | None, previous: bool
    ) -> SensorStateClass | None:
        """Soften ``total_increasing`` to ``total`` for last month's figures.

        A previous-month sensor holds a value that stops rising and then drops
        back once the current month arrives, which ``total_increasing`` would
        read as a meter reset and count twice.
        """
        if previous and state_class is SensorStateClass.TOTAL_INCREASING:
            return SensorStateClass.TOTAL
        return state_class

    @property
    def native_value(self) -> float | None:
        reading = self.coordinator.reading_for(self._spec.energy, self._spec.previous)
        return reading.measure(self._spec.measure) if reading else None

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        reading = self.coordinator.reading_for(self._spec.energy, self._spec.previous)
        sync = self.coordinator.last_sync
        return {
            "Energy": self._spec.energy,
            "Measure": self._spec.measure,
            "Registration Date": reading.date if reading else None,
            "Sync date": sync.strftime("%Y-%m-%d %H:%M:%S") if sync else None,
        }
