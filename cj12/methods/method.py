from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class Method:
    def __init__(self, *, static_id: str, name: str, description: str) -> None:
        self.static_id = static_id
        self.name = name
        self.description = description
        self.on_key_received: Callable[[bytes | None], Awaitable[None]] | None = None

    async def setup(self) -> None: ...
