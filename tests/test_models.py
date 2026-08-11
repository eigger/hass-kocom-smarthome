"""Identifiers, date handling and sensor selection."""

import pytest

from custom_components.kocom_smarthome.models import (
    EnergyReading,
    Pair,
    Session,
    build_specs,
    year_month,
    zone_id,
)

KINDS = ("elec", "gas", "heat", "hotwater", "water")


# --- zone id --------------------------------------------------------------


@pytest.mark.parametrize(
    ("zone", "ikod", "expected"),
    [
        (138, 100138, "0000013800100138"),
        (1, 1, "0000000100000001"),
        (12345678, 87654321, "1234567887654321"),
    ],
)
def test_zone_id_pads_each_half_to_eight(zone, ikod, expected):
    assert zone_id(zone, ikod) == expected
    assert len(zone_id(zone, ikod)) == 16


def test_zone_id_does_not_assume_field_widths():
    """A two-digit zone must not shift the household id left.

    The previous implementation concatenated fixed prefixes, which only
    produced a valid key when the zone was three digits wide.
    """
    assert zone_id(12, 100138) == "0000001200100138"
    assert zone_id(1234, 100138) == "0000123400100138"


def test_session_derives_its_zone_id():
    session = Session.parse({"zone": 138, "id": 100138, "pwd": "secret"})
    assert session.zone_id == "0000013800100138"
    assert session.password == "secret"


# --- pair -----------------------------------------------------------------


def test_pair_prefers_apiurl_over_apiip():
    pair = Pair.parse(
        {
            "idx": 1,
            "zone": 138,
            "id": 100138,
            "alias": "우리집",
            "svrip": "10.0.0.9",
            "svrport": 5060,
            "apiip": "192.168.0.1",
            "apiurl": "https://apt.example.com/",
        }
    )
    assert pair.base_url == "https://apt.example.com"
    assert pair.url_for("energy/stdcheck/202608") == (
        "https://apt.example.com/api/0000013800100138/energy/stdcheck/202608"
    )


def test_pair_falls_back_to_apiip_when_apiurl_is_blank():
    pair = Pair.parse(
        {"zone": 138, "id": 100138, "apiip": "192.168.0.1", "apiurl": "   "}
    )
    assert pair.base_url == "http://192.168.0.1"


def test_pair_never_uses_the_sip_address():
    """svrip/svrport belong to the video-call stack, not the API."""
    pair = Pair.parse(
        {"zone": 1, "id": 2, "svrip": "10.9.9.9", "apiip": "192.168.0.1", "apiurl": ""}
    )
    assert "10.9.9.9" not in pair.url_for("x")


def test_pair_round_trips_through_storage():
    payload = {
        "idx": 3,
        "zone": 138,
        "id": 100138,
        "alias": "우리집",
        "apiurl": "https://apt.example.com",
        "apiip": "192.168.0.1",
    }
    assert Pair.parse(Pair.parse(payload).as_dict()) == Pair.parse(payload)


# --- reading dates --------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2026-08", "202608"),
        ("202608", "202608"),
        ("2026-08-31", "202608"),
        ("20260831", "202608"),
        ("2026/08", "202608"),
        ("", ""),
        ("08", ""),
        (None, ""),
    ],
)
def test_year_month_normalises_every_observed_shape(raw, expected):
    assert year_month(raw) == expected


def test_a_row_for_the_requested_month_is_current():
    reading = EnergyReading.parse(
        {"energy": "elec", "date": "2026-08", "value": 1.0, "avg": 2.0, "price": 3}
    )
    assert reading.is_previous_month("202608") is False


def test_a_row_for_another_month_is_previous():
    reading = EnergyReading.parse({"energy": "elec", "date": "2026-07"})
    assert reading.is_previous_month("202608") is True


def test_an_unreadable_date_is_treated_as_current():
    """Better a sensor with an odd date than no sensor at all."""
    reading = EnergyReading.parse({"energy": "elec", "date": "?"})
    assert reading.is_previous_month("202608") is False


def test_reading_coerces_numbers_and_tolerates_gaps():
    reading = EnergyReading.parse(
        {"energy": "gas", "date": "2026-08", "value": "12.5", "price": None}
    )
    assert reading.value == 12.5
    assert reading.avg is None
    assert reading.price is None


def test_reading_measure_lookup():
    reading = EnergyReading.parse(
        {"energy": "gas", "date": "2026-08", "value": 1, "avg": 2, "price": 3}
    )
    assert (reading.measure("value"), reading.measure("avg"), reading.measure("price")) == (
        1.0,
        2.0,
        3.0,
    )


