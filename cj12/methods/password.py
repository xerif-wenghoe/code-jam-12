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
        self._input = [None] * 2
        self._warn_mismatch = elem_by_id("warn-mismatch")
        for i in range(2):
            self._input[i] = elem_by_id(f"password-input{i}", InputElement)
            add_event_listener(self._input[i], "keydown", self._on_key_down)


    async def _on_key_down(self, event: Any) -> None:
        if self.on_key_received is None:
            return
        if self._input[0].value != self._input[1].value:
            self._warn_mismatch.style.color = "#FF0000"
            self._warn_mismatch.innerText = "Passwords don't match!"
            await self.on_key_received(None)
        else:
            self._warn_mismatch.style.color = "#00FF00"
            self._warn_mismatch.innerText = "- OK -"
            await self.on_key_received(self._input[0].value.encode())
