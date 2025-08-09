from asyncio import Event
from typing import final

from js import document
from pyodide.ffi import create_proxy


@final
class Terminal:
    def __init__(self) -> None:
        document.body.innerHTML = """
        <main class="terminal">
            <ul class="terminal_lines"></ul>
            <input class="terminal_input" placeholder="Enter a command"></input>
        </main>

        <style>
            .terminal {
                width: 100%;
                height: 100vh;
                padding: 1rem;
                background-color: black;
                color: #00ff00;
                font-family: "JetBrains Mono", monospace;
                font-weight: 400;
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }

            .terminal_lines {
                padding: 1rem;
                border: 2px solid #00ff00;
                list-style-type: none;
                flex: 1;
            }

            .terminal_input {
                padding: 1rem;
                border: 2px solid #00ff00;
                background-color: transparent;
                outline: none;
            }
        </style>
        """

        self._lines_element = document.body.querySelector(".terminal_lines")
        self._input_element = document.body.querySelector(".terminal_input")

    def print(self, s: str) -> None:
        self._lines_element.innerHTML += f"<li>{s}</li>"

    async def wait_for_command(self) -> str:
        event = Event()
        command = ""

        @create_proxy
        def handle_keydown(e) -> None:  # noqa: ANN001
            nonlocal command
            if e.key == "Enter":
                command = self._input_element.value
                self._input_element.value = ""
                event.set()

        self._input_element.addEventListener("keydown", handle_keydown)
        self._input_element.focus()

        await event.wait()

        self._input_element.removeEventListener("keydown", handle_keydown)
        return command
