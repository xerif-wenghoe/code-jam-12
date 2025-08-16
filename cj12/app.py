from hashlib import sha256

from js import URL, Blob, Uint8Array, document

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
        encrypted_data = encrypt(data, sha256(key).digest())
        self._download_file(encrypted_data, "encrypted_file.bin")

    async def _on_decrypt_button(self, _: object) -> None:
        data, key = self._ensure_data_and_key()
        decrypted_data = decrypt(data, sha256(key).digest())
        self._download_file(decrypted_data, "decrypted_file.bin")

    def _download_file(self, data: bytes, filename: str) -> None:
        uint8_array = Uint8Array.new(len(data))
        uint8_array.set(data)  # pyright: ignore[reportAttributeAccessIssue]

        # Create blob from processed data
        blob = Blob.new([uint8_array], {"type": "application/octet-stream"})

        # Create download link
        url = URL.createObjectURL(blob)

        # Create temporary anchor element for download
        download_link = document.createElement("a")
        download_link.href = url  # pyright: ignore[reportAttributeAccessIssue]
        download_link.download = filename  # pyright: ignore[reportAttributeAccessIssue]
        download_link.style.display = "none"

        # Add to document, click, and cleanup
        document.body.appendChild(download_link)
        download_link.click()  # pyright: ignore[reportAttributeAccessIssue]
        document.body.removeChild(download_link)  # pyright: ignore[reportAttributeAccessIssue]

        # Clean up the URL object
        URL.revokeObjectURL(url)

    def _ensure_data_and_key(self) -> tuple[bytes, bytes]:
        if self._data is None or self._key is None:
            msg = "Data or key not set"
            raise ValueError(msg)

        return (self._data, self._key)
