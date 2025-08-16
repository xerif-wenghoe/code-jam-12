from collections.abc import Awaitable, Callable
from typing import Any

from js import FileReader, alert, document

from cj12.dom import (
    ButtonElement,
    InputElement,
    add_event_listener,
    elem_by_id,
    fetch_text,
)


class App:
    async def start(self) -> None:
        document.title = "Super Duper Encryption Tool"
        document.body.innerHTML = await fetch_text("/ui.html")

        self._data: bytes | None = None
        self._key: bytes | None = None

        self._file_input = FileInput(self._on_data_received)
        self._methods = Methods(self._on_key_received)

        self._encrypt_button = elem_by_id("encrypt-button", ButtonElement)
        self._decrypt_button = elem_by_id("decrypt-button", ButtonElement)
        add_event_listener(self._encrypt_button, "click", self._on_encrypt_button)
        add_event_listener(self._decrypt_button, "click", self._on_decrypt_button)

    async def _on_data_received(self, data: bytes) -> None:
        self._data = data
        self._enable_encrypt_decrypt_buttons_if_valid()

    async def _on_key_received(self, key: bytes) -> None:
        self._key = key
        self._enable_encrypt_decrypt_buttons_if_valid()

    def _enable_encrypt_decrypt_buttons_if_valid(self) -> None:
        if self._data is not None and self._key is not None:
            self._encrypt_button.disabled = False
            self._decrypt_button.disabled = False

    async def _on_encrypt_button(self, _: object) -> None:
        data, key = self._ensure_data_and_key()

    async def _on_decrypt_button(self, _: object) -> None:
        data, key = self._ensure_data_and_key()

    def _ensure_data_and_key(self) -> tuple[bytes, bytes]:
        if self._data is None or self._key is None:
            msg = "Data or key not set"
            raise ValueError(msg)

        return (self._data, self._key)


class FileInput:
    def __init__(self, on_data_received: Callable[[bytes], Awaitable[None]]) -> None:
        self._on_data_received = on_data_received

        self._reader = FileReader.new()
        add_event_listener(self._reader, "load", self._on_data_load)
        add_event_listener(self._reader, "error", self._on_error)
        add_event_listener(elem_by_id("file-input"), "change", self._on_file_change)

    def _on_file_change(self, event: Any) -> None:
        file = event.target.files.item(0)
        elem_by_id("dropzone").innerText = f"{file.name} ({file.size / 1024:.2f} KB)"
        self._reader.readAsBinaryString(file)

    async def _on_data_load(self, _: object) -> None:
        await self._on_data_received(self._reader.result.encode())

    async def _on_error(self, _: object) -> None:
        alert("Failed to read file")


KeyReceiveCallback = Callable[[bytes], Awaitable[None]]


class Methods:
    def __init__(self, on_key_received: KeyReceiveCallback) -> None:
        self._on_key_received = on_key_received
        self._container = elem_by_id("method")
        self._register_selections()

    def _register_selections(self) -> None:
        self._container.innerHTML = ""

        methods: set[Method] = {PasswordMethod()}

        for method in methods:

            async def on_select(_: object, method: Method = method) -> None:
                self._container.innerHTML = method.html
                method.on_key_received = self._on_key_received
                await method.setup()

            btn = document.createElement("button")
            btn.className = "method"
            btn.innerText = method.name
            add_event_listener(btn, "click", on_select)
            self._container.appendChild(btn)


class Method:
    def __init__(self, *, name: str, html: str) -> None:
        self.name = name
        self.html = html
        self.on_key_received: KeyReceiveCallback | None = None

    async def setup(self) -> None: ...


class PasswordMethod(Method):
    def __init__(self) -> None:
        super().__init__(
            name="Password",
            html='<input id="password-input" />',
        )

    async def setup(self) -> None:
        self._input = elem_by_id("password-input", InputElement)
        add_event_listener(self._input, "keydown", self._on_key_down)

    async def _on_key_down(self, event: Any) -> None:
        if self.on_key_received is not None and event.key == "Enter":
            await self.on_key_received(self._input.value.encode())
