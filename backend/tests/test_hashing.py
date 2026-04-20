from anasklad.core.security.hashing import hash_password, verify_password


def test_hash_and_verify():
    h = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", h) is True
    assert verify_password("wrong", h) is False


def test_hash_is_nondeterministic():
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2
