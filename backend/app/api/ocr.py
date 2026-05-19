from fastapi import APIRouter, File, HTTPException, Path 
from fastapi import UploadFile as UF  
from typing import Annotated
from pydantic import WithJsonSchema       
import os
import shutil
import uuid
import logging

from app.ocr.parsers.multi_parser import total_parser
from app.ocr.db_helper import save_ocr_result, get_connection 

logger = logging.getLogger(__name__)

UploadFile = Annotated[UF, WithJsonSchema({"type": "string", "format": "binary"})]

router = APIRouter(prefix="/ocr", tags=["문서 분석 (OCR)"])

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(description="업로드할 문서 파일들")):
    results = []
    
    for file in files:
        # 1. 파일명 충돌 방지를 위한 안전한 고유 파일명(UUID) 생성
        ext = os.path.splitext(file.filename)[1].lower() # 확장자 추출 (예: .hwp)
        safe_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # 파일 임시 저장
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            # 2. 텍스트 추출 (Service) - 안전한 경로를 파서에 넘깁니다.
            extracted_text = total_parser(file_path)
            
            # 3. 추출 성공 시 DB에 저장 (Repository)
            doc_id = None
            if extracted_text and not extracted_text.startswith(("❌", "⚠️")):
                 # db_helper의 파라미터 규칙에 맞게 확장자에서 점(.)을 제거합니다 (예: hwp)
                 file_type = ext.replace('.', '')
                 
                 # DB 저장 함수 호출 (원본 파일명 사용)
                 # 현재 테스트 환경이므로 임시로 'testid'를 user_id로 사용합니다.
                 doc_id = save_ocr_result(
                     filename=file.filename, 
                     extension=file_type, 
                     content=extracted_text, 
                     user_id="testid"
                 )
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "doc_id": doc_id, # DB에 저장된 고유 번호도 응답에 포함해 줍니다.
                "text": extracted_text
            })
            
        except Exception as e:
            logger.error(f"❌ 문서 처리 중 오류 발생 ({file.filename}): {e}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })
            
        finally:
            # 4. 임시 파일 삭제 (정리)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except PermissionError:
                    logger.warning(f"⚠️ [경고] 파일을 삭제할 수 없습니다 (사용 중): {file.filename}")
                except Exception as e:
                    logger.warning(f"⚠️ [경고] 파일 삭제 중 알 수 없는 오류 발생: {e}")
                
    return {"count": len(files), "results": results}


# =====================================================================
# 💡 [여기서부터 새로 추가된 부분] LLM 팀원이 데이터를 가져갈 창구입니다!
# =====================================================================
@router.get("/{file_id}")
async def get_ocr_text(file_id: int = Path(..., description="조회할 파일의 DB 고유 번호")):
    """
    LLM 파트에서 요약/청킹 작업을 위해 특정 문서의 OCR 텍스트를 가져가는 API입니다.
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # text 테이블에서 file_id에 해당하는 텍스트만 쏙 빼옵니다.
                cursor.execute("""
                    SELECT extracted_text, created_at 
                    FROM text 
                    WHERE file_id = %s
                """, (file_id,))
                
                result = cursor.fetchone()
                
                if not result:
                    raise HTTPException(status_code=404, detail="해당 파일의 텍스트를 찾을 수 없습니다.")
                
                return {
                    "file_id": file_id,
                    "text": result[0],
                    "created_at": result[1]
                }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 조회 중 오류 발생: {str(e)}")