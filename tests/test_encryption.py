import base64

import pytest

from cj12.aes import decrypt, encrypt


def test_encryption() -> None:
    data = b"Hello, world!"
    key = b"1234567812345678"

    encrypted = encrypt(data, key)
    decrypted = decrypt(encrypted, key)

    assert decrypted == data


def test_wrong_key_size() -> None:
    with pytest.raises(ValueError, match="Incorrect number of bits"):
        _ = encrypt(b"", b"12345")


def test_expected_value() -> None:
    data = b"Hello, world!"
    key = b"1234567812345678"
    expected_b64 = b"AsQnFm+RcXqEbO7q77zcRQ=="

    encrypted = encrypt(data, key)
    assert base64.b64encode(encrypted) == expected_b64
