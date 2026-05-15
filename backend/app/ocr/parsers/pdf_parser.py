import os
import re
import logging
# 상대 경로를 통해 상위 폴더의 db_helper에 접근합니다.
from ..db_helper import init_db, save_ocr_result

try:
    from .pdf_parser import extract_text_from_pdf
    from .docx_parser import extract_text_from_docx
    from .pptx_parser import extract_text_from_pptx
    from .hwp_parser import extract_text_from_hwp
except ImportError:
    from pdf_parser import extract_text_from_pdf
    from docx_parser import extract_text_from_docx
    from pptx_parser import extract_text_from_pptx
    from hwp_parser import extract_text_from_hwp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 파서 모듈이 로드될 때 DB 테이블이 없다면 생성합니다.
init_db()

def clean_text(text):
    """공백 및 특수문자 정제 (세탁기)"""
    if not text: return ""
    
    text = re.sub(r'[^\w\s\.,!?가-힣a-zA-Z0-9\-\(\)\[\]★☆▶▷➔→·]', ' ', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def total_parser(file_path):
    """확장자에 따라 전문가에게 일을 배분하고 결과를 공용 DB에 저장하는 엔진"""
    if not os.path.exists(file_path):
        return f"❌ 파일을 찾을 수 없습니다: {file_path}"

    # 파일명과 확장자 추출 (DB 저장용)
    filename = os.path.basename(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    file_type = ext.replace('.', '') # 'pdf', 'hwp' 등
    
    logger.info(f"📂 [{ext}] 파일 분석 모드 가동: {filename}")

    if ext == ".ppt":
        return "❌ .ppt 파일은 이전 버전 형식입니다. [.pptx] 형식으로 변환 후 다시 업로드해 주세요."

    raw_text = ""
    
    # 확장자별 파서 호출
    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        raw_text = extract_text_from_docx(file_path)
    elif ext == ".pptx":
        raw_text = extract_text_from_pptx(file_path)
    elif ext == ".hwp":
        raw_text = extract_text_from_hwp(file_path)
    else:
        return f"❌ 지원하지 않는 확장자입니다: {ext}"
    
    if not raw_text or len(raw_text.strip()) == 0:
        return "⚠️ 파일에서 텍스트를 추출하지 못했습니다."
    
    # 텍스트 정제
    cleaned_text = clean_text(raw_text)

    # 💡 [핵심 추가]: 정제된 텍스트를 공용 PostgreSQL DB에 저장합니다.
    if cleaned_text:
        doc_id = save_ocr_result(filename, file_type, cleaned_text)
        if doc_id:
            logger.info(f"✅ DB 저장 성공 (ID: {doc_id})")
        else:
            logger.warning("⚠️ DB 저장에 실패했습니다. (권한이나 네트워크 확인 필요)")
    
    return cleaned_text