"""Generate a Fernet key for CREDENTIALS_FERNET_KEY.

Usage:
    python scripts/gen_fernet_key.py
"""
from cryptography.fernet import Fernet

if __name__ == "__main__":
    print(Fernet.generate_key().decode())
