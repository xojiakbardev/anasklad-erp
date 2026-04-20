from datetime import timedelta

import pytest

from anasklad.core.http.errors import AuthError
from anasklad.core.security.jwt import JwtService


def test_issue_and_verify_access_token():
    svc = JwtService(secret="test_secret_at_least_32_characters_long", access_ttl_minutes=5)
    pair = svc.issue_pair("user-123", tenant_id="tenant-1")
    payload = svc.verify(pair.access_token, expected_type="access")
    assert payload.sub == "user-123"
    assert payload.tenant_id == "tenant-1"
    assert payload.type == "access"


def test_refresh_token_rejected_for_access_use():
    svc = JwtService(secret="test_secret_at_least_32_characters_long")
    pair = svc.issue_pair("user-123")
    with pytest.raises(AuthError):
        svc.verify(pair.refresh_token, expected_type="access")


def test_tampered_token_rejected():
    svc = JwtService(secret="test_secret_at_least_32_characters_long")
    pair = svc.issue_pair("user-123")
    bad = pair.access_token[:-4] + "xxxx"
    with pytest.raises(AuthError):
        svc.verify(bad)
