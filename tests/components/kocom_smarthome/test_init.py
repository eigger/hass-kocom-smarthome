"""Load the integration and sensors through real Home Assistant."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er


async def test_setup_sensor_states_unload_and_reload(
    hass, mock_config_entry, mock_client
):
    """Entry setup registers real entities and unload removes their state."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED
    entities = er.async_entries_for_config_entry(
        er.async_get(hass), mock_config_entry.entry_id
    )
    assert len(entities) == 3
    states = [hass.states.get(entity.entity_id) for entity in entities]
    assert {state.state for state in states} == {"123.4", "210.0", "18500.0"}
    usage = next(state for state in states if state.attributes["Measure"] == "value")
    assert usage.attributes["unit_of_measurement"] == "kWh"
    assert usage.attributes["device_class"] == "energy"
    assert usage.attributes["state_class"] == "total_increasing"
    assert (
        len(
            dr.async_entries_for_config_entry(
                dr.async_get(hass), mock_config_entry.entry_id
            )
        )
        == 1
    )
    coordinator = mock_config_entry.runtime_data.energy
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert all(
        hass.states.get(entity.entity_id) is None
        or hass.states.get(entity.entity_id).state == STATE_UNAVAILABLE
        for entity in entities
    )
    assert not coordinator.async_update_listeners()
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_client.energy_readings.await_count == 2
    assert (
        len(
            er.async_entries_for_config_entry(
                er.async_get(hass), mock_config_entry.entry_id
            )
        )
        == 3
    )
