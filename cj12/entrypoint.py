from js import document
from pyodide.http import pyfetch


async def start() -> None:
    document.title = "Code Jam 12"

    resp = await pyfetch("/cj12/ui.html")
    html = await resp.text()
    document.body.innerHTML = html
