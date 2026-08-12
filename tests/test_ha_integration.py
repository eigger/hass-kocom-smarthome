"""End-to-end check of KocomClient against a fake KOCOM server.

Everything in tests/test_digest.py and tests/test_models.py is pure Python and
needs no Home Assistant. This file imports custom_components.kocom_smarthome.api,
which imports .const for its own HA-free constants (BRANCH_BASE_URL, timeouts,
mask()) — but const.py also imports `SensorDeviceClass`/`SensorStateClass` at
module level for ENERGY_META, so importing api.py at all requires Home
Assistant to be installed regardless of whether api.py itself uses those
names. Home Assistant is therefore a real, unavoidable dependency for this
file specifically, which is why it is excluded from the fast matrix job and
run only in the job pinned to the minimum supported Home Assistant version
(see .github/workflows/tests.yml).
"""

import json

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from custom_components.kocom_smarthome import api as api_mod
from custom_components.kocom_smarthome.api import (
    KocomAuthError,
    KocomClient,
    KocomResponseError,
)
from custom_components.kocom_smarthome.const import mask
from custom_components.kocom_smarthome.coordinator import KocomEnergyCoordinator
from custom_components.kocom_smarthome.digest import build_header
from custom_components.kocom_smarthome.models import EnergyReading

# pytest.ini sets asyncio_mode = auto, so async def tests are picked up
# without a marker — this file mixes them with plain sync tests below.

NONCE = "9d37def8022c1f432587c4a7586b1300"
IKOD = "Android!1000002"
MEMBERSHIP = "4990e9e16a532aa9010403b01e0ee52a"
SESSION_PW = "sess-pw"
PHONE = "01012345678"


def make_app(request_log, sphone_ikod=IKOD, session_password=SESSION_PW):
    """A minimal stand-in for both KOCOM servers on one aiohttp app.

    Digest realm, challenge shape, and error body match what the real
    branch server sends — confirmed against a live, unauthenticated request.
    """

    async def handler(request: web.Request) -> web.Response:
        request_log.append((request.method, request.path))
        auth = request.headers.get("Authorization")

        accepted = [
            build_header(u, p, request.method, request.path, "kbranch", NONCE)
            for u, p in ((sphone_ikod, MEMBERSHIP), ("0000013800100138", session_password))
        ]
        if auth not in accepted:
            return web.Response(
                status=401,
                text='{"error":401, "error-msg":"Unauthorized"}',
                headers={
                    "WWW-Authenticate": f'Digest realm="kbranch",nonce="{NONCE}"',
                    "Set-Cookie": "PHPSESSID=abc123; path=/",
                },
                content_type="text/html",
            )

        if request.path.endswith("/sphone"):
            body = json.loads(await request.text())
            assert body["phonenum"] == PHONE
            assert body["type"] == "Android!1000001"
            payload = {"zone": 138, "id": 100138, "pwd": SESSION_PW}
        elif request.path.endswith("/pairlist"):
            payload = {
                "list": [
                    {
                        "idx": 1,
                        "zone": 138,
                        "id": 100138,
                        "alias": "우리집",
                        "svrip": "10.0.0.9",
                        "svrport": 5060,
                        "apiip": "127.0.0.1",
                        "apiurl": "",
                    }
                ]
            }
        elif request.path.endswith("/pairnum"):
            body = json.loads(await request.text())
            if body.get("pairnum") != "12345678":
                return web.Response(
                    text='{"error":90,"error-msg":"PairNum Fail"}',
                    content_type="text/html",
                )
            payload = {}
        elif "energy/stdcheck" in request.path:
            payload = {
                "cnt": 2,
                "list": [
                    {"date": "2026-08", "energy": "elec", "value": 123.4,
                     "avg": 210.0, "price": 18500},
                    {"date": "2026-07", "energy": "gas", "value": 12.3,
                     "avg": 20.1, "price": 9800},
                ],
            }
        else:
            payload = {}
        return web.Response(text=json.dumps(payload), content_type="text/html")

    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handler)
    return app


