from fastapi import APIRouter, Depends, UploadFile
from app.services import file_service
from app.services.auth_service import get_current_user
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/user", tags=["auth"])

@router.post("/doc")
async def upload(
    file: UploadFile,
    current_user = Depends(get_current_user),  # 자동으로 토큰 검증
    db: Session = Depends(get_db)
):
    return await file_service.upload_file(db, file, current_user.user_id)