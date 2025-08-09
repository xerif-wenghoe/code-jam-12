from typing import final

from cj12.rpg.terminal import Terminal


@final
class RPG:
    def __init__(self) -> None:
        self._terminal = Terminal()

    async def start(self) -> None:
        self._terminal.print("Hello, world!")
        self._terminal.print("This is an RPG.")
        while True:
            msg = await self._terminal.wait_for_command()
            self._terminal.print(f"You entered: {msg}")
