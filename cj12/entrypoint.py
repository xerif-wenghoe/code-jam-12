import logging

from js import document
from pyodide.http import pyfetch


async def start() -> None:
    logging.basicConfig(level=logging.INFO)

    document.title = "Code Jam 12"

    resp = await pyfetch("/ui.html")
    html = await resp.text()
    document.body.innerHTML = html
