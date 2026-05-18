import psycopg2
from datetime import datetime

DB_CONFIG = {
    "host": "13.125.122.39",
    "port": "5432",
    "database": "global_db",
    "user": "developer",
    "password": "global22!"
}

def save_file_metadata(user_id: str, file_name: str, extension: str, category: str, summary_text: str) -> int:
    """
    files 테이블에 메타데이터를 저장합니다.
    PostgreSQL enum 값에 맞춰 처리됩니다.
    """
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = """
        INSERT INTO files (user_id, file_name, extension, status, summary, summary_day, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING file_id;
        """
        
        cursor.execute(query, (
            user_id, 
            file_name, 
            extension, 
            'DONE',
            summary_text, 
            datetime.now(), 
            category
        ))
        file_id = cursor.fetchone()[0]
        
        conn.commit()
        print(f"✓ File metadata saved (ID: {file_id})")
        return file_id

    except Exception as e:
        print(f"❌ Error saving file metadata: {e}")
        if conn: conn.rollback()
        return -1
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


def save_raw_text(file_id: int, user_id: str, raw_text: str) -> bool:
    """
    raw 테이블에 OCR 원문을 저장합니다.
    """
    if file_id == -1:
        print("⚠️ File metadata save failed. Skipping raw text save.")
        return False

    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = """
        INSERT INTO raw (file_id, user_id, raw)
        VALUES (%s, %s, %s);
        """
        
        cursor.execute(query, (file_id, user_id, raw_text))
        conn.commit()
        print(f"✓ Raw text saved (File ID: {file_id})")
        return True
        
    except Exception as e:
        print(f"❌ Error saving raw text: {e}")
        if conn: conn.rollback()
        return False
        
    finally:
        if cursor: cursor.close()
        if conn: conn.close()