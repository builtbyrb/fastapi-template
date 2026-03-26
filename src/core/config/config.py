from pydantic import BaseModel

from src.core.config.env import APP_ENV, AppEnv
from src.core.config.rules import APP_VALIDATION_RULES, AppValidationRules


class AppConfig(BaseModel):
    env: AppEnv = APP_ENV
    validations_rules: AppValidationRules = APP_VALIDATION_RULES


APP_CONFIG = AppConfig()
