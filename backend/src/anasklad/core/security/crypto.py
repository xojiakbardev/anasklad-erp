"""Symmetric encryption for secrets at rest (Fernet)."""
from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken


class CryptoService:
    """Wraps Fernet with friendly errors and lazy validation."""

    def __init__(self, key: str) -> None:
        if not key:
            raise ValueError("Fernet key is required (see CREDENTIALS_FERNET_KEY)")
        try:
            self._fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid Fernet key format: {e}") from e

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode()).decode()
        except InvalidToken as e:
            raise ValueError("failed to decrypt — key mismatch or data tampered") from e

    @staticmethod
    def generate_key() -> str:
        """For `python -m anasklad.scripts.gen_fernet_key`."""
        return Fernet.generate_key().decode()
