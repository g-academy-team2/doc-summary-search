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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text):
    """공백 및 특수문자 정제 (세탁기)"""
    if not text: return ""
    
    text = re.sub(r'[^\w\s\.,!?가-힣a-zA-Z0-9\-\(\)\[\]★☆▶▷➔→·]', ' ', text)
    
    text = re.sub(r' {2,}', ' ', text)

    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def total_parser(file_path):
    """확장자에 따라 전문가에게 일을 배분하는 총괄 엔진"""
    if not os.path.exists(file_path):
        return f"❌ 파일을 찾을 수 없습니다: {file_path}"

    ext = os.path.splitext(file_path)[1].lower()
    logger.info(f"📂 [{ext}] 파일 분석 모드 가동")

    if ext == ".ppt":
        return "❌ .ppt 파일은 이전 버전 형식입니다. [.pptx] 형식으로 변환 후 다시 업로드해 주세요."

    raw_text = ""
    
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
        return "⚠️ 파일에서 텍스트를 추출하지 못했습니다. 문서가 비어있거나 보안(암호)이 걸려있는지 확인해 주세요."
    
    return clean_text(raw_text)