import os

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

app = Starlette(
    routes=[
        Mount("/cj12", StaticFiles(directory="cj12")),
        Mount("/", StaticFiles(directory="static", html=True)),
    ],
)

if __name__ == "__main__":
    host: str = os.getenv("CJ12_HOST", "0.0.0.0")  # noqa: S104
    port: int = os.getenv("CJ12_PORT", "8000")
    uvicorn.run(app, host=host, port=int(port))
