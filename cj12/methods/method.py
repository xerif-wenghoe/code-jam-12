from typing import Protocol

from cj12.methods import KeyReceiveCallback


class Method(Protocol):
    static_id: str
    name: str
    description: str

    on_key_received: KeyReceiveCallback | None = None

    async def setup(self) -> None: ...
