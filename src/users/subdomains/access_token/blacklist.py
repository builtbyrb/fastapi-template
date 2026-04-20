import uuid


def append_prefix(access_token_jti: uuid.UUID, prefix: str) -> str:
    return f"{prefix}:{access_token_jti}"
