"""Errors must not expose credentials, response content, or household URLs."""

import json
import traceback
from unittest.mock import MagicMock

import aiohttp
import pytest
from homeassistant.config_entries import ConfigEntryState

from custom_components.kocom_smarthome.api import (
    KocomAuthError,
    KocomClient,
    KocomError,
)

SECRET = "PRIVATE-phone-password-household-server"


@pytest.mark.parametrize(
    "body",
    [
        SECRET,
        json.dumps([SECRET]),
        json.dumps({"error": 90, "error-msg": SECRET}),
        json.dumps({"error": 401, "error-msg": SECRET}),
        json.dumps({"error": SECRET, "error-msg": SECRET}),
    ],
)
def test_response_errors_do_not_expose_content_or_url(body):
    with pytest.raises(KocomError) as raised:
        KocomClient._decode(body, f"https://{SECRET}/api/{SECRET}")
    assert SECRET not in "".join(traceback.format_exception(raised.value))


@pytest.mark.parametrize(
    "error", [aiohttp.ClientConnectionError(SECRET), TimeoutError(SECRET)]
)
async def test_transport_errors_do_not_expose_host_or_path(error):
    session = MagicMock()
    session.request.side_effect = error
    with pytest.raises(KocomError) as raised:
        await KocomClient(session)._request(
            "GET", f"https://{SECRET}/api/{SECRET}", SECRET, SECRET
        )
    assert SECRET not in "".join(traceback.format_exception(raised.value))


async def test_missing_digest_nonce_does_not_expose_challenge_url():
    session = MagicMock()
    response = session.request.return_value.__aenter__.return_value
    response.headers = {}
    with pytest.raises(KocomAuthError) as raised:
        await KocomClient(session)._request(
            "GET",
            f"https://{SECRET}/api/{SECRET}",
            SECRET,
            SECRET,
            challenge_url=f"https://{SECRET}",
        )
    assert SECRET not in "".join(traceback.format_exception(raised.value))


async def test_invalid_entry_does_not_log_stored_value(
    hass, mock_config_entry, mock_client, caplog
):
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry, data={**mock_config_entry.data, "branch_zone_id": SECRET}
    )
    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
    assert SECRET not in caplog.text


async def test_authentication_failure_is_not_retried_as_network_error(
    hass, mock_config_entry, mock_client, caplog
):
    mock_client.energy_readings.side_effect = KocomAuthError(SECRET)
    mock_config_entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    assert "authentication failed" in mock_config_entry.reason
    assert SECRET not in caplog.text


async def test_unknown_energy_kind_does_not_log_server_payload(
    hass, mock_config_entry, mock_client, caplog
):
    from custom_components.kocom_smarthome.models import EnergyReading

    mock_client.energy_readings.return_value.append(
        EnergyReading.parse({"energy": SECRET, "date": "2000-01", "value": 10})
    )
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert SECRET not in caplog.text
