from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Word(Base):
    text: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    translation: Mapped[str] = mapped_column(String(128), nullable=False)
    examples: Mapped[list[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
