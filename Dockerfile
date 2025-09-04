FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /chat

WORKDIR /chat

RUN uv sync --locked

EXPOSE 8000

CMD ["uv", "run", "main.py"]