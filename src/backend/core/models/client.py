"""
Acceptance Criteria:
- Client has id (UUID PK), name (unique), slug (unique), status, created_at, updated_at.
- ClientUser has id (UUID PK), client_id (FK -> clients.id), user_id (UUID), role, created_at.
- ClientSetting has id (UUID PK), client_id (FK -> clients.id), key, value (text),
  created_at, updated_at.
- (client_id, key) is unique in client_settings.
- All timestamps default to now() in UTC.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    users: Mapped[list["ClientUser"]] = relationship(
        "ClientUser", back_populates="client", cascade="all, delete-orphan"
    )
    settings: Mapped[list["ClientSetting"]] = relationship(
        "ClientSetting", back_populates="client", cascade="all, delete-orphan"
    )
    pipelines: Mapped[list["Pipeline"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Pipeline", back_populates="client", cascade="all, delete-orphan"
    )


class ClientUser(Base):
    __tablename__ = "client_users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    client: Mapped["Client"] = relationship("Client", back_populates="users")


class ClientSetting(Base):
    __tablename__ = "client_settings"
    __table_args__ = (UniqueConstraint("client_id", "key", name="uq_client_settings_client_key"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), nullable=False
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    client: Mapped["Client"] = relationship("Client", back_populates="settings")
