from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum, Text
from app.core.database import Base
import enum
from ulid import ULID

class FileStatus(enum.Enum):
    UPLOADING = "UPLOADING"
    SUMMARIZING = "SUMMARIZING"
    DONE = "DONE"
    FAILED = "FAILED"

class FileCategory(enum.Enum):
    Unknown = "Unknown"
    IT = "IT"
    law = "law"
    bill = "bill"
    education = "education"

class File(Base):
    __tablename__ = "files"
    file_id = Column(String, primary_key=True, default=lambda: str(ULID()))
    user_id = Column(String, ForeignKey("users.user_id"))
    file_name = Column(String, index=True)
    extension = Column(String)
    status = Column(Enum(FileStatus), default=FileStatus.UPLOADING)
    sha256_hash = Column(String)  # 추가
    summary = Column(Text)
    summary_day = Column(DateTime)
    category = Column(Enum(FileCategory))