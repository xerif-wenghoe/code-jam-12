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
    uvicorn.run(app)
