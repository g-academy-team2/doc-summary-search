from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.model.file import File, FileStatus

ALLOWED_EXTENSIONS = ["pdf", "pptx", "docx", "hwp"]

#파일 업로드
async def upload_file(db: Session, file: UploadFile, user_id: str):
    ext = file.filename.split(".")[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식이에요.")

    new_file = File(
        user_id=user_id,
        file_name=file.filename,
        extension=ext,
        status=FileStatus.UPLOADING
    )
    
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    #여기에서 OCR쪽에 파일 넘기는 코드 작성
    #이후 status=FileStatus.UPLOADING 가 OCR_ING으로 변경되어야 함.

    return new_file

#요약 진행중
def get_processing_files(db: Session, user_id: str):
    return db.query(File).filter(
        File.user_id == user_id,
        File.status.in_([FileStatus.UPLOADING, FileStatus.OCR_ING, FileStatus.SUMMARIZING])
    ).all()

#최근 파일
def recent_loaded_file(db: Session, user_id: str):
    return db.query(File).filter(
        File.user_id == user_id,
        File.status.in_([FileStatus.DONE])
    ).order_by(File.summary_day.desc()).limit(5).all()

def search_file(db: Session, user_id: str, file_name: str):
    return db.query(File).filter(
        File.user_id == user_id,
        File.file_name.like(f"%{file_name}%"),
        File.status.in_([FileStatus.DONE])
    ).all()