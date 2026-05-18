from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum, Text
from app.core.database import Base
import enum

class FileStatus(enum.Enum):
    UPLOADING = "업로드중"
    OCR_ING = "OCR 처리중"
    SUMMARIZING = "요약중"
    DONE = "완료"
    FAILED = "실패"

class Filecategory(enum.Enum):
    IT = "IT"
    law = "법률"
    bill = "법안"
    education = "교육"

class File(Base):
    __tablename__ = "files"
    user_id = Column(String, ForeignKey("users.user_id"))

    file_id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String, index=True)
    extension = Column(String)
    status = Column(Enum(FileStatus), default=FileStatus.UPLOADING)
    summary = Column(Text)
    summary_day = Column(DateTime)
    category = Column(Enum(Filecategory))
