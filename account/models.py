
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, String, DateTime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db_config.storage_config import Base, intpk, points


class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True, index=True
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    file: Mapped[str] = mapped_column(String, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    privileged: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    # ..
    created_at: Mapped[points]
    modified_at: Mapped[points]
    last_login_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # ...
    user_group: Mapped[list["GroupChat"]] = relationship(
        back_populates="group_admin",
        cascade="all, delete-orphan"
    )
    user_chat: Mapped[list["MessageGroup"]] = relationship(
        back_populates="chat_user",
        cascade="all, delete-orphan"
    )
    one_chat: Mapped[list["OneChat"]] = relationship(
        back_populates="chat_one",
    )
    user_one_one: Mapped[list["OneOneChat"]] = relationship(
        back_populates="one_one_user",
        cascade="all, delete-orphan"
    )
    user_participant: Mapped[list["PersonParticipant"]] = relationship(
        back_populates="participant_user",
        cascade="all, delete-orphan"
    )

    def __str__(self):
        return str(self.id)

    def get_display_name(self) -> str:
        return self.name or ""

    def get_id(self) -> int:
        assert self.id
        return self.id

    def get_hashed_password(self) -> str:
        return self.password or ""

    def get_scopes(self) -> list:
        return []
