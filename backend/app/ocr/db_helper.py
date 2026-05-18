import os
import psycopg2
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

def get_connection():
    """.env 파일에 정의된 DATABASE_URL을 활용하여 PostgreSQL 데이터베이스에 연결합니다."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("❌ 환경 변수 'DATABASE_URL'을 찾을 수 없습니다. .env 파일을 확인해 주세요.")
        raise ValueError("DATABASE_URL is not set in environment variables.")
    
    return psycopg2.connect(db_url)

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
    1. files 테이블에 메타데이터 저장 (RETURNING을 이용해 생성된 file_id 획득)
    2. text 테이블에 추출된 본문 저장
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # 단계 1: files 테이블 저장
                cursor.execute("""
                    INSERT INTO files (user_id, file_name, extension, status)
                    VALUES (%s, %s, %s, %s)
                    RETURNING file_id;
                """, (user_id, filename, extension, 'DONE'))
                
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
        return None