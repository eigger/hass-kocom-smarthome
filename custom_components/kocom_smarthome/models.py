"""Typed views over the KOCOM JSON responses."""

from __future__ import annotations

import re
from collections.abc import Container, Mapping
from dataclasses import dataclass
from typing import Any


def zone_id(zone: int, ikod: int) -> str:
    """Build the 16-character household key: each half zero-padded to 8.

    Every authenticated path is scoped by this value, and it doubles as the
    digest username after login.
    """
    return f"{int(zone):08d}{int(ikod):08d}"


@dataclass(frozen=True, slots=True)
class Session:
    """What ``/api/sphone`` hands back."""

    zone: int
    ikod: int
    password: str

    @property
    def zone_id(self) -> str:
        return zone_id(self.zone, self.ikod)

    @classmethod
    def parse(cls, payload: dict[str, Any]) -> Session:
        return cls(
            zone=int(payload["zone"]),
            ikod=int(payload["id"]),
            password=str(payload["pwd"]),
        )


@dataclass(frozen=True, slots=True)
class Pair:
    """One wallpad registration from ``/api/{zoneid}/pairlist``."""

    idx: int
    zone: int
    ikod: int
    alias: str
    api_url: str
    api_ip: str
    # Not an API host — the SIP stack uses it. Kept only so the debug log can
    # show it when an apartment server turns out to be unreachable.
    svr_ip: str = ""

    @property
    def zone_id(self) -> str:
        return zone_id(self.zone, self.ikod)

    @property
    def base_url(self) -> str:
        """Apartment server base: ``apiurl`` wins, ``apiip`` is the fallback.

        ``svrip``/``svrport`` belong to the SIP stack and are not an API host.
        """
        if self.api_url:
            return self.api_url.rstrip("/")
        return f"http://{self.api_ip}"

    def url_for(self, path: str) -> str:
        return f"{self.base_url}/api/{self.zone_id}/{path}"

    @classmethod
    def parse(cls, payload: dict[str, Any]) -> Pair:
        return cls(
            idx=int(payload.get("idx", 0)),
            zone=int(payload["zone"]),
            ikod=int(payload["id"]),
            alias=str(payload.get("alias") or "").strip(),
            api_url=str(payload.get("apiurl") or "").strip(),
            api_ip=str(payload.get("apiip") or "").strip(),
            svr_ip=str(payload.get("svrip") or "").strip(),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "idx": self.idx,
            "zone": self.zone,
            "id": self.ikod,
            "alias": self.alias,
            "apiurl": self.api_url,
            "apiip": self.api_ip,
            "svrip": self.svr_ip,
        }


MEASURES = ("value", "avg", "price")


def year_month(date: str) -> str:
    """Normalise a reading's ``date`` to ``YYYYMM``.

    Observed as ``YYYY-MM``; digits are extracted rather than sliced so that
    ``YYYYMM``, ``YYYY-MM-DD`` and ``YYYYMMDD`` all land on the same value.
    Returns an empty string when there are not enough digits to tell.
    """
    digits = re.sub(r"\D", "", str(date))
    return digits[:6] if len(digits) >= 6 else ""


@dataclass(frozen=True, slots=True)
class EnergyReading:
    """One row of ``energy/stdcheck/{YYYYMM}``."""

    energy: str
    date: str
    value: float | None
    avg: float | None
    price: float | None
    # Which measures the row actually carried. Apartment servers omit the ones
    # they do not compute, and a sensor for a figure that never arrives is just
    # a permanently unknown entity.
    measures: frozenset[str]

    @property
    def year_month(self) -> str:
        return year_month(self.date)

    def is_previous_month(self, current_month: str) -> bool:
        """True when this row is not for ``current_month`` (``YYYYMM``).

        The apartment server withholds the current month until the reading is
        finalised, so it may answer with last month's rows instead — for some
        energy kinds but not others. A row whose date cannot be read is treated
        as current so it still produces a sensor.
        """
        reading = self.year_month
        if not reading:
            return False
        return reading != current_month

    def measure(self, name: str) -> float | None:
        return {"value": self.value, "avg": self.avg, "price": self.price}[name]

    @classmethod
    def parse(cls, payload: dict[str, Any]) -> EnergyReading:
        def number(key: str) -> float | None:
            raw = payload.get(key)
            if raw is None or raw == "":
                return None
            try:
                return float(raw)
            except (TypeError, ValueError):
                return None

        return cls(
            energy=str(payload["energy"]),
            date=str(payload.get("date") or ""),
            value=number("value"),
            avg=number("avg"),
            price=number("price"),
            measures=frozenset(m for m in MEASURES if m in payload),
        )


@dataclass(frozen=True, slots=True)
class SensorSpec:
    """One sensor: an energy kind, a measure, and which month it covers."""

    energy: str
    measure: str
    previous: bool

    @property
    def translation_key(self) -> str:
        """Key into ``entity.sensor`` of strings.json / translations.

        Display names live in the translation files, not in code — the
        integration ships Korean and English and neither belongs in a module.
        """
        suffix = "_previous" if self.previous else ""
        return f"{self.energy}_{self.measure}{suffix}"

    def unique_id(self, phone_number: str) -> str:
        """Identifier used since the first release.

        Changing the shape would orphan every existing entity along with its
        recorded history, so it is fixed regardless of how the code around it
        is arranged.
        """
        suffix = "_previous" if self.previous else ""
        if self.measure == "price":
            return f"{self.energy}{suffix}_expect_price-{phone_number}"
        return f"{self.energy}{suffix}_{self.measure}_usage-{phone_number}"


def build_specs(
    readings: Mapping[str, Mapping[bool, EnergyReading]],
    known_kinds: Container[str] | None = None,
) -> list[SensorSpec]:
    """Decide which sensors exist, from one month's response.

    The response is the source of truth twice over: only the energy kinds a
    household actually meters come back, and only the measures the apartment
    server computes are present on each row.

    When a kind arrived as last month's row and has no current-month row, a
    current-month sensor is added alongside it and fed the older figure, so the
    history does not develop a gap while the reading is finalised.
    """
    specs: list[SensorSpec] = []
    for energy in sorted(readings):
        if known_kinds is not None and energy not in known_kinds:
            continue
        rows = readings[energy]
        months = dict(rows)
        if True in months and False not in months:
            months[False] = rows[True]
        for previous in sorted(months):
            reading = months[previous]
            specs.extend(
                SensorSpec(energy, measure, previous)
                for measure in MEASURES
                if measure in reading.measures
            )
    return specs
