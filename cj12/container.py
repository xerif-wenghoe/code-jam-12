from __future__ import annotations

import struct
from dataclasses import dataclass


class InvalidMagicError(Exception): ...


MAGIC = b"SDET"


@dataclass(frozen=True)
class Container:
    method: int
    original_filename: str
    data_hash: bytes
    data: bytes

    def __bytes__(self) -> bytes:
        filename_bytes = self.original_filename.encode("utf-8")

        return MAGIC + struct.pack(
            f"<III{len(filename_bytes)}s32s{len(self.data)}s",
            int(self.method),
            len(filename_bytes),
            len(self.data),
            filename_bytes,
            self.data_hash,
            self.data,
        )

    @staticmethod
    def from_bytes(raw: bytes) -> Container:
        if not raw.startswith(MAGIC):
            raise InvalidMagicError

        offset = len(MAGIC)
        method, filename_length, data_length = struct.unpack(
            "<III",
            raw[offset : offset + 12],
        )
        offset += 12

        filename_bytes = struct.unpack(
            f"<{filename_length}s",
            raw[offset : offset + filename_length],
        )[0]
        filename = filename_bytes.decode("utf-8")
        offset += filename_length

        data_hash = struct.unpack("32s", raw[offset : offset + 32])[0]
        offset += 32

        data = struct.unpack(
            f"<{data_length}s",
            raw[offset : offset + data_length],
        )[0]

        return Container(
            method=method,
            original_filename=filename,
            data_hash=data_hash,
            data=data,
        )
