from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
