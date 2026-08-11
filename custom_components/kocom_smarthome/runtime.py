"""What a loaded config entry carries at runtime.

The integration ships energy metering only, but the authenticated session and
the paired wallpad are not specific to metering — the app reaches control and
config endpoints through exactly the same credentials. Keeping them here rather
than inside the energy coordinator means a second feature area becomes another
field on this container plus another entry in ``PLATFORMS``, not a rewrite of
the setup path.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry

if TYPE_CHECKING:
    from .api import KocomClient
    from .coordinator import KocomEnergyCoordinator
    from .models import Pair, Session


@dataclass
class KocomRuntimeData:
    """Live objects shared by every platform of one config entry."""

    client: KocomClient
    session: Session
    pair: Pair
    energy: KocomEnergyCoordinator


type KocomConfigEntry = ConfigEntry[KocomRuntimeData]
