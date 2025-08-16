from typing import Any

from cj12.dom import InputElement, add_event_listener, elem_by_id
from cj12.methods.method import Method


class PasswordMethod(Method):
    def __init__(self) -> None:
        super().__init__(
            static_id="password",
            name="Password",
            description="Boring old password (deprecated) (please don't use)",
        )

    async def setup(self) -> None:
        self._input = elem_by_id("password-input", InputElement)
        add_event_listener(self._input, "keydown", self._on_key_down)

    async def _on_key_down(self, event: Any) -> None:
        if self.on_key_received is not None and event.key == "Enter":
            await self.on_key_received(self._input.value.encode())
