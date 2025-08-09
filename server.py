import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles


async def serve_index(_: Request) -> FileResponse:
    return FileResponse("cj12/index.html")


app = Starlette(
    routes=[
        Route("/", serve_index),
        Mount("/cj12", StaticFiles(directory="cj12")),
    ],
)

if __name__ == "__main__":
    uvicorn.run(app)
