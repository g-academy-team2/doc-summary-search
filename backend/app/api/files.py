from fastapi import APIRouter, Depends, UploadFile, Request
from app.services import file_service, auth_service
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/file", tags=["upload"])

# 사용자가 올린 파일 받기
@router.post("/doc")
async def upload(request: Request, file: UploadFile, force: bool = False, db: Session = Depends(get_db)):
    user_id = auth_service.get_user_id_from_token(request)
    return await file_service.upload_file(db, file, user_id, force)

# 요약 진행중 파일 리스트
@router.get("/doc/ongoing")
async def get_processing(request: Request, db: Session = Depends(get_db)):
    user_id = auth_service.get_user_id_from_token(request)
    return file_service.get_processing_files(db, user_id)

# 최근 요약 파일 리스트
@router.get("/doc/latest")
async def get_recent(request: Request, db: Session = Depends(get_db)):
    user_id = auth_service.get_user_id_from_token(request)
    return file_service.recent_loaded_file(db, user_id)

# 검색 파일 리스트
@router.get("/doc")
async def search(request: Request, file_name: str, db: Session = Depends(get_db)):
    user_id = auth_service.get_user_id_from_token(request)
    return file_service.search_file(db, user_id, file_name)

# 파일 삭제
@router.delete("/doc/{file_id}")
async def delete(request: Request, file_id: str, db: Session = Depends(get_db)):
    user_id = auth_service.get_user_id_from_token(request)
    return file_service.delete_file(db, user_id, file_id)