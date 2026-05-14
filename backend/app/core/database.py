from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

# env 연결
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL") #가져오기
engine = create_engine(DATABASE_URL) #db에 연결

#세션 열기
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#https://velog.io/@bongbong/sqlalchemy-orm-model
class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()