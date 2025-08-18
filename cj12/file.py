from collections.abc import Awaitable, Callable
from typing import Any

from js import FileReader, Uint8Array, alert

from cj12.dom import add_event_listener, elem_by_id

# async on_data_received(data, filename)
DataReceiveCallback = Callable[[bytes, str], Awaitable[None]]


class FileInput:
    def __init__(self, on_data_received: DataReceiveCallback) -> None:
        self._callback = on_data_received

        self._reader = FileReader.new()
        add_event_listener(self._reader, "load", self._on_data_load)
        add_event_listener(self._reader, "error", self._on_error)
        add_event_listener(elem_by_id("file-input"), "change", self._on_file_change)

        self._filename = ""

    def _on_file_change(self, event: Any) -> None:
        file = event.target.files.item(0)
        self._filename = file.name
        elem_by_id("dropzone").innerText = f"{file.name} ({file.size / 1024:.2f} KB)"
        self._reader.readAsArrayBuffer(file)

    async def _on_data_load(self, _: object) -> None:
        await self._callback(
            bytes(Uint8Array.new(self._reader.result)),
            self._filename,
        )

    async def _on_error(self, _: object) -> None:
        alert("Failed to read file")
