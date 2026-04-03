from enum import StrEnum


ENV_FILE = (".env.prod", ".env")


class Environment(StrEnum):
    DEV = "DEV"
    PROD = "PROD"
