from fastapi import FastAPI                             
from app.core.database import Base, engine              
from app.model import user, file                        
from app.api import auth, files                     
from pydantic import BaseModel                          
from sqlalchemy.orm import Session                      
from fastapi import Depends                             
from app.services import auth_service                   
from app.core.database import get_db                    
from fastapi.security import OAuth2PasswordRequestForm  

# 💡 내 코드 추가: ocr 창구 불러오기
from app.api import ocr 

app = FastAPI(title="문서 요약 및 검색 서비스 API")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(files.router)

# 💡 내 코드 추가: ocr 창구 등록하기
app.include_router(ocr.router)

@app.get("/")
async def root():
    return {"message": "서버가 정상 가동 중입니다. /docs 에서 테스트해 보세요!"}