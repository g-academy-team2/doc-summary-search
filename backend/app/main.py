from fastapi import FastAPI
# 김주한의 api
from backend.app.api import ocr

app = FastAPI(title="문서 요약 및 검색 서비스 API")

# 김주한의 router
app.include_router(ocr.router)

@app.get("/")
async def root():
    return {"message": "서버가 정상 가동 중입니다. /docs 에서 테스트해 보세요!"}