from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from enum import Enum as PEnum
from app.models.mixin import SharedMixin
from app.models.user import UserType


class ChatPDFStatus(str, PEnum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ChatPDFConversion(Base, SharedMixin):
    __tablename__ = "chat_pdf_conversions"

    name_internal: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    pdf_filename: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[ChatPDFStatus] = mapped_column(
        Enum(ChatPDFStatus), nullable=False, default=ChatPDFStatus.PROCESSING
    )

    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_by_user_type: Mapped[UserType] = mapped_column(
        Enum(UserType), nullable=False
    )
    wasabi_key: Mapped[str] = mapped_column(String, nullable=False)
    zip_wasabi_key: Mapped[str | None] = mapped_column(String, nullable=True)


    # Relationship to User model
    # Rename the relationship to `created_by` and add `back_populates` and `overlaps`
    created_by: Mapped["User"] = relationship(
        "User", back_populates="chat_pdfs", overlaps="chat_pdfs"
    )


