import os
import logging
import pdfplumber
from .vision_helper import get_text_from_image_bytes # ✨ 공통의 '눈' 불러오기
from io import BytesIO

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """텍스트 추출과 Vision OCR을 결합한 하이브리드 파서"""
    if not os.path.exists(file_path):
        logger.error(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        return ""

    full_text_list = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                # 1. 일단 일반적인 방법으로 텍스트 추출 시도
                text = page.extract_text()
                
                # 2. 글자가 너무 없거나(이미지 위주) 인식 실패 시 OpenAI '눈' 가동!
                if not text or len(text.strip()) < 50:
                    logger.info(f"👀 {i+1}페이지 텍스트 부족(약 {len(text) if text else 0}자). AI Vision 모드 가동...")
                    
                    try:
                        # 페이지를 이미지로 변환 (해상도 150으로 최적화)
                        page_image = page.to_image(resolution=150).original
                        
                        # 이미지를 바이트로 변환하여 vision_helper에 전달
                        img_buffer = BytesIO()
                        page_image.save(img_buffer, format="PNG")
                        
                        vision_text = get_text_from_image_bytes(img_buffer.getvalue())
                        if vision_text:
                            text = vision_text
                    except Exception as vision_err:
                        logger.warning(f"⚠️ {i+1}페이지 Vision OCR 실패: {vision_err}")
                
                if text:
                    full_text_list.append(text)
                logger.info(f"✅ {i+1}/{len(pdf.pages)} 페이지 처리 완료")

        return "\n\n".join(full_text_list)

    except Exception as e:
        logger.error(f"❌ PDF 파싱 중 심각한 오류 발생: {e}")
        return f"PDF 읽기 실패: {str(e)}"