from js import document

from cj12.dom import add_event_listener, elem_by_id, fetch_text
from cj12.methods import KeyReceiveCallback
from cj12.methods.chess import ChessMethod
from cj12.methods.safe import SafeMethod
from cj12.methods.location import LocationMethod
from cj12.methods.method import Method
from cj12.methods.password import PasswordMethod

methods: list[Method] = [PasswordMethod(), LocationMethod(), ChessMethod(), SafeMethod()]


class Methods:
    def __init__(self, on_key_received: KeyReceiveCallback) -> None:
        self._on_key_received = on_key_received
        self._container = elem_by_id("method")
        self._html_cache: dict[str, str] = {}

    async def _get_cached_html(self, method: Method) -> str:
        if method.static_id not in self._html_cache:
            url = f"/methods/{method.static_id}/page.html"
            self._html_cache[method.static_id] = await fetch_text(url)
        return self._html_cache[method.static_id]

    async def register_selections(self) -> None:
        self._container.innerHTML = ""

        for method in methods:

            async def on_back(_: object) -> None:
                await self._on_key_received(None)
                await self.register_selections()

            async def on_select(_: object, method: Method = method) -> None:
                self._container.innerHTML = f"""
                    <button id="back">Back to selections</button>
                    {await self._get_cached_html(method)}
                """
                method.on_key_received = self._on_key_received
                add_event_listener(elem_by_id("back"), "click", on_back)
                await method.setup()

            btn = document.createElement("button")
            btn.className = "method-selection"
            btn.innerHTML = f"""
                <img src="/methods/{method.static_id}/img.png" />
                <h3>{method.name}</h3>
                <p>{method.description}</p>
            """
            add_event_listener(btn, "click", on_select)
            self._container.appendChild(btn)
