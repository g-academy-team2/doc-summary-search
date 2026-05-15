from datetime import datetime
from typing import Any

try:
	import psycopg
except ImportError:
	psycopg = None

from .util import SummaryResult, normalize_postgres_url, validate_table_name


def ensure_summary_table(conn: Any, table_name: str) -> None:
	table_name = validate_table_name(table_name)
	with conn.cursor() as cur:
		cur.execute(
			f"""
			CREATE TABLE IF NOT EXISTS {table_name} (
				id BIGSERIAL PRIMARY KEY,
				batch_id TEXT NOT NULL,
				file_name TEXT NOT NULL,
				file_path TEXT NOT NULL,
				model TEXT NOT NULL,
				category TEXT NOT NULL,
				status TEXT NOT NULL,
				elapsed_seconds DOUBLE PRECISION NOT NULL,
				prompt_chars INTEGER NOT NULL,
				summary TEXT,
				prompt_eval_count INTEGER,
				eval_count INTEGER,
				total_duration_ns BIGINT,
				eval_duration_ns BIGINT,
				tokens_per_second DOUBLE PRECISION,
				error TEXT,
				created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
			)
			"""
		)
		cur.execute(
			f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS category TEXT"
		)
		cur.execute(
			f"CREATE INDEX IF NOT EXISTS idx_{table_name}_batch_id ON {table_name}(batch_id)"
		)
	conn.commit()


def save_results_to_db(db_url: str, table_name: str, data: list[SummaryResult]) -> tuple[str, int]:
	if not data:
		return "", 0

	if psycopg is None:
		raise RuntimeError("psycopg 패키지가 없어 DB 저장을 할 수 없습니다. `uv pip install psycopg[binary]` 후 재시도하세요.")

	batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
	normalized_url = normalize_postgres_url(db_url)
	table_name = validate_table_name(table_name)

	with psycopg.connect(normalized_url) as conn:
		ensure_summary_table(conn, table_name)
		rows = [
			(
				batch_id,
				item.file_name,
				item.file_path,
				item.model,
				item.category,
				item.status,
				item.elapsed_seconds,
				item.prompt_chars,
				item.summary,
				item.prompt_eval_count,
				item.eval_count,
				item.total_duration_ns,
				item.eval_duration_ns,
				item.tokens_per_second,
				item.error,
			)
			for item in data
		]

		with conn.cursor() as cur:
			cur.executemany(
				f"""
				INSERT INTO {table_name} (
					batch_id,
					file_name,
					file_path,
					model,
					category,
					status,
					elapsed_seconds,
					prompt_chars,
					summary,
					prompt_eval_count,
					eval_count,
					total_duration_ns,
					eval_duration_ns,
					tokens_per_second,
					error
				) VALUES (
					%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
				)
				""",
				rows,
			)
		conn.commit()

	return batch_id, len(rows)


def search_results_in_db(
	db_url: str,
	table_name: str,
	*,
	keyword: str | None = None,
	category: str | None = None,
	start_date: str | None = None,
	end_date: str | None = None,
	limit: int = 100,
) -> list[dict[str, Any]]:
	if psycopg is None:
		raise RuntimeError(
			"psycopg 패키지가 없습니다. `uv pip install psycopg[binary]`를 실행하세요."
		)
	table_name = validate_table_name(table_name)
	normalized_url = normalize_postgres_url(db_url)

	conditions: list[str] = []
	params: list[Any] = []

	if keyword:
		conditions.append("(summary ILIKE %s OR file_name ILIKE %s)")
		params.extend([f"%{keyword}%", f"%{keyword}%"])
	if category:
		conditions.append("category = %s")
		params.append(category)
	if start_date:
		conditions.append("created_at >= %s::timestamptz")
		params.append(start_date)
	if end_date:
		conditions.append("created_at <= %s::timestamptz")
		params.append(end_date)

	where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
	query = f"SELECT * FROM {table_name} {where} ORDER BY created_at DESC LIMIT %s"
	params.append(limit)

	with psycopg.connect(normalized_url) as conn:
		with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
			cur.execute(query, params)
			return [dict(row) for row in cur.fetchall()]
