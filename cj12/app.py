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
            
            file = event.target.files.item(0)
            document.getElementById("file-area").innerHTML = f'''
            <section id="file-display">
            <div class="inner-flex">
                <p>{file.name}</p>
                <p>{round(file.size/1024, 2)} KB</p>
            </div>
            <div class="inner-flex">
                <button id="encrypt-button" class="right" disabled>Encrypt</button>
                <button id="decrypt-button" class="right" disabled>Decrypt</button>
            </div>
            </section>
            '''

            reader = FileReader.new()
            reader.addEventListener("load", on_content_load)
            reader.readAsBinaryString(file)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]


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
