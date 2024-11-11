from sqlalchemy import Boolean, String, Integer, LargeBinary, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from enum import Enum as PEnum

from app.models.mixin import SharedMixin

class UserType(str, PEnum):
    ADMIN = "admin"
    USER = "user"


class User(Base,SharedMixin):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[LargeBinary] = mapped_column(LargeBinary)
    password_salt: Mapped[LargeBinary] = mapped_column(LargeBinary)
    is_super_admin: Mapped[bool] = mapped_column(Boolean)
    user_type = mapped_column(
        Enum(UserType), nullable=False, default=UserType.USER
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationship to ChatPDFConversion model
    chat_pdfs: Mapped["ChatPDFConversion"] = relationship(
        "ChatPDFConversion", back_populates="created_by", overlaps="created_by"
    )
