from pydantic import BaseModel

from src.auth.config.env import AUTH_ENV, AuthConfigEnv
from src.auth.config.exceptions import AUTH_ERRORS, AuthConfigErrors


class AuthConfig(BaseModel):
    env: AuthConfigEnv = AUTH_ENV
    exceptions: AuthConfigErrors = AUTH_ERRORS


AUTH_CONFIG = AuthConfig()
