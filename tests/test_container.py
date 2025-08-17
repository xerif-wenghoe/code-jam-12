import pytest

from cj12.container import Container, InvalidMagicError


def test_encode_decode() -> None:
    c = Container(1, "secret.txt", b"A" * 32, b"Hello, world")

    encoded = bytes(c)
    decoded = Container.from_bytes(encoded)

    assert decoded == c


def test_decode_invalid_bytes() -> None:
    with pytest.raises(InvalidMagicError):
        Container.from_bytes(b"invalid")


def test_hash_preservation() -> None:
    """Test that the data hash is preserved during encoding/decoding."""
    original_hash = b"0123456789abcdef" * 2  # 32 bytes
    c = Container(2, "test.bin", original_hash, b"test data")

    encoded = bytes(c)
    decoded = Container.from_bytes(encoded)

    assert decoded.data_hash == original_hash
    assert len(decoded.data_hash) == 32


def test_hash_different_values() -> None:
    """Test containers with different hash values."""
    hash1 = b"A" * 32
    hash2 = b"B" * 32

    c1 = Container(1, "file1.txt", hash1, b"data1")
    c2 = Container(1, "file1.txt", hash2, b"data1")

    # Same data but different hashes should create different containers
    assert c1 != c2
    assert c1.data_hash != c2.data_hash

    # Encoding should preserve the difference
    encoded1 = bytes(c1)
    encoded2 = bytes(c2)
    assert encoded1 != encoded2

    # Decoding should preserve the hash difference
    decoded1 = Container.from_bytes(encoded1)
    decoded2 = Container.from_bytes(encoded2)
    assert decoded1.data_hash == hash1
    assert decoded2.data_hash == hash2


def test_hash_zero_bytes() -> None:
    """Test container with all-zero hash."""
    zero_hash = b"\x00" * 32
    c = Container(0, "empty.txt", zero_hash, b"")

    encoded = bytes(c)
    decoded = Container.from_bytes(encoded)

    assert decoded.data_hash == zero_hash
    assert all(byte == 0 for byte in decoded.data_hash)


def test_hash_random_bytes() -> None:
    """Test container with random-looking hash bytes."""
    random_hash = bytes(range(32))  # 0x00, 0x01, 0x02, ..., 0x1F
    c = Container(255, "random.data", random_hash, b"random content")

    encoded = bytes(c)
    decoded = Container.from_bytes(encoded)

    assert decoded.data_hash == random_hash
    assert decoded.data_hash == bytes(range(32))


def test_hash_in_encoded_format() -> None:
    """Test that hash appears correctly in the encoded binary format."""
    test_hash = b"HASH" + b"X" * 28  # 32 bytes total
    c = Container(1, "test.txt", test_hash, b"data")

    encoded = bytes(c)

    # The hash should be present in the encoded bytes
    assert test_hash in encoded

    # Verify it's at the expected position after magic, method, lengths, and filename
    magic_size = 4  # "SDET"
    header_size = 12  # 3 * 4 bytes for method, filename_length, data_length
    filename_size = len("test.txt")

    expected_hash_start = magic_size + header_size + filename_size
    expected_hash_end = expected_hash_start + 32

    assert encoded[expected_hash_start:expected_hash_end]
