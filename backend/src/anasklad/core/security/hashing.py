"""Argon2 password hashing."""
from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, password)
    except VerifyMismatchError:
        return False


def needs_rehash(hashed: str) -> bool:
    return _hasher.check_needs_rehash(hashed)
