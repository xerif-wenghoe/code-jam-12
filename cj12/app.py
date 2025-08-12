from abc import ABC, abstractmethod
from typing import final

from js import FileReader, document
from pyodide.ffi import create_proxy
from pyodide.http import pyfetch

from cj12.dom import ButtonElement, get_element_by_id


@final
class App:
    def __init__(self) -> None:
        self._data: bytes | None = None

    async def start(self) -> None:
        document.title = "Code Jam 12"
        document.body.innerHTML = await fetch_text("/ui.html")

        self._register_file_input_handler()

    def _register_file_input_handler(self) -> None:
        @create_proxy
        def on_input_element_change(event: object) -> None:
            reader = FileReader.new()
            reader.addEventListener("load", on_content_load)
            reader.readAsBinaryString(event.target.files.item(0))  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]

        @create_proxy
        def on_content_load(event: object) -> None:
            self._data = event.target.result.encode()  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            get_element_by_id("encrypt-button", ButtonElement).disabled = False
            get_element_by_id("decrypt-button", ButtonElement).disabled = False

        file_input = get_element_by_id("file-input")
        file_input.addEventListener("change", on_input_element_change)


class Method(ABC):
    @abstractmethod
    async def wait_for_encryption_key(self) -> bytes: ...
    @abstractmethod
    async def wait_for_decryption_key(self) -> bytes: ...


async def fetch_text(url: str) -> str:
    resp = await pyfetch(url)
    return await resp.text()
