import logging
from abc import ABC, abstractmethod
from typing import final

from js import URL, Blob, FileReader, Uint8Array, alert, document
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch

from cj12.aes import decrypt, encrypt, ensure_length
from cj12.dom import ButtonElement, get_element_by_id
from cj12.html import DOWNLOAD_SECTION, FILE_AREA

logger = logging.getLogger(__name__)


@final
class App:
    def __init__(self) -> None:
        self._data: bytes | None = None
        self._processed_data: bytes | None = None
        self._current_filename: str = ""

    async def start(self) -> None:
        document.title = "Code Jam 12"
        document.body.innerHTML = await fetch_text("/ui.html")

        self._register_file_input_handler()

    def _register_file_input_handler(self) -> None:
        @create_proxy
        def on_input_element_change(event: object) -> None:
            file = event.target.files.item(0)
            self._current_filename = file.name
            document.getElementById("file-area").innerHTML = FILE_AREA.format(
                file_name=file.name,
                file_size=round(file.size / 1024, 2),
            )
            reader = FileReader.new()
            reader.addEventListener("load", on_content_load)
            reader.readAsArrayBuffer(file)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]

        @create_proxy
        def on_content_load(event: object) -> None:
            # Convert ArrayBuffer to bytes using Uint8Array
            array_buffer = event.target.result  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            uint8_array = Uint8Array.new(array_buffer)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            self._data = bytes(uint8_array)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            get_element_by_id("encrypt-button", ButtonElement).disabled = False
            get_element_by_id("decrypt-button", ButtonElement).disabled = False

            # Register button handlers after they're enabled
            self._register_encrypt_handler()
            self._register_decrypt_handler()

        file_input = get_element_by_id("file-input")
        file_input.addEventListener("change", on_input_element_change)

    def _register_encrypt_handler(self) -> None:
        @create_proxy
        def on_encrypt_click(_: object) -> None:
            self._handle_encryption()

        encrypt_button = get_element_by_id("encrypt-button", ButtonElement)
        encrypt_button.addEventListener("click", on_encrypt_click)

    def _register_decrypt_handler(self) -> None:
        @create_proxy
        def on_decrypt_click(_: object) -> None:
            self._handle_decryption()

        decrypt_button = get_element_by_id("decrypt-button", ButtonElement)
        decrypt_button.addEventListener("click", on_decrypt_click)

    def _handle_encryption(self) -> None:
        if self._data is None:
            return

        # Get key from input field
        key_input = document.getElementById("key-input")
        if key_input is None:
            alert("Key input field not found")
            return

        key_value = key_input.value
        if not key_value or key_value.strip() == "":
            alert("Please enter an encryption key")
            return

        try:
            # Convert key to bytes (pad or truncate to 16, 24, or 32 bytes for AES)
            key = ensure_length(key_value.encode("utf-8"))

            # Encrypt the data
            self._processed_data = encrypt(self._data, key)
            self._show_download_button("encrypted")

        except Exception as e:
            logger.exception("Encryption failed")
            alert(f"Encryption failed: {e!s}")

    def _handle_decryption(self) -> None:
        if self._data is None:
            return

        # Get key from input field
        key_input = document.getElementById("key-input")
        if key_input is None:
            alert("Key input field not found")
            return

        key_value = key_input.value
        if not key_value or key_value.strip() == "":
            alert("Please enter a decryption key")
            return

        try:
            # Convert key to bytes (pad or truncate to 16, 24, or 32 bytes for AES)
            key = ensure_length(key_value.encode("utf-8"))

            # Decrypt the data
            self._processed_data = decrypt(self._data, key)
            self._show_download_button("decrypted")

        except Exception as e:
            logger.exception("Decryption failed")
            alert(f"Decryption failed: {e!s}")

    def _show_download_button(self, operation: str) -> None:
        # Remove existing download section if any
        existing_download = document.getElementById("download-section")
        if existing_download:
            existing_download.remove()

        # Create download section
        download_section = document.createElement("section")
        download_section.id = "download-section"

        # Determine filename with appropriate extension
        base_name = (
            self._current_filename.rsplit(".", 1)[0]
            if "." in self._current_filename
            else self._current_filename
        )
        original_ext = (
            self._current_filename.rsplit(".", 1)[1]
            if "." in self._current_filename
            else ""
        )

        if operation == "encrypted":
            download_filename = f"{base_name}_encrypted.bin"
        # For decryption, try to restore original extension if possible
        elif original_ext and original_ext.lower() not in ["bin", "enc", "encrypted"]:
            download_filename = f"{base_name}_decrypted.{original_ext}"
        else:
            download_filename = f"{base_name}_decrypted.bin"

        download_section.innerHTML = DOWNLOAD_SECTION.format(
            operation=operation,
            file_size=len(self._processed_data) if self._processed_data else 0,
            title=operation.title(),
        )

        # Insert after file display
        file_display = document.getElementById("file-display")
        file_display.parentNode.insertBefore(download_section, file_display.nextSibling)

        # Register download button handler
        @create_proxy
        def on_download_click(_: object) -> None:
            self._download_file(download_filename)

        download_button = get_element_by_id("download-button", ButtonElement)
        download_button.addEventListener("click", on_download_click)

    def _download_file(self, filename: str) -> None:
        if self._processed_data is None:
            return

        uint8_array = Uint8Array.new(len(self._processed_data))
        uint8_array.set(self._processed_data)
        # Create blob from processed data
        blob = Blob.new([uint8_array], {"type": "application/octet-stream"})

        # Create download link
        url = URL.createObjectURL(blob)

        # Create temporary anchor element for download
        download_link = document.createElement("a")
        download_link.href = url
        download_link.download = filename
        download_link.style.display = "none"

        # Add to document, click, and cleanup
        document.body.appendChild(download_link)
        download_link.click()
        document.body.removeChild(download_link)

        # Clean up the URL object
        URL.revokeObjectURL(url)


class Method(ABC):
    @abstractmethod
    async def wait_for_encryption_key(self) -> bytes: ...
    @abstractmethod
    async def wait_for_decryption_key(self) -> bytes: ...


async def fetch_text(url: str) -> str:
    resp = await pyfetch(url)
    return await resp.text()
