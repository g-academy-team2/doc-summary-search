from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.model.file import File, FileStatus

ALLOWED_EXTENSIONS = ["pdf", "pdf", "docx", "hwp"]

async def upload_file(db: Session, file: UploadFile, user_id: str):
    ext = file.filename.split(".")[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식이에요.")

    new_file = File(
        user_id=user_id,
        file_name=file.filename,
        extension=ext,
        status=FileStatus.PENDING
    )
    
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    #여기에서 OCR쪽에 파일 넘기는 코드 작성

    return new_file