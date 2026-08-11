"""Digest authentication."""

import pytest

from custom_components.kocom_smarthome.digest import build_header, parse_challenge


def test_parses_the_challenge_the_server_actually_sends():
    header = 'Digest realm="kbranch",nonce="9d37def8022c1f432587c4a7586b1300"'
    assert parse_challenge(header) == {
        "realm": "kbranch",
        "nonce": "9d37def8022c1f432587c4a7586b1300",
    }


def test_parses_unquoted_and_spaced_parameters():
    header = 'Digest realm=kbranch, nonce="abc", qop="auth", stale=FALSE'
    parsed = parse_challenge(header)
    assert parsed["realm"] == "kbranch"
    assert parsed["nonce"] == "abc"
    assert parsed["stale"] == "FALSE"


@pytest.mark.parametrize("header", [None, "", "Basic realm=\"kbranch\""])
def test_ignores_anything_that_is_not_a_digest_challenge(header):
    assert parse_challenge(header) == {}


def test_response_hash_is_the_rfc_2069_three_step():
    # HA1 = md5("Android!1000002:kbranch:secret")
    # HA2 = md5("POST:/kbranch/api/sphone")
    # response = md5(HA1 + ":" + nonce + ":" + HA2)
    header = build_header(
        "Android!1000002",
        "secret",
        "POST",
        "/kbranch/api/sphone",
        "kbranch",
        "0123456789abcdef0123456789abcdef",
    )
    assert 'response="d187a33a63e0f4ffce5f0a585af744f1"' in header


def test_header_carries_every_parameter_the_server_needs():
    header = build_header(
        "0000013800100138",
        "pw",
        "GET",
        "/api/0000013800100138/energy/stdcheck/202608",
        "kbranch",
        "nonce123",
    )
    assert header.startswith("Digest ")
    for fragment in (
        'username="0000013800100138"',
        'realm="kbranch"',
        'nonce="nonce123"',
        'uri="/api/0000013800100138/energy/stdcheck/202608"',
    ):
        assert fragment in header


def test_method_case_does_not_change_the_hash():
    args = ("user", "pw", "get", "/api/x", "kbranch", "n")
    upper = ("user", "pw", "GET", "/api/x", "kbranch", "n")
    assert build_header(*args) == build_header(*upper)


def test_uri_is_part_of_the_hash():
    """The HTTPS host prefixes paths with /kbranch, so the two must differ."""
    plain = build_header("u", "p", "POST", "/api/sphone", "kbranch", "n")
    prefixed = build_header("u", "p", "POST", "/kbranch/api/sphone", "kbranch", "n")
    assert plain != prefixed
