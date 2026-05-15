import psycopg2
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 쓰기 권한이 있는 backend 계정 정보
DB_CONFIG = {
    "host": "13.125.122.39",
    "port": "5432",
    "database": "global_db",
    "user": "backend",
    "password": "global22!",
    "connect_timeout": 5
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """텍스트 추출 결과를 담을 text 테이블 생성"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS text (
                        text_id SERIAL PRIMARY KEY,
                        file_id INT,
                        user_id VARCHAR(50),
                        extracted_text TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                conn.commit()
                logger.info("✅ DB 테이블(text) 준비 완료")
    except Exception as e:
        logger.error(f"❌ DB 초기화 실패: {e}")

def save_ocr_result(filename, extension, content, user_id="testid"):
    """
    1. files 테이블에 메타데이터 저장 (이미지 확인 컬럼명 적용)
    2. text 테이블에 본문 저장
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # 단계 1: files 테이블 저장 (이미지에서 확인된 컬럼명 사용)
                # status와 category는 ENUM 타입일 확률이 높으므로 기본값을 대문자로 시도해봅니다.
                cursor.execute("""
                    INSERT INTO files (user_id, file_name, extension, status)
                    VALUES (%s, %s, %s, %s)
                    RETURNING file_id;
                """, (user_id, filename, extension, 'DONE')) # 또는 'ING'
                
                file_id = cursor.fetchone()[0]

                # 단계 2: text 테이블에 본문 저장
                cursor.execute("""
                    INSERT INTO text (file_id, user_id, extracted_text)
                    VALUES (%s, %s, %s)
                """, (file_id, user_id, content))
                
                conn.commit()
                logger.info(f"💾 DB 저장 성공! (File ID: {file_id}, Table: text)")
                return file_id
    except Exception as e:
        logger.error(f"❌ DB 저장 실패: {e}")
        # 만약 ENUM 값 오류가 난다면 status를 'SUCCESS' 대신 다른 값으로 바꿔야 할 수 있습니다.
        return None