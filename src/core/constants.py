from enum import StrEnum


ENV_FILE = (".env.prod", ".env.stag", ".env")


class Environment(StrEnum):
    DEV = "DEV"
    PROD = "PROD"
    STAG = "STAG"
