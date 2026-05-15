from fastapi import APIRouter, File, HTTPException
from fastapi import UploadFile as UF  
from typing import Annotated
from pydantic import WithJsonSchema       
import os
import shutil

from app.ocr.parsers.multi_parser import total_parser

UploadFile = Annotated[UF, WithJsonSchema({"type": "string", "format": "binary"})]

router = APIRouter(prefix="/ocr", tags=["문서 분석 (OCR)"])

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(description="업로드할 문서 파일들")):
    results = []
    
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            extracted_text = total_parser(file_path)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "text_preview": extracted_text[:1000]
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
        finally:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except PermissionError:
                    print(f"⚠️ [경고] 파일을 삭제할 수 없습니다 (사용 중): {file.filename}")
                except Exception as e:
                    print(f"⚠️ [경고] 파일 삭제 중 알 수 없는 오류 발생: {e}")
                
    return {"count": len(files), "results": results}