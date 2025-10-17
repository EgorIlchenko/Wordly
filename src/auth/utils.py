from passlib.context import CryptContext

from users.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(secret=password)


def validate_password(
    password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(secret=password, hash=hashed_password)


def check_active_user(
    user: User,
) -> bool:
    if user.is_active:
        return True
    return False
