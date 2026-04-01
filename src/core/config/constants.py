from enum import Enum


ENV_FILE = (".env.prod", ".env")


class Environment(Enum):
    DEV = "DEV"
    PROD = "PROD"