# --- sensor selection -----------------------------------------------------


FULL = {"value": 1.0, "avg": 2.0, "price": 3}


def readings(*rows, measures=None):
    """Build the coordinator's ``{energy: {previous: reading}}`` shape."""
    out = {}
    for energy, month, current in rows:
        payload = {"energy": energy, "date": month}
        payload.update(FULL if measures is None else measures)
        reading = EnergyReading.parse(payload)
        out.setdefault(energy, {})[month != current] = reading
    return out


def slots(specs):
    return sorted({(spec.energy, spec.previous) for spec in specs})


def test_only_metered_kinds_get_sensors():
    specs = build_specs(readings(("elec", "202608", "202608")), KINDS)
    assert slots(specs) == [("elec", False)]
    assert sorted(spec.measure for spec in specs) == ["avg", "price", "value"]


def test_current_month_only():
    data = readings(("elec", "202608", "202608"), ("gas", "202608", "202608"))
    assert slots(build_specs(data, KINDS)) == [("elec", False), ("gas", False)]


def test_previous_month_only_also_fills_the_current_month():
    """Otherwise the graph goes blank until the reading is finalised."""
    data = readings(("elec", "202607", "202608"))
    assert slots(build_specs(data, KINDS)) == [("elec", False), ("elec", True)]


def test_mixed_months_across_kinds():
    data = readings(
        ("elec", "202608", "202608"),
        ("gas", "202607", "202608"),
        ("water", "202608", "202608"),
    )
    assert slots(build_specs(data, KINDS)) == [
        ("elec", False),
        ("gas", False),
        ("gas", True),
        ("water", False),
    ]


def test_a_kind_present_for_both_months_is_not_duplicated():
    data = readings(("elec", "202608", "202608"), ("elec", "202607", "202608"))
    assert slots(build_specs(data, KINDS)) == [("elec", False), ("elec", True)]


def test_unknown_energy_kinds_are_dropped():
    data = readings(("elec", "202608", "202608"), ("plasma", "202608", "202608"))
    assert slots(build_specs(data, KINDS)) == [("elec", False)]


def test_no_readings_means_no_sensors():
    assert build_specs({}, KINDS) == []


def test_only_the_measures_the_server_sent_get_sensors():
    """A figure the apartment server never computes would sit at unknown."""
    data = readings(("elec", "202608", "202608"), measures={"value": 1.0, "avg": 2.0})
    assert sorted(spec.measure for spec in build_specs(data, KINDS)) == ["avg", "value"]


def test_a_row_with_only_a_household_figure_makes_one_sensor():
    data = readings(("gas", "202608", "202608"), measures={"value": 1.0})
    specs = build_specs(data, KINDS)
    assert [(s.energy, s.measure, s.previous) for s in specs] == [("gas", "value", False)]


def test_a_null_measure_still_counts_as_present():
    """The key being there means the server reports it, just not this month."""
    data = readings(("elec", "202608", "202608"), measures={"value": 1.0, "price": None})
    assert sorted(spec.measure for spec in build_specs(data, KINDS)) == ["price", "value"]


def test_the_filled_current_month_inherits_the_previous_row_measures():
    data = readings(("elec", "202607", "202608"), measures={"value": 1.0, "avg": 2.0})
    specs = build_specs(data, KINDS)
    assert sorted((s.measure, s.previous) for s in specs) == [
        ("avg", False),
        ("avg", True),
        ("value", False),
        ("value", True),
    ]


# --- unique ids -----------------------------------------------------------


@pytest.mark.parametrize(
    ("energy", "measure", "previous", "expected"),
    [
        ("elec", "value", False, "elec_value_usage-01012345678"),
        ("elec", "avg", False, "elec_avg_usage-01012345678"),
        ("elec", "price", False, "elec_expect_price-01012345678"),
        ("gas", "value", True, "gas_previous_value_usage-01012345678"),
        ("gas", "price", True, "gas_previous_expect_price-01012345678"),
    ],
)
def test_unique_ids_match_the_shape_shipped_since_the_first_release(
    energy, measure, previous, expected
):
    """These are pinned: a change would orphan every existing entity."""
    from custom_components.kocom_smarthome.models import SensorSpec

    assert SensorSpec(energy, measure, previous).unique_id("01012345678") == expected


def test_every_generated_sensor_has_a_distinct_id():
    data = readings(
        ("elec", "202608", "202608"),
        ("gas", "202607", "202608"),
        ("water", "202607", "202608"),
    )
    specs = build_specs(data, KINDS)
    ids = [spec.unique_id("01012345678") for spec in specs]
    assert len(ids) == len(set(ids))
