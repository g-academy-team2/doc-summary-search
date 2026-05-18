from passlib.context import CryptContext    #0
from sqlalchemy.orm import Session          #1
from app.model.user import User             #1
from fastapi import HTTPException  #1
from jose import jwt            #2
from datetime import datetime, timedelta    #2
import os                                   #2
from fastapi import Request

#0 #https://zambbon.tistory.com/52
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def get_password_hash(password):
    return bcrypt_context.hash(password)

# 1
def register(db: Session, user_id: str, user_pw: str):
    existing_user = db.query(User).filter(User.user_id == user_id).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    
    hash_password = get_password_hash(user_pw)
    
    new_user = User(user_id=user_id, user_pw=hash_password)
    db.add(new_user)
    db.commit()

    return new_user

#2 :: https://zambbon.tistory.com/55 :: JWT 토큰
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(user_id: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": user_id, "exp": expire}
    return jwt.encode(data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

#3 :: https://zambbon.tistory.com/55 :: 로그인 + 토큰 발급
def login(db: Session, user_id: str, user_pw: str):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="아이디가 존재하지 않습니다.")
    
    if not bcrypt_context.verify(user_pw, user.user_pw):
        raise HTTPException(status_code=400, detail="비밀번호가 틀렸습니다.")
    
    token = create_access_token(user_id)

    return token


#4 :: @router.post("/doc") upload에서 요청한 토큰에서 id 분리 작업 후 반환
def get_user_id_from_token(request: Request) -> str:
    token = request.headers.get("Authorization").split(" ")[1]
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return payload.get("sub")

