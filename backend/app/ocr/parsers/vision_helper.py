import os
import logging
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path: str) -> str:
    """
    오픈소스 OCR(Tesseract)을 사용하여 
    이미지(jpg, png 등)에서 텍스트를 추출하는 전용 함수입니다.
    """
    if not os.path.exists(image_path):
        logger.error(f"❌ 이미지를 찾을 수 없습니다: {image_path}")
        return ""

    try:
        logger.info(f"👁️ 이미지 OCR 분석 시작: {os.path.basename(image_path)}")
        
        # 1. 이미지를 파이썬으로 열어줍니다
        img = Image.open(image_path)
        
        # 2. Tesseract OCR을 실행하여 글자를 추출합니다. (한국어+영어)
        extracted_text = pytesseract.image_to_string(img, lang='kor+eng')
        
        # 3. 추출된 텍스트가 비어있지 않다면 반환합니다.
        if extracted_text and extracted_text.strip():
            logger.info("✅ 이미지 OCR 분석 완료")
            return extracted_text.strip()
        else:
            logger.warning("⚠️ 이미지에서 읽을 수 있는 텍스트가 없습니다.")
            return ""
            
    except Exception as e:
        logger.error(f"❌ 이미지 OCR 처리 중 오류 발생: {e}")
        return ""