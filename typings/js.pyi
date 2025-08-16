# This comes from https://github.com/pyodide/pyodide/blob/main/src/py/js.pyi
# with some minor modifications

# ruff: noqa: N802, A002, N803, N815, N801
# pyright: reportAny=false, reportExplicitAny=false

from collections.abc import Callable, Iterable
from typing import Any, Literal, overload, override

from _pyodide._core_docs import _JsProxyMetaClass  # pyright: ignore[reportPrivateUsage]
from pyodide.ffi import (
    JsArray,
    JsDomElement,
    JsException,
    JsFetchResponse,
    JsNull,
    JsProxy,
    JsTypedArray,
)
from pyodide.webloop import PyodideFuture

def alert(msg: str) -> None: ...
def eval(code: str) -> Any: ...  # noqa: A001

# in browser the cancellation token is an int, in node it's a special opaque
# object.
type _CancellationToken = int | JsProxy

def setTimeout(cb: Callable[[], Any], timeout: float) -> _CancellationToken: ...
def clearTimeout(id: _CancellationToken) -> None: ...
def setInterval(cb: Callable[[], Any], interval: float) -> _CancellationToken: ...
def clearInterval(id: _CancellationToken) -> None: ...
def fetch(
    url: str,
    options: JsProxy | None = None,
) -> PyodideFuture[JsFetchResponse]: ...

self: Any = ...
window: Any = ...

# Shenanigans to convince skeptical type system to behave correctly:
#
# These classes we are declaring are actually JavaScript objects, so the class
# objects themselves need to be instances of JsProxy. So their type needs to
# subclass JsProxy. We do this with a custom metaclass.

class _JsMeta(_JsProxyMetaClass, JsProxy): ...
class _JsObject(metaclass=_JsMeta): ...

class XMLHttpRequest(_JsObject):
    response: str

    @staticmethod
    def new() -> XMLHttpRequest: ...
    def open(self, method: str, url: str, sync: bool) -> None: ...
    def send(self, body: JsProxy | None = None) -> None: ...

class Object(_JsObject):
    @staticmethod
    def fromEntries(it: Iterable[JsArray[Any]]) -> JsProxy: ...

class Array(_JsObject):
    @staticmethod
    def new() -> JsArray[Any]: ...

class ImageData(_JsObject):
    @staticmethod
    def new(width: int, height: int, settings: JsProxy | None = None) -> ImageData: ...

    width: int
    height: int

class _TypedArray(_JsObject):
    @staticmethod
    def new(
        a: int | Iterable[int | float] | JsProxy | None,
        byteOffset: int = 0,
        length: int = 0,
    ) -> JsTypedArray: ...

class Uint8Array(_TypedArray):
    BYTES_PER_ELEMENT: int = 1

class Float64Array(_TypedArray):
    BYTES_PER_ELEMENT: int = 8

class JSON(_JsObject):
    @staticmethod
    def stringify(a: JsProxy) -> str: ...
    @staticmethod
    def parse(a: str) -> JsProxy: ...

class _DomElement(JsDomElement):
    innerHTML: str
    innerText: str
    className: str

class document(_JsObject):
    title: str
    body: _DomElement
    children: list[_DomElement]
    @overload
    @staticmethod
    def createElement(tagName: Literal["canvas"]) -> JsCanvasElement: ...
    @overload
    @staticmethod
    def createElement(tagName: str) -> _DomElement: ...
    @staticmethod
    def appendChild(child: _DomElement) -> None: ...
    @staticmethod
    def getElementById(id: str) -> _DomElement | JsNull: ...

class JsCanvasElement(_DomElement):
    width: int | float
    height: int | float
    def getContext(
        self,
        ctxType: str,
        *,
        powerPreference: str = "",
        premultipliedAlpha: bool = False,
        antialias: bool = False,
        alpha: bool = False,
        depth: bool = False,
        stencil: bool = False,
    ) -> Any: ...

class ArrayBuffer(_JsObject):
    @staticmethod
    def isView(x: Any) -> bool: ...

class DOMException(JsException): ...

class Map:
    @staticmethod
    def new(a: Iterable[Any]) -> Map: ...

async def sleep(ms: float) -> None: ...

class AbortSignal(_JsObject):
    @staticmethod
    def any(iterable: Iterable[AbortSignal]) -> AbortSignal: ...
    @staticmethod
    def timeout(ms: int) -> AbortSignal: ...
    aborted: bool
    reason: JsException
    def throwIfAborted(self) -> None: ...
    def onabort(self) -> None: ...

class AbortController(_JsObject):
    @staticmethod
    def new() -> AbortController: ...
    signal: AbortSignal
    def abort(self, reason: JsException | None = None) -> None: ...

class Response(_JsObject):
    @staticmethod
    def new(body: Any) -> Response: ...

class Promise(_JsObject):
    @staticmethod
    def resolve(value: Any) -> Promise: ...

class FileReader(_DomElement):
    result: str

    @override
    @staticmethod
    def new() -> FileReader: ...
    def readAsBinaryString(self, file: object) -> None: ...
