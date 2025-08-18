from typing import Protocol

from js import document

from cj12.dom import add_event_listener, elem_by_id, fetch_text
from cj12.methods import KeyReceiveCallback
from cj12.methods.chess import ChessMethod
from cj12.methods.direction import DirectionLockMethod
from cj12.methods.location import LocationMethod
from cj12.methods.music import MusicMethod
from cj12.methods.password import PasswordMethod
from cj12.methods.pattern_lock import PatternLockMethod
from cj12.methods.safe import SafeMethod
from cj12.methods.colour_picker import ColourPickerMethod


class Method(Protocol):
    byte: int
    static_id: str
    name: str
    description: str

    on_key_received: KeyReceiveCallback | None = None

    async def setup(self) -> None: ...


methods: list[Method] = [
    PasswordMethod(),
    ChessMethod(),
    LocationMethod(),
    SafeMethod(),
    PatternLockMethod(),
    MusicMethod(),
    DirectionLockMethod(),,
    ColourPickerMethod()
]


class Methods:
    def __init__(self, on_key_received: KeyReceiveCallback) -> None:
        self._on_key_received = on_key_received
        self._container = elem_by_id("method")
        self._html_cache: dict[str, str] = {}
        self.current: Method | None = None

    async def _get_cached_html(self, method: Method) -> str:
        if method.static_id not in self._html_cache:
            url = f"/methods/{method.static_id}/page.html"
            self._html_cache[method.static_id] = await fetch_text(url)
        return self._html_cache[method.static_id]

    async def register_selections(self) -> None:
        self._container.innerHTML = '<div id="method-selections"></div>'
        selections_container = elem_by_id("method-selections")

        for method in methods:
            btn = document.createElement("button")
            btn.className = "method-selection"
            btn.innerHTML = f"""
                <img src="/methods/{method.static_id}/img.png" />
                <h3>{method.name}</h3>
                <p>{method.description}</p>
            """

            async def wrapper(_: object, method: Method = method) -> None:
                await self.go_to(method)

            add_event_listener(btn, "click", wrapper)
            selections_container.appendChild(btn)

    async def _on_back(self, _: object) -> None:
        await self._on_key_received(None)
        await self.register_selections()

    async def go_to(self, method: Method) -> None:
        self.current = method
        self._container.innerHTML = f"""
            <button id="back">Back to selections</button>
            {await self._get_cached_html(method)}
        """
        method.on_key_received = self._on_key_received
        add_event_listener(elem_by_id("back"), "click", self._on_back)
        await method.setup()
