from js import document


async def start() -> None:
    document.title = "Code Jam 12"
    document.body.innerHTML = "<p>Hello, world!</p>"
