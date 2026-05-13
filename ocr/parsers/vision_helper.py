import os
import base64
import logging
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일 로드 및 클라이언트 초기화
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 로그 설정
logger = logging.getLogger(__name__)

def get_text_from_image_bytes(image_bytes):
    """이미지 바이트 데이터를 받아 OpenAI Vision으로 텍스트를 읽어옵니다."""
    if not image_bytes:
        return ""

    # 이미지 인코딩
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    try:
        # OpenAI API 호출
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
                                "detail": "high"  # ✨ 작은 글자나 표를 더 정밀하게 분석
                            }
                        },
                    ],
                }
            ],
            max_tokens=1500, # 표 내용이 길 수 있으므로 넉넉하게 설정
            temperature=0,   # ✨ 일관성 있는 추출을 위해 창의성을 0으로 설정
        )
        
        extracted_content = response.choices[0].message.content
        return extracted_content.strip()

    except Exception as e:
        # 에러 발생 시 로그를 남겨 추적 가능하게 함
        logger.error(f"❌ OpenAI Vision API 호출 실패: {e}")
        return ""