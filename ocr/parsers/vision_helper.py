import os
import base64
import logging
import io
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logger = logging.getLogger(__name__)

def convert_to_safe_png(image_bytes):
    """어떤 형식의 이미지든 OpenAI가 좋아하는 PNG 형식으로 강제 변환합니다."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        output_buffer = io.BytesIO()
        img.save(output_buffer, format="PNG")
        return output_buffer.getvalue()
        
    except Exception as e:
        logger.warning(f"⚠️ 이미지 PNG 변환 실패 (원본 유지): {e}")
        return image_bytes
# ---------------------------------------------

def get_text_from_image_bytes(image_bytes):
    """이미지 바이트 데이터를 받아 OpenAI Vision으로 텍스트를 읽어옵니다."""
    if not image_bytes:
        return ""

    safe_image_bytes = convert_to_safe_png(image_bytes)

    base64_image = base64.b64encode(safe_image_bytes).decode('utf-8')

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "너는 문서 이미지를 텍스트로 변환하는 OCR 전문가야. 친절한 설명은 생략하고, 오직 이미지에서 보이는 텍스트와 표의 내용만 정확하게 추출해서 반환해줘."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": "이 이미지 속의 모든 글자를 읽어서 텍스트로 추출해줘. 표가 있다면 표의 구조를 유지하며 텍스트로 정리해줘."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high" 
                            }
                        },
                    ],
                }
            ],
            max_tokens=1500,
            temperature=0,   
        )
        
        extracted_content = response.choices[0].message.content
        return extracted_content.strip()

    except Exception as e:
        logger.error(f"❌ OpenAI Vision API 호출 실패: {e}")
        return ""