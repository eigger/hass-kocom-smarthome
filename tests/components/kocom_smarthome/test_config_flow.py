"""Exercise pairing and options through the actual HA flow manager."""

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.kocom_smarthome.api import (
    KocomAuthError,
    KocomError,
    KocomResponseError,
)
from custom_components.kocom_smarthome.const import DOMAIN


async def start_flow(hass):
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


async def test_existing_pair_creates_and_loads_entry(hass, mock_client):
    result = await start_flow(hass)
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"phone_number": "01000000000"}
    )
    assert result["step_id"] == "options"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"energy_interval": 12}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == "0000013800100138"
    assert result["result"].options == {"energy_interval": 12}
    assert result["result"].state is config_entries.ConfigEntryState.LOADED
    assert len(hass.states.async_all("sensor")) == 3


async def test_duplicate_aborts(hass, mock_config_entry, mock_client):
    mock_config_entry.add_to_hass(hass)
    result = await start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"phone_number": "01000000000"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize(
    ("phone", "error", "expected"),
    [
        ("123", None, "invalid_phone_number"),
        ("01000000000", KocomAuthError("Denied"), "auth_failed"),
        ("01000000000", KocomError("Offline"), "network_error"),
    ],
)
async def test_login_errors(hass, mock_client, phone, error, expected):
    mock_client.login.side_effect = error
    result = await start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"phone_number": phone}
    )
    assert result["errors"] == {"base": expected}


async def test_wallpad_pairing_errors_and_success(hass, mock_client):
    pair = mock_client.pairs.return_value
    mock_client.pairs.return_value = []
    result = await start_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"phone_number": "01000000000"}
    )
    assert result["step_id"] == "wallpad"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"wallpad_number": "123"}
    )
    assert result["errors"] == {"base": "invalid_auth_number"}
    mock_client.register_wallpad.side_effect = KocomResponseError(90, "Invalid code")
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"wallpad_number": "12345678"}
    )
    assert result["errors"] == {"base": "wallpad_auth_failure"}
    mock_client.register_wallpad.side_effect = None
    mock_client.pairs.return_value = pair
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"wallpad_number": "12345678"}
    )
    assert result["step_id"] == "options"


async def test_options_reload_entry(hass, mock_config_entry, mock_client):
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"energy_interval": 6}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options == {"energy_interval": 6}
    assert (
        mock_config_entry.runtime_data.energy.update_interval.total_seconds() == 21600
    )


async def test_migrate_legacy_entry(hass, mock_config_entry, mock_client):
    legacy = mock_config_entry.data
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry,
        version=1,
        data={
            "phone_number": legacy["phone_number"],
            "energy_interval": 8,
            "pairing_data": {
                "password": legacy["password"],
                "pairing_info": legacy["pair"],
            },
        },
    )
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.version == 2
    assert mock_config_entry.unique_id == "0000013800100138"
    assert mock_config_entry.data == legacy


async def test_reauth_refreshes_credentials_and_reloads(
    hass, mock_config_entry, mock_client
):
    from custom_components.kocom_smarthome.models import Session

    mock_config_entry.add_to_hass(hass)
    mock_client.login.return_value = Session(138, 100138, "new-test-password")
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": mock_config_entry.entry_id,
            "unique_id": mock_config_entry.unique_id,
        },
        data=mock_config_entry.data,
    )
    assert result["step_id"] == "reauth_confirm"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert mock_config_entry.data["password"] == "new-test-password"
    assert mock_config_entry.state is config_entries.ConfigEntryState.LOADED


async def test_reauth_rejects_another_household(hass, mock_config_entry, mock_client):
    from custom_components.kocom_smarthome.models import Session

    mock_config_entry.add_to_hass(hass)
    mock_client.login.return_value = Session(999, 999, "new-test-password")
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": mock_config_entry.entry_id,
            "unique_id": mock_config_entry.unique_id,
        },
        data=mock_config_entry.data,
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "unique_id_mismatch"
    assert mock_config_entry.data["password"] == "test-password"


async def test_reauth_preserves_wallpad_when_branch_identity_differs(
    hass, mock_config_entry, mock_client
):
    """Branch login and apartment wallpad identities can differ."""
    from custom_components.kocom_smarthome.models import Pair, Session

    mock_config_entry.add_to_hass(hass)
    stored_pair = Pair(7, 777, 777001, "Stored wallpad", "", "192.0.2.7")
    hass.config_entries.async_update_entry(
        mock_config_entry,
        data={**mock_config_entry.data, "pair": stored_pair.as_dict()},
    )
    mock_client.login.return_value = Session(138, 100138, "new-test-password")
    other_pair = Pair(1, 138, 100138, "Another wallpad", "", "192.0.2.1")
    mock_client.pairs.return_value = [other_pair, stored_pair]
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": mock_config_entry.entry_id,
            "unique_id": mock_config_entry.unique_id,
        },
        data=mock_config_entry.data,
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    await hass.async_block_till_done()
    assert result["reason"] == "reauth_successful"
    assert mock_config_entry.data["pair"] == stored_pair.as_dict()
    assert mock_config_entry.unique_id == "0000013800100138"
    assert mock_config_entry.runtime_data.pair == stored_pair


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        ("auth", "auth_failed"),
        ("network", "network_error"),
        ("missing_pair", "wallpad_auth_failure"),
    ],
)
async def test_reauth_failure_preserves_credentials_and_can_recover(
    hass, mock_config_entry, mock_client, failure, expected
):
    from custom_components.kocom_smarthome.models import Session

    mock_config_entry.add_to_hass(hass)
    previous_data = dict(mock_config_entry.data)
    pairs = mock_client.pairs.return_value
    if failure == "auth":
        mock_client.login.side_effect = KocomAuthError("Denied")
    elif failure == "network":
        mock_client.pairs.side_effect = KocomError("Offline")
    else:
        mock_client.pairs.return_value = []
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": mock_config_entry.entry_id,
            "unique_id": mock_config_entry.unique_id,
        },
        data=mock_config_entry.data,
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"] == {"base": expected}
    assert mock_config_entry.data == previous_data
    mock_client.login.side_effect = None
    mock_client.login.return_value = Session(138, 100138, "refreshed-test-password")
    mock_client.pairs.side_effect = None
    mock_client.pairs.return_value = pairs
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    await hass.async_block_till_done()
    assert result["reason"] == "reauth_successful"
    assert mock_config_entry.data["password"] == "refreshed-test-password"
