from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SummaryRecord(BaseModel):
    id: int
    batch_id: str
    file_name: str
    file_path: str
    model: str
    category: str
    status: str
    elapsed_seconds: float
    prompt_chars: int
    summary: Optional[str] = None
    prompt_eval_count: Optional[int] = None
    eval_count: Optional[int] = None
    total_duration_ns: Optional[int] = None
    eval_duration_ns: Optional[int] = None
    tokens_per_second: Optional[float] = None
    error: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryStat(BaseModel):
    category: str
    count: int
