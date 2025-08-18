from collections.abc import Awaitable, Callable
from typing import cast

from js import document
from pyodide.ffi import JsDomElement, JsNull, create_proxy
from pyodide.http import pyfetch


class DomElement(JsDomElement):
    innerHTML: str  # noqa: N815
    innerText: str  # noqa: N815
    className: str  # noqa: N815


class ButtonElement(DomElement):
    disabled: bool


class InputElement(DomElement):
    value: str


def elem_by_id[T](elem_id: str, _: type[T] = DomElement) -> T:
    """
    Get an element by its ID.

    Usage:

    - `elem_by_id("my-element")`: Return the element of ID `my-element` and raise
        a TypeError if it cannot be found.

    - `elem_by_id("my-button", ButtonElement)`: Same as before, but return an
        element of type `ButtonElement`.
    """

    elem = document.getElementById(elem_id)

    if isinstance(elem, JsNull):
        msg = f"Element with ID {elem_id} not found"
        raise TypeError(msg)

    return cast("T", elem)


def add_event_listener(
    elem: JsDomElement,
    event: str,
    listener: Callable[[object], Awaitable[None] | None],
) -> None:
    elem.addEventListener(event, create_proxy(listener))


async def fetch_text(url: str) -> str:
    resp = await pyfetch(url)
    return await resp.text()
