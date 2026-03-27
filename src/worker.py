from uvicorn_worker import UvicornWorker


class ProductionWorker(UvicornWorker):
    CONFIG_KWARGS = {  # noqa: RUF012
        "loop": "uvloop",
        "http": "httptools",
        "limit-concurrency": 1000,
        "backlog": 2048,
    }
