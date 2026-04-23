FROM python:3.13-slim AS py-builder

ARG ENVIRONMENT

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && \
  apt-get install -y --no-install-recommends gcc && \
  apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN uv export --no-dev --format requirements.txt --output-file ./requirements.txt

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r ./requirements.txt

FROM python:3.13-slim

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
RUN chmod +x /app/entrypoint.sh
USER app

ENTRYPOINT ["/app/entrypoint.sh"]