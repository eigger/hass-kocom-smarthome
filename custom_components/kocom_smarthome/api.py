"""HTTP client for the KOCOM Smart Home+ servers."""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any
from urllib.parse import urlsplit

import aiohttp

from .const import (
    BRANCH_BASE_URL,
    CONNECT_TIMEOUT,
    DIGEST_IKODS,
    DIGEST_MEMBERSHIP,
    DIGEST_REALM,
    LOGGER,
    READ_TIMEOUT,
    SPHONE_TYPE,
    mask,
)
from .digest import build_header, parse_challenge
from .models import EnergyReading, Pair, Session

TIMEOUT = aiohttp.ClientTimeout(connect=CONNECT_TIMEOUT, sock_read=READ_TIMEOUT)


class KocomError(Exception):
    """Base failure talking to KOCOM."""


class KocomAuthError(KocomError):
    """Digest authentication was rejected."""


class KocomResponseError(KocomError):
    """The server answered with an ``error`` payload."""

    def __init__(self, code: int | None, message: str) -> None:
        super().__init__(f"{message} ({code})" if code is not None else message)
        self.code = code
        self.message = message


def dummy_push_token(phone_number: str) -> str:
    """A stand-in for the FCM registration token.

    The server only stores this to address push notifications, which this
    integration never receives. It must stay stable across reconfigurations so
    repeated setups do not pile up dead tokens.
    """
    digest = hashlib.sha256(phone_number.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode()


class KocomClient:
    """Talks digest-authenticated JSON to the branch and apartment servers."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def _request(
        self,
        method: str,
        url: str,
        username: str,
        password: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send one request, answering a digest challenge if we get one.

        The nonce is never cached: an unauthenticated attempt is made first and
        the 401 it draws carries a fresh nonce plus the session cookie it is
        bound to. That is one extra round trip per call, and in exchange there
        is no nonce expiry to manage.
        """
        body = json.dumps(payload).encode() if payload is not None else None
        uri = urlsplit(url).path or "/"
        if query := urlsplit(url).query:
            uri = f"{uri}?{query}"

        try:
            async with self._session.request(
                method, url, data=body, timeout=TIMEOUT
            ) as response:
                if response.status != 401:
                    return self._decode(await response.text(), url)
                challenge = parse_challenge(response.headers.get("WWW-Authenticate"))
                cookie = response.headers.get("Set-Cookie", "").split(";")[0]
                await response.read()

            if not (nonce := challenge.get("nonce")):
                raise KocomAuthError(f"No digest nonce in the challenge from {uri}")

            headers = {
                "Authorization": build_header(
                    username,
                    password,
                    method,
                    uri,
                    challenge.get("realm", DIGEST_REALM),
                    nonce,
                )
            }
            if cookie:
                headers["Cookie"] = cookie

            async with self._session.request(
                method, url, data=body, headers=headers, timeout=TIMEOUT
            ) as response:
                text = await response.text()
                if response.status in (401, 403):
                    raise KocomAuthError(
                        f"Digest authentication rejected for {uri} "
                        f"(HTTP {response.status})"
                    )
                return self._decode(text, url)
        except aiohttp.ClientError as err:
            raise KocomError(f"Request to {uri} failed: {err}") from err
        except TimeoutError as err:
            raise KocomError(f"Request to {uri} timed out") from err

    @staticmethod
    def _decode(text: str, url: str) -> dict[str, Any]:
        """Parse a response body and surface server-reported errors.

        Responses are JSON but are served as ``text/html``, so the content type
        is not consulted. An ``error`` key means failure regardless of the HTTP
        status.
        """
        try:
            payload = json.loads(text)
        except ValueError as err:
            raise KocomError(
                f"Expected JSON from {urlsplit(url).path}, got {text[:80]!r}"
            ) from err

        if not isinstance(payload, dict):
            raise KocomError(f"Expected a JSON object from {urlsplit(url).path}")

        if (code := payload.get("error")) is not None:
            message = str(payload.get("error-msg") or "Unknown error")
            if code in (401, 403):
                raise KocomAuthError(message)
            raise KocomResponseError(code, message)

        return payload

    # --- Authenticated endpoints ------------------------------------------
    #
    # Every path past login is scoped by a household id and signed with the
    # session password. These two helpers cover both servers; anything the app
    # can call — config, control, notices — is one call through them.

    async def branch_request(
        self,
        session: Session,
        path: str,
        method: str = "GET",
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call a path on the central (kbranch) server."""
        return await self._request(
            method,
            f"{BRANCH_BASE_URL}/api/{session.zone_id}/{path}",
            session.zone_id,
            session.password,
            payload,
        )

    async def zone_request(
        self,
        session: Session,
        pair: Pair,
        path: str,
        method: str = "GET",
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Call a path on the apartment server for a paired wallpad."""
        return await self._request(
            method,
            pair.url_for(path),
            pair.zone_id,
            session.password,
            payload,
        )

    # --- Branch server ----------------------------------------------------

    async def login(self, phone_number: str) -> Session:
        """Exchange a phone number for household ids and a session password.

        Two fixed app credentials exist and it is not settled which the server
        still honours, so they are tried in order.
        """
        payload = {
            "phonenum": phone_number,
            "type": SPHONE_TYPE,
            "token": dummy_push_token(phone_number),
        }

        last_error: KocomAuthError | None = None
        for ikod in DIGEST_IKODS:
            try:
                response = await self._request(
                    "POST",
                    f"{BRANCH_BASE_URL}/api/sphone",
                    ikod,
                    DIGEST_MEMBERSHIP,
                    payload,
                )
            except KocomAuthError as err:
                LOGGER.debug("sphone rejected ikod %s: %s", ikod, err)
                last_error = err
                continue

            LOGGER.debug("sphone accepted ikod %s", ikod)
            try:
                return Session.parse(response)
            except (KeyError, TypeError, ValueError) as err:
                raise KocomError(f"Unexpected sphone response: {err}") from err

        raise last_error or KocomAuthError("sphone login failed")

    async def pairs(self, session: Session) -> list[Pair]:
        """List the wallpads this household is registered against."""
        response = await self.branch_request(session, "pairlist")
        entries = response.get("list") or []
        if not isinstance(entries, list):
            raise KocomError("pairlist did not contain a list")

        pairs = []
        for entry in entries:
            try:
                pairs.append(Pair.parse(entry))
            except (KeyError, TypeError, ValueError) as err:
                LOGGER.warning("Skipping malformed pairlist entry: %s", err)
        return pairs

    async def register_wallpad(self, session: Session, wallpad_number: str) -> None:
        """Claim the household using the code shown on the wallpad."""
        await self.branch_request(
            session, "pairnum", "POST", {"pairnum": wallpad_number}
        )

    # --- Apartment server -------------------------------------------------

    async def energy_readings(
        self, session: Session, pair: Pair, month: str
    ) -> list[EnergyReading]:
        """Fetch one month of metering, as ``YYYYMM``.

        The apartment server may answer with last month's rows for some or all
        energy kinds; that is reported as-is and sorted out by the coordinator.
        """
        LOGGER.debug(
            "Fetching energy for %s from %s",
            month,
            mask(urlsplit(pair.base_url).netloc, keep=0),
        )
        response = await self.zone_request(
            session, pair, f"energy/stdcheck/{month}"
        )

        entries = response.get("list") or []
        if not isinstance(entries, list):
            raise KocomError("energy/stdcheck did not contain a list")

        readings = []
        for entry in entries:
            try:
                readings.append(EnergyReading.parse(entry))
            except (KeyError, TypeError, ValueError) as err:
                LOGGER.warning("Skipping malformed energy entry: %s", err)
        return readings
