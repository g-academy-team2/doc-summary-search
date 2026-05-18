import os
import re
import logging

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

logger = logging.getLogger(__name__)

def clean_text(text):
    """공백 및 특수문자 정제 (세탁기)"""
    if not text: return ""
    
    text = re.sub(r'[^\w\s\.,!?가-힣a-zA-Z0-9\-\(\)\[\]★☆▶▷➔→·]', ' ', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def total_parser(file_path):
    """오직 확장자에 따라 텍스트를 추출하고 정제하는 순수 엔진 (DB 저장 X)"""
    if not os.path.exists(file_path):
        return f"❌ 파일을 찾을 수 없습니다: {file_path}"

    ext = os.path.splitext(file_path)[1].lower()
    logger.info(f"📂 [{ext}] 파일 분석 모드 가동")

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
    
    # 텍스트 정제 후 순수 텍스트만 반환 (DB 저장은 ocr.py 창구에서 알아서 합니다!)
    cleaned_text = clean_text(raw_text)
    
    return cleaned_text