from fastapi import FastAPI                             
from app.core.database import Base, engine              
from app.model import user, file                        # 유지
from app.api import auth, files                     #0             #1                          #1
from pydantic import BaseModel                          #2
from sqlalchemy.orm import Session                      #3
from fastapi import Depends                             #3
from app.services import auth_service                   #3
from app.core.database import get_db                    #3
from fastapi.security import OAuth2PasswordRequestForm  #4
from app.api import ocr

#0
app = FastAPI(title="문서 요약 및 검색 서비스 API")

#1
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(files.router)

@app.get("/")
async def root():
    return {"message": "서버가 정상 가동 중입니다. /docs 에서 테스트해 보세요!"}



