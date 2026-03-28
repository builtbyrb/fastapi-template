from enum import Enum


class Environment(Enum):
    DEV = "DEV"
    PROD = "PROD"


ENV_FILE = (".env.prod", ".env")
