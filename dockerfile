FROM python:3.14-slim AS py-builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && \
  apt-get install -y --no-install-recommends gcc && \
  apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN uv export --no-dev --format requirements.txt --output-file ./requirements.txt

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r ./requirements.txt

FROM python:3.14-slim

LABEL org.opencontainers.image.source="https://github.com/builtbyrb/fastapi-template"

RUN addgroup --gid 1001 --system app && \
  adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=py-builder /app/wheels /wheels
COPY --from=py-builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .

RUN chown -R app:app /app
USER app

ENTRYPOINT ["uvicorn",  "src.app:app", "--host", "0.0.0.0", "--port", "8080", \
  "--loop", "uvloop", "--http", "httptools", \
  "--timeout-keep-alive", "5", \
  "--limit-concurrency", "1000", \
  "--backlog", "2048"]

HEALTHCHECK  --start-period=20s --interval=1m30s --timeout=30s --retries=5 CMD python3 -c  "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/', timeout=5)" || exit 1