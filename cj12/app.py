from hashlib import sha256

from js import URL, Blob, alert, document
from pyodide.ffi import to_js

from cj12.aes import decrypt, encrypt
from cj12.dom import (
    ButtonElement,
    add_event_listener,
    elem_by_id,
    fetch_text,
)
from cj12.file import FileInput
from cj12.methods.methods import Methods


class App:
    async def start(self) -> None:
        document.title = "Super Duper Encryption Tool"
        document.body.innerHTML = await fetch_text("/ui.html")

        self._data: bytes | None = None
        self._key: bytes | None = None

        self._file_input = FileInput(self._on_data_received)

        self._encrypt_button = elem_by_id("encrypt-button", ButtonElement)
        self._decrypt_button = elem_by_id("decrypt-button", ButtonElement)
        add_event_listener(self._encrypt_button, "click", self._on_encrypt_button)
        add_event_listener(self._decrypt_button, "click", self._on_decrypt_button)

        self._methods = Methods(self._on_key_received)
        await self._methods.register_selections()

    async def _on_data_received(self, data: bytes) -> None:
        self._data = data
        self._update_button_availability()

    async def _on_key_received(self, key: bytes | None) -> None:
        self._key = key
        self._update_button_availability()

    def _update_button_availability(self) -> None:
        disabled = self._data is None or self._key is None
        self._encrypt_button.disabled = disabled
        self._decrypt_button.disabled = disabled

        if self._data is not None and len(self._data) % 16 != 0:
            # Encrypted data must be a multiple of 16 bytes
            # If it isn't, then it can't be an encrypted file, so disable decryption
            self._decrypt_button.disabled = True

    async def _on_encrypt_button(self, _: object) -> None:
        data, key = self._ensure_data_and_key()
        encrypted_data = encrypt(data, sha256(key).digest())
        self._download_file(encrypted_data, "encrypted_file.bin")

    async def _on_decrypt_button(self, _: object) -> None:
        data, key = self._ensure_data_and_key()
        try:
            decrypted_data = decrypt(data, sha256(key).digest())
            self._download_file(decrypted_data, "decrypted_file.bin")
        except Exception as e:  # noqa: BLE001
            print(e)  # noqa: T201
            alert("Wrong key!")

    def _download_file(self, data: bytes, filename: str) -> None:
        u8 = to_js(data, create_pyproxies=False)
        blob = Blob.new([u8], {"type": "application/octet-stream"})
        url = URL.createObjectURL(blob)
        a = document.createElement("a")
        a.href = url  # pyright: ignore[reportAttributeAccessIssue]
        a.download = filename  # pyright: ignore[reportAttributeAccessIssue]
        document.body.appendChild(a)
        a.click()  # pyright: ignore[reportAttributeAccessIssue]
        document.body.removeChild(a)
        URL.revokeObjectURL(url)

    def _ensure_data_and_key(self) -> tuple[bytes, bytes]:
        if self._data is None or self._key is None:
            msg = "Data or key not set"
            raise ValueError(msg)

        return (self._data, self._key)
