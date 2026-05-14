from fastapi import FastAPI                             
from app.core.database import Base, engine              
from app.model import user, file                        # 유지
from app.routers import auth, files

#0
app = FastAPI()

#1
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(files.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}




