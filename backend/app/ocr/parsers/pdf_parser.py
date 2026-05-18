import os
import logging
import pdfplumber
import uuid
# 💡 우리가 아까 새로 만든 Tesseract 비전 헬퍼를 불러옵니다!
from app.ocr.parsers.vision_helper import extract_text_from_image 

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
                text = page.extract_text()
                
                # 💡 글자가 없거나 너무 적으면(스캔본) 이미지로 변환해서 비전 헬퍼에게 넘깁니다!
                if not text or len(text.strip()) < 50:
                    logger.info(f"👀 {i+1}페이지 텍스트 부족. AI Vision 모드 가동...")
                    
                    try:
                        # 1. 페이지를 이미지 객체로 변환
                        page_image = page.to_image(resolution=150).original
                        
                        # 2. 임시 파일로 저장 (비전 헬퍼가 파일 경로를 필요로 하기 때문)
                        temp_img_path = f"temp_page_{uuid.uuid4().hex}.png"
                        page_image.save(temp_img_path, format="PNG")
                        
                        # 3. 비전 헬퍼에게 이미지 읽기 지시
                        vision_text = extract_text_from_image(temp_img_path)
                        
                        # 4. 다 쓴 임시 이미지 파일 삭제
                        if os.path.exists(temp_img_path):
                            os.remove(temp_img_path)
                            
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