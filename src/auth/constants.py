from src.auth.security import password_hash


DUMMY_HASH = password_hash.hash("dummyPassword")
