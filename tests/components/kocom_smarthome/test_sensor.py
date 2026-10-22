"""Verify previous-month sensor semantics using the loaded sensor platform."""

from homeassistant.helpers import entity_registry as er

from custom_components.kocom_smarthome.models import EnergyReading


async def test_previous_month_sensors_and_current_fallback(
    hass, mock_config_entry, mock_client
):
    """A previous reading has total state class and current values fall back."""
    mock_client.energy_readings.return_value = [
        EnergyReading.parse(
            {
                "energy": "elec",
                "date": "2000-01",
                "value": 45.6,
            }
        )
    ]
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    entities = er.async_entries_for_config_entry(
        er.async_get(hass), mock_config_entry.entry_id
    )
    assert len(entities) == 2
    states = [hass.states.get(entity.entity_id) for entity in entities]
    assert all(state.state == "45.6" for state in states)
    previous = next(
        state for state in states if state.attributes["state_class"] == "total"
    )
    assert previous.attributes["Registration Date"] == "2000-01"
    assert previous.attributes["device_class"] == "energy"
    assert previous.attributes["unit_of_measurement"] == "kWh"
