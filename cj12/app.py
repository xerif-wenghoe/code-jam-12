from contextlib import suppress
from hashlib import sha256

from js import URL, Blob, alert, document
from pyodide.ffi import to_js

from cj12.aes import decrypt, encrypt
from cj12.container import Container, InvalidMagicError
from cj12.dom import (
    ButtonElement,
    add_event_listener,
    elem_by_id,
    fetch_text,
)
from cj12.file import FileInput
from cj12.methods.methods import Methods, methods


class App:
    async def start(self) -> None:
        document.title = "Super Duper Encryption Tool"
        document.body.innerHTML = await fetch_text("/ui.html")

        self._data: bytes | None = None
        self._key: bytes | None = None
        self._container: Container | None = None

        self._file_input = FileInput(self._on_data_received)
        self._filename = ""

        self._encrypt_button = elem_by_id("encrypt-button", ButtonElement)
        self._decrypt_button = elem_by_id("decrypt-button", ButtonElement)
        add_event_listener(self._encrypt_button, "click", self._on_encrypt_button)
        add_event_listener(self._decrypt_button, "click", self._on_decrypt_button)

        self._methods = Methods(self._on_key_received)
        await self._methods.register_selections()

    async def _on_data_received(self, data: bytes, filename: str) -> None:
        self._data = data
        self._filename = filename

        with suppress(InvalidMagicError):
            self._container = Container.from_bytes(data)

        if self._container is not None:
            for method in methods:
                if method.byte == self._container.method:
                    await self._methods.go_to(method)

        self._update_button_availability()

    async def _on_key_received(self, key: bytes | None) -> None:
        self._key = key
        self._update_button_availability()

    def _update_button_availability(self) -> None:
        disabled = self._data is None or self._key is None
        self._encrypt_button.disabled = disabled
        self._decrypt_button.disabled = disabled

        if self._container is None:
            self._decrypt_button.disabled = True

    async def _on_encrypt_button(self, _: object) -> None:
        if self._methods.current is None:
            return

        data, key = self._ensure_data_and_key()

        container = Container(
            method=self._methods.current.byte,
            original_filename=self._filename,
            data_hash=sha256(data).digest(),
            data=encrypt(data, sha256(key).digest()),
        )

        self._download_file(bytes(container), "encrypted_file.bin")

    async def _on_decrypt_button(self, _: object) -> None:
        if self._container is None:
            return

        _, key = self._ensure_data_and_key()

        decrypted = decrypt(self._container.data, sha256(key).digest())
        decrypted_hash = sha256(decrypted).digest()

        if decrypted_hash != self._container.data_hash:
            alert("Incorrect key")
            return

        self._download_file(decrypted, self._container.original_filename)

    def _download_file(self, data: bytes, filename: str) -> None:
        u8 = to_js(data, create_pyproxies=False)
        blob = Blob.new([u8], {"type": "application/octet-stream"})
        url = URL.createObjectURL(blob)
        a = document.createElement("a")
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)

    def _ensure_data_and_key(self) -> tuple[bytes, bytes]:
        if self._data is None or self._key is None:
            msg = "Data or key not set"
            raise ValueError(msg)

        return (self._data, self._key)
