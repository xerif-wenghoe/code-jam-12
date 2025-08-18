FROM python:3.13-alpine AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY ./pyproject.toml .
COPY ./uv.lock .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN --mount=type=ssh uv sync --frozen --no-cache

FROM python:3.13-alpine

WORKDIR /app

COPY --from=builder /app /app

COPY ./server.py /app
COPY ./cj12 /app/cj12
COPY ./static /app/static
COPY ./typings /app/typings

ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "server.py"]
