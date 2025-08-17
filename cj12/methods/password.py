from typing import Any

from cj12.dom import InputElement, add_event_listener, elem_by_id
from cj12.methods import KeyReceiveCallback


class PasswordMethod:
    byte = 0x01
    static_id = "password"
    name = "Password"
    description = "Plain password (deprecated)"

    on_key_received: KeyReceiveCallback | None = None

    async def setup(self) -> None:
        self._input = elem_by_id("password-input", InputElement)
        add_event_listener(self._input, "keydown", self._on_key_down)

    async def _on_key_down(self, event: Any) -> None:
        if self.on_key_received is not None and event.key == "Enter":
            await self.on_key_received(self._input.value.encode())
