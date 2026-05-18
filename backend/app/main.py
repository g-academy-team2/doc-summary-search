from fastapi import FastAPI, Request    
from fastapi.responses import JSONResponse                    
from app.core.database import Base, engine              
from app.model import user, file                        # 유지
from app.api import auth, files   
from jose import jwt, JWTError       
import os
from dotenv import load_dotenv      

app = FastAPI(title="문서 요약 및 검색 서비스 API")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(files.router)

load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
PUBLIC_PATHS = ["/user/join", "/user/login", "/", "/docs", "/openapi.json"]

# 토큰(로그인 상태) 검증용
@app.middleware("http") #HTTP 요청이 들어올 때마다 API 실행 전에 먼저 실행됨.
async def auth_middleware(request: Request, call_next): # 요청 정보, 다음 단계(api 경로)
    if request.url.path in PUBLIC_PATHS: #검증이 필요없는 경로면 넘김
        return await call_next(request)
    
    token = request.headers.get("Authorization") # 요청 헤더에서 토큰 빼기
    if not token or not token.startswith("Bearer "): # 토큰이 없거나 이상한 형태?
        return JSONResponse(status_code=401, content={"detail": "인증 실패"})
    
    try:
        token = token.split(" ")[1]  # 앞부분 자르고 토큰값만 빼고 유효 토큰 검증
        jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return JSONResponse(status_code=401, content={"detail": "토큰이 유효하지 않습니다."})
    
    return await call_next(request)

@app.get("/")
async def root():
    return {"message": "서버가 정상 가동 중입니다. /docs 에서 테스트해 보세요!"}



