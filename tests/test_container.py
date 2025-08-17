import pytest

from cj12.container import Container, InvalidMagicError


def test_encode_decode() -> None:
    c = Container(1, "secret.txt", b"Hello, world")

    encoded = bytes(c)
    decoded = Container.from_bytes(encoded)

    assert decoded == c


def test_decode_invalid_bytes() -> None:
    with pytest.raises(InvalidMagicError):
        Container.from_bytes(b"invalid")
