from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from core.models import Base


class EmailVerificationCode(Base):
    email: Mapped[str] = mapped_column(index=True)
    code: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at
