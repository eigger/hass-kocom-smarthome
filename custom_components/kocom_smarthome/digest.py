"""RFC 2069 HTTP Digest.

The servers challenge with realm and nonce only — no qop, no opaque, no
algorithm — so the classic three-hash form applies.
"""

from __future__ import annotations

import hashlib
import re

_PARAM_RE = re.compile(r'(\w+)\s*=\s*(?:"([^"]*)"|([^\s,]+))')


def parse_challenge(header: str | None) -> dict[str, str]:
    """Pull the parameters out of a ``WWW-Authenticate`` header.

    Returns an empty mapping when the header is missing or is not a Digest
    challenge.
    """
    if not header or not header.lstrip().lower().startswith("digest"):
        return {}
    body = header.lstrip()[len("digest") :]
    return {m.group(1).lower(): m.group(2) or m.group(3) for m in _PARAM_RE.finditer(body)}


def _md5(value: str) -> str:
    return hashlib.md5(value.encode()).hexdigest()


def build_header(
    username: str, password: str, method: str, uri: str, realm: str, nonce: str
) -> str:
    """Build the ``Authorization`` header for a digest challenge.

    ``uri`` must be the full request path, including any prefix the host adds
    (``/kbranch/api/sphone`` on the HTTPS host) and any query string.
    """
    ha1 = _md5(f"{username}:{realm}:{password}")
    ha2 = _md5(f"{method.upper()}:{uri}")
    response = _md5(f"{ha1}:{nonce}:{ha2}")
    return (
        f'Digest username="{username}", realm="{realm}", '
        f'nonce="{nonce}", uri="{uri}", response="{response}"'
    )
