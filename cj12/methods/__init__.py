from collections.abc import Awaitable, Callable

KeyReceiveCallback = Callable[[bytes | None], Awaitable[None]]
