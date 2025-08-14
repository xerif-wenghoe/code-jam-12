from typing import cast

from js import document
from pyodide.ffi import JsDomElement, JsNull


class ButtonElement(JsDomElement):
    disabled: bool  # pyright: ignore[reportUninitializedInstanceVariable]


def get_element_by_id[T](elem_id: str, _: type[T] = JsDomElement) -> T:
    """
    Get an element by its ID.

    Usage:

    - `get_element_by_id("my-element")`: Return the element of ID `my-element` and raise
        a TypeError if it cannot be found.

    - `get_element_by_id("my-button", ButtonElement)`: Same as before, but return an
        element of type `ButtonElement`.
    """

    elem = document.getElementById(elem_id)

    if isinstance(elem, JsNull):
        msg = f"Element with ID {elem_id} not found"
        raise TypeError(msg)

    return cast("T", elem)
