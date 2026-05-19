from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import auth_service
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/user", tags=["auth"])

class RegisterRequest(BaseModel):
    user_id: str
    user_pw: str

@router.post("/join")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register(db=db, user_id=request.user_id, user_pw=request.user_pw)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    token = auth_service.login(db=db, user_id=form_data.username, user_pw=form_data.password)
    return {"access_token": token, "token_type": "bearer"}