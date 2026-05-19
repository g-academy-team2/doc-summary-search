from fastapi import APIRouter, Depends, UploadFile, Request
from app.services import file_service, auth_service
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/file", tags=["upload"])

# 사용자가 올린 파일 받기
@router.post("/doc")
async def upload( #async 추가된 이유 : 파일 업로드 느려서 다른 처리도 동시에 하기 위해
    request: Request, # 헤더 토큰에서 id값 빼기 위함
    file: UploadFile,
    db: Session = Depends(get_db)
):
    user_id = auth_service.get_user_id_from_token(request) #id 빼기
    return await file_service.upload_file(db, file, user_id) #필요한 곳에 반환

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