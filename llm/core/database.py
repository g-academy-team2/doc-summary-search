import os
from pathlib import Path

from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _normalize_url(url: str) -> str:
    for prefix in ("postgresql+psycopg://", "postgresql+psycopg2://"):
        if url.startswith(prefix):
            return "postgresql://" + url[len(prefix):]
    return url


def get_db_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL 환경변수가 설정되지 않았습니다.")
    return _normalize_url(url)


def get_connection():
    return psycopg.connect(get_db_url(), row_factory=dict_row)
