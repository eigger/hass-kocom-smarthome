"""Coordinator failure and recovery through real HA entities."""

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers import entity_registry as er

from custom_components.kocom_smarthome.api import KocomError


async def test_failed_refresh_marks_entities_unavailable_and_recovers(
    hass, mock_config_entry, mock_client
):
    """Network failures preserve readings and recovery restores entity states."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    entities = er.async_entries_for_config_entry(
        er.async_get(hass), mock_config_entry.entry_id
    )
    coordinator = mock_config_entry.runtime_data.energy
    readings = coordinator.data
    mock_client.energy_readings.side_effect = KocomError("Connection failed")
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert coordinator.data == readings
    assert all(
        hass.states.get(e.entity_id).state == STATE_UNAVAILABLE for e in entities
    )
    mock_client.energy_readings.side_effect = None
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert all(
        hass.states.get(e.entity_id).state != STATE_UNAVAILABLE for e in entities
    )


@pytest.mark.parametrize("readings", [[], KocomError("Connection failed")])
async def test_initial_refresh_failure_keeps_polling(
    hass, mock_config_entry, mock_client, readings
):
    """Empty or unreachable servers do not block setup; sensors appear later."""
    original = mock_client.energy_readings.return_value
    if isinstance(readings, Exception):
        mock_client.energy_readings.side_effect = readings
    else:
        mock_client.energy_readings.return_value = readings
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED
    registry = er.async_get(hass)
    assert not er.async_entries_for_config_entry(registry, mock_config_entry.entry_id)

    mock_client.energy_readings.side_effect = None
    mock_client.energy_readings.return_value = original
    await mock_config_entry.runtime_data.energy.async_refresh()
    await hass.async_block_till_done()
    assert er.async_entries_for_config_entry(registry, mock_config_entry.entry_id)