@pytest.fixture
async def kocom(monkeypatch):
    """A KocomClient wired to the fake server, with request paths logged."""
    log: list[tuple[str, str]] = []
    server = TestServer(make_app(log))
    client = TestClient(server)
    await client.start_server()

    monkeypatch.setattr(api_mod, "BRANCH_BASE_URL", str(client.make_url("/kbranch")))

    async with aiohttp.ClientSession() as session:
        yield KocomClient(session), client, log

    await client.close()


async def test_login_authenticates_and_parses_zone_and_password(kocom):
    client, _, _ = kocom
    session = await client.login(PHONE)
    assert session.zone == 138
    assert session.ikod == 100138
    assert session.password == SESSION_PW
    # %08d%08d, not a field-width assumption that only holds for some zones.
    assert session.zone_id == "0000013800100138"


async def test_login_falls_back_to_the_legacy_ikod(monkeypatch):
    """Which of the two fixed ikod values the server accepts is unverified,
    so both are tried in order."""
    log: list[tuple[str, str]] = []
    server = TestServer(make_app(log, sphone_ikod="Android!1000001"))
    client = TestClient(server)
    await client.start_server()
    monkeypatch.setattr(api_mod, "BRANCH_BASE_URL", str(client.make_url("/kbranch")))

    async with aiohttp.ClientSession() as session:
        result = await KocomClient(session).login(PHONE)
    assert result.zone_id == "0000013800100138"
    await client.close()


async def test_wrong_credentials_raise_without_looping(kocom):
    client, http_client, log = kocom
    before = len(log)
    with pytest.raises(KocomAuthError):
        await client._request(
            "GET", str(http_client.make_url("/kbranch/api/x")), "nobody", "wrong"
        )
    # One unauthenticated attempt, one authenticated retry — never more.
    assert len(log) - before == 2


async def test_pairs_prefers_apiurl_but_the_fixture_has_none_so_falls_back(kocom):
    client, _, _ = kocom
    session = await client.login(PHONE)
    pairs = await client.pairs(session)
    assert len(pairs) == 1
    pair = pairs[0]
    assert pair.alias == "우리집"
    assert pair.base_url == "http://127.0.0.1"  # apiip fallback, not svrip


async def test_register_wallpad_reports_the_servers_own_failure_message(kocom):
    client, _, _ = kocom
    session = await client.login(PHONE)
    with pytest.raises(KocomResponseError, match="PairNum Fail"):
        await client.register_wallpad(session, "00000000")


async def test_register_wallpad_succeeds_with_the_right_code(kocom):
    client, _, _ = kocom
    session = await client.login(PHONE)
    await client.register_wallpad(session, "12345678")  # must not raise


async def test_energy_readings_round_trip_through_real_json(kocom):
    client, http_client, _ = kocom
    session = await client.login(PHONE)
    pair = (await client.pairs(session))[0]
    pair = type(pair)(
        pair.idx, pair.zone, pair.ikod, pair.alias,
        str(http_client.make_url("/")).rstrip("/"), pair.api_ip, pair.svr_ip,
    )

    readings = await client.energy_readings(session, pair, "202608")
    assert len(readings) == 2
    assert isinstance(readings[0], EnergyReading)

    elec, gas = readings
    assert elec.energy == "elec" and elec.value == 123.4
    assert elec.is_previous_month("202608") is False
    assert gas.energy == "gas" and gas.is_previous_month("202608") is True


async def test_digest_uri_includes_whatever_prefix_the_host_actually_uses(kocom):
    """The /kbranch path prefix is part of the digest hash, not decoration —
    if the client hashed the wrong uri, every request above would already
    have failed with KocomAuthError instead of succeeding."""
    client, _http_client, log = kocom
    await client.login(PHONE)
    assert any(path.startswith("/kbranch/api/sphone") for _, path in log)


# --- month rollover ---------------------------------------------------------
#
# The reference implementation got this wrong twice (a lookup that always
# treated every row as "previous month" because of a botched date-substring
# calculation, then a second pass to fix that calculation). This is the
# runtime path a sensor actually calls, so it is worth pinning down
# separately from the pure date-comparison tests in test_models.py.
#
# KocomEnergyCoordinator subclasses DataUpdateCoordinator, whose __init__
# needs a running HomeAssistant instance we don't have here — reading_for()
# only ever touches self.data, so object.__new__ sidesteps that entirely.


