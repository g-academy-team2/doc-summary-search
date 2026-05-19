from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.model.file import File, FileStatus
import hashlib

ALLOWED_EXTENSIONS = ["pdf", "pptx", "docx", "hwp"]

async def upload_file(db: Session, file: UploadFile, user_id: str, force: bool = False):
    ext = file.filename.split(".")[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식이에요.")

    content = await file.read()
    sha256_hash = hashlib.sha256(content).hexdigest()

    # 중복 파일 체크
    existing_file = db.query(File).filter(
        File.user_id == user_id,
        File.sha256_hash == sha256_hash
    ).first()

    if existing_file and not force: # 중복 파일(해시 동일) + force가 false :: 이후 프론트가 '무시하고 재요약' 요청을 보낼 때 true로 보내면 다시 요약.
        raise HTTPException(
            status_code=409,
            detail={
                "message": "이미 요약한 파일입니다.",
                "file_id": existing_file.file_id,
                "file_name": existing_file.file_name
            }
        )

    new_file = File(
        user_id=user_id,
        file_name=file.filename,
        extension=ext,
        status=FileStatus.UPLOADING,
        sha256_hash=sha256_hash
    )
    
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    #OCR로 데이터 토스 예시 :: 해시 만들 때 파일을 한 번 다 읽어버려서, content를 전달하는게 나음. 
    # await ocr_service.extract(content, ext)

    new_file.status = FileStatus.SUMMARIZING
    db.commit()

    return new_file # 프론트가 이걸 받아서 업로드 완료 표시

# 요약 진행중
# def get_processing_files(db: Session, user_id: str):
#     return db.query(File).filter(
#         File.user_id == user_id,
#         File.status.in_([FileStatus.UPLOADING, FileStatus.SUMMARIZING])
#     ).all()

# 최근 파일
def recent_loaded_file(db: Session, user_id: str):
    return db.query(File).filter(
        File.user_id == user_id,
        File.status.in_([FileStatus.DONE])
    ).order_by(File.summary_day.desc()).limit(5).all()

# 파일 검색
def search_file(db: Session, user_id: str, file_name: str):
    return db.query(File).filter(
        File.user_id == user_id,
        File.file_name.like(f"%{file_name}%"),
        File.status.in_([FileStatus.DONE])
    ).all()

# 파일 삭제
def delete_file(db: Session, user_id: str, file_id: str):
    file = db.query(File).filter(
        File.user_id == user_id,
        File.file_id == file_id
    ).first()

    if not file:
        raise HTTPException(status_code=404, detail="파일이 없습니다.")

    db.delete(file)
    db.commit()
    return {"message": "삭제됐어요."}