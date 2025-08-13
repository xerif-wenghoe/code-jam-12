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