def _coordinator_with(data):
    coordinator = object.__new__(KocomEnergyCoordinator)
    coordinator.data = data
    return coordinator


def test_reading_for_prefers_this_months_own_row_when_present():
    coordinator = _coordinator_with(
        {"elec": {False: "current-row", True: "previous-row"}}
    )
    assert coordinator.reading_for("elec", previous=False) == "current-row"
    assert coordinator.reading_for("elec", previous=True) == "previous-row"


def test_reading_for_falls_back_to_last_month_on_the_1st():
    """The apartment server has not finalised this month yet — day 1 of a new
    month, before that happens, is exactly when a household only has a row
    filed under "previous"."""
    coordinator = _coordinator_with({"elec": {True: "previous-row"}})
    assert coordinator.reading_for("elec", previous=False) == "previous-row"


def test_reading_for_previous_sensor_does_not_borrow_the_current_row():
    """A _previous entity is not "whatever the other one isn't" — if there is
    no previous-month row, it goes unknown rather than showing this month's
    figure under the wrong label."""
    coordinator = _coordinator_with({"elec": {False: "current-row"}})
    assert coordinator.reading_for("elec", previous=True) is None


def test_reading_for_is_none_when_the_energy_kind_is_entirely_absent():
    """A different energy kind having data this cycle must not leak into one
    that has none — this is the "unknown state, not a crash" outcome when the
    server drops an energy kind for a poll or two."""
    coordinator = _coordinator_with({"gas": {False: "gas-row"}})
    assert coordinator.reading_for("elec", previous=False) is None
    assert coordinator.reading_for("elec", previous=True) is None


def test_reading_for_survives_no_data_yet():
    """Before the first successful refresh, coordinator.data is None."""
    coordinator = _coordinator_with(None)
    assert coordinator.reading_for("elec", previous=False) is None


async def test_a_household_with_no_previous_month_history_survives_rollover(kocom):
    """End-to-end version of the fallback above: a household that has never
    needed a _previous sensor (every past poll had clean current-month data)
    hits a month where the server briefly answers with last month's row only
    — the coordinator update must not raise, and the existing (non-previous)
    sensor must be able to read a value through it."""
    client, http_client, _ = kocom
    session = await client.login(PHONE)
    pair = (await client.pairs(session))[0]
    pair = type(pair)(
        pair.idx, pair.zone, pair.ikod, pair.alias,
        str(http_client.make_url("/")).rstrip("/"), pair.api_ip, pair.svr_ip,
    )

    # energy/stdcheck/202608 in the fixture server answers with one row dated
    # "2026-08" (elec) and one dated "2026-07" (gas) — treat "202608" as the
    # freshly rolled-over month and confirm gas resolves through the fallback
    # exactly as it would from a real coordinator poll on the 1st.
    readings = await client.energy_readings(session, pair, "202608")
    by_kind = {}
    for reading in readings:
        by_kind.setdefault(reading.energy, {})[reading.is_previous_month("202608")] = reading

    coordinator = _coordinator_with(by_kind)
    assert coordinator.reading_for("elec", previous=False) is by_kind["elec"][False]
    gas_reading = coordinator.reading_for("gas", previous=False)
    assert gas_reading is by_kind["gas"][True]
    assert gas_reading.energy == "gas"


# --- log masking -------------------------------------------------------------
#
# coordinator.py logs the apartment server address with mask(pair.base_url,
# keep=0) — "reveal nothing". Python's own str[-0:] slicing means -0 == 0, so
# a naive "*" * (len - keep) + text[-keep:] silently returns the *entire*
# original string when keep=0, defeating the mask in exactly the call site
# that most needs it. Caught during live testing; pinned here so it cannot
# regress silently again.


def test_mask_keeps_the_last_few_characters_by_default():
    assert mask("01012345678") == "*******5678"


def test_mask_with_keep_zero_reveals_nothing():
    assert mask("https://apt.example.com", keep=0) == "*" * len("https://apt.example.com")


def test_mask_with_negative_keep_also_reveals_nothing():
    assert mask("secret", keep=-1) == "******"


def test_mask_never_reveals_more_than_the_input_has():
    assert mask("ab", keep=4) == "**"


def test_mask_of_empty_string_is_empty():
    assert mask("", keep=0) == ""
    assert mask("") == ""
