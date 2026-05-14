from sqlalchemy import Column, String, DateTime
from app.core.database import Base

#https://devspoon.tistory.com/326 :: 1번 방식
class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    user_pw = Column(String)


