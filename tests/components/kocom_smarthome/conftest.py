"""Fixtures for the KOCOM integration."""

# <!-- hass-standards:domain-fixtures:start -->
# Use pytest_homeassistant_custom_component.common.MockConfigEntry for
# mock_config_entry when the integration uses config entries.
# Define mock_client only when an external communication client is present.
# Mock external communication boundaries, never Home Assistant core modules.
# Keep integration-specific fixtures below this managed block.
# <!-- hass-standards:domain-fixtures:end -->

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.kocom_smarthome.const import DOMAIN
from custom_components.kocom_smarthome.models import EnergyReading, Pair, Session


@pytest.fixture
def mock_config_entry():
    """An entry with the real persisted version 2 schema."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Test wallpad",
        unique_id="0000013800100138",
        version=2,
        data={
            "phone_number": "01000000000",
            "password": "test-password",
            "branch_zone_id": "0000013800100138",
            "pair": {
                "idx": 1,
                "zone": 138,
                "id": 100138,
                "alias": "Test wallpad",
                "apiip": "192.0.2.1",
                "apiurl": "",
                "svrip": "",
            },
        },
        options={"energy_interval": 24},
    )


@pytest.fixture
def mock_client():
    """Replace only the external KOCOM communication boundary."""

    with (
        patch(
            "custom_components.kocom_smarthome.api.KocomClient", autospec=True
        ) as factory,
        patch("custom_components.kocom_smarthome.config_flow.KocomClient", factory),
    ):
        client = factory.return_value
        client.login = AsyncMock(return_value=Session(138, 100138, "test-password"))
        client.pairs = AsyncMock(
            return_value=[Pair(1, 138, 100138, "Test wallpad", "", "192.0.2.1")]
        )
        client.register_wallpad = AsyncMock()
        client.energy_readings = AsyncMock(
            return_value=[
                EnergyReading.parse(
                    {
                        "energy": "elec",
                        "date": dt_util.now().strftime("%Y-%m"),
                        "value": 123.4,
                        "avg": 210.0,
                        "price": 18500,
                    }
                )
            ]
        )
        yield client
