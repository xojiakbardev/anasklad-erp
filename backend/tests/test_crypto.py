import pytest

from anasklad.core.security.crypto import CryptoService


def test_roundtrip():
    key = CryptoService.generate_key()
    c = CryptoService(key)
    assert c.decrypt(c.encrypt("secret")) == "secret"


def test_wrong_key_fails():
    c1 = CryptoService(CryptoService.generate_key())
    c2 = CryptoService(CryptoService.generate_key())
    encrypted = c1.encrypt("secret")
    with pytest.raises(ValueError):
        c2.decrypt(encrypted)


def test_empty_key_rejected():
    with pytest.raises(ValueError):
        CryptoService("")


def test_malformed_key_rejected():
    with pytest.raises(ValueError):
        CryptoService("not-a-real-fernet-key")
