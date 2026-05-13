import argparse
import csv
import json
import os
import re
import time
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import requests

try:
	import psycopg
except ImportError:
	psycopg = None


DEFAULT_MODELS = [
	"gemma2:2b",
	"gemma2:9b",
]


@dataclass
class SummaryResult:
	file_name: str
	file_path: str
	model: str
	category: str
	status: str
	elapsed_seconds: float
	prompt_chars: int
	summary: str
	prompt_eval_count: int | None
	eval_count: int | None
	total_duration_ns: int | None
	eval_duration_ns: int | None
	tokens_per_second: float | None
	error: str | None


def build_prompt(text: str, max_input_chars: int) -> str:
	clipped = text[:max_input_chars]
	return (
		"당신은 문서 요약 전문가입니다.\n"
		"아래 OCR 추출 텍스트를 읽고, 한국어로 요약해 주세요.\n\n"
		"[출력 형식]\n"
		"1) 한 줄 핵심 요약\n"
		"2) 주요 포인트 5개 이하\n"
		"3) 업무 액션 아이템(있다면)\n"
		"4) 숫자/날짜/고유명사 등 중요 엔티티\n\n"
		"[주의]\n"
		"- OCR 노이즈가 있으면 문맥으로 보정\n"
		"- 불확실한 내용은 추정이라고 표기\n"
		"- 출력은 간결하고 읽기 쉽게\n\n"
		"[문서 본문]\n"
		f"{clipped}"
	)


def list_text_files(input_dir: Path, recursive: bool) -> list[Path]:
	patterns = ["*.txt", "*.md", "*.text"]
	files: list[Path] = []
	if recursive:
		for pattern in patterns:
			files.extend(input_dir.rglob(pattern))
	else:
		for pattern in patterns:
			files.extend(input_dir.glob(pattern))
	return sorted([p for p in files if p.is_file()])


def read_text_file(path: Path, encoding: str = "utf-8") -> str:
	try:
		return path.read_text(encoding=encoding)
	except UnicodeDecodeError:
		return path.read_text(encoding="cp949", errors="replace")


def ensure_ollama_up(base_url: str, timeout: int) -> None:
	try:
		response = requests.get(f"{base_url}/api/tags", timeout=timeout)
		response.raise_for_status()
	except Exception as exc:
		raise RuntimeError(
			"Ollama 서버에 연결할 수 없습니다. "
			"ollama serve 실행 여부와 --ollama-url 값을 확인하세요."
		) from exc


def ensure_models_available(base_url: str, timeout: int, models: list[str]) -> tuple[list[str], list[str]]:
	response = requests.get(f"{base_url}/api/tags", timeout=timeout)
	response.raise_for_status()
	payload = response.json()
	available = {m.get("name", "") for m in payload.get("models", [])}
	present: list[str] = []
	missing: list[str] = []
	for model in models:
		if model in available:
			present.append(model)
		else:
			missing.append(model)
	return present, missing


def summarize_with_ollama(
	base_url: str,
	timeout: int,
	model: str,
	prompt: str,
	temperature: float,
) -> dict[str, Any]:
	payload = {
		"model": model,
		"prompt": prompt,
		"stream": False,
		"options": {
			"temperature": temperature,
		},
	}
	response = requests.post(f"{base_url}/api/generate", json=payload, timeout=timeout)
	response.raise_for_status()
	return response.json()


def ns_to_tps(eval_count: int | None, eval_duration_ns: int | None) -> float | None:
	if not eval_count or not eval_duration_ns:
		return None
	duration_sec = eval_duration_ns / 1_000_000_000
	if duration_sec <= 0:
		return None
	return eval_count / duration_sec


def save_json(path: Path, data: list[SummaryResult]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(
		json.dumps([asdict(item) for item in data], ensure_ascii=False, indent=2),
		encoding="utf-8",
	)


def save_csv(path: Path, data: list[SummaryResult]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", newline="", encoding="utf-8-sig") as f:
		writer = csv.DictWriter(f, fieldnames=list(asdict(data[0]).keys()))
		writer.writeheader()
		for item in data:
			writer.writerow(asdict(item))


def classify_document(text: str, summary: str) -> str:
	combined = (text[:8000] + "\n" + (summary or "")).lower()

	keywords = {
		"IT": [
			"ai",
			"llm",
			"api",
			"서버",
			"클라우드",
			"데이터",
			"python",
			"java",
			"프로그래밍",
			"시스템",
			"네트워크",
			"소프트웨어",
			"하드웨어",
			"알고리즘",
			"머신러닝",
		],
		"법률": [
			"판결",
			"소송",
			"계약",
			"약관",
			"형사",
			"민사",
			"헌법",
			"법원",
			"변호사",
			"법률",
			"조항",
			"시행",
			"규정",
			"위법",
			"준법",
		],
		"법안": [
			"법안",
			"입법예고",
			"제안이유",
			"의안",
			"발의",
			"제정안",
			"일부개정안",
			"전부개정안",
			"국회",
			"상임위원회",
			"본회의",
			"의결",
			"공포 전",
		],
		"교육": [
			"교육",
			"학습",
			"학교",
			"대학",
			"학생",
			"교사",
			"교수",
			"수업",
			"교과",
			"평가",
			"커리큘럼",
			"학기",
			"강의",
			"입시",
			"학부모",
		],
	}

	scores: dict[str, int] = {k: 0 for k in keywords}
	for category, words in keywords.items():
		for word in words:
			scores[category] += combined.count(word)

	# If score ties, prefer 법안 over 법률 when legislative signals are present.
	if scores["법안"] > 0 and scores["법안"] >= scores["법률"]:
		return "법안"

	best = max(scores.items(), key=lambda item: item[1])
	if best[1] == 0:
		# Default bucket when no signal is found.
		return "IT"
	return best[0]


def validate_table_name(table_name: str) -> str:
	if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
		raise ValueError("db_table은 영문/숫자/언더스코어만 사용 가능하며 숫자로 시작할 수 없습니다.")
	return table_name


def normalize_postgres_url(db_url: str) -> str:
	# psycopg uses postgresql://... format and does not need SQLAlchemy dialect suffixes.
	if db_url.startswith("postgresql+psycopg://"):
		return db_url.replace("postgresql+psycopg://", "postgresql://", 1)
	if db_url.startswith("postgresql+psycopg2://"):
		return db_url.replace("postgresql+psycopg2://", "postgresql://", 1)
	return db_url


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


def run(args: argparse.Namespace) -> int:
	input_dir = Path(args.input_dir)
	output_dir = Path(args.output_dir)

	if not input_dir.exists() or not input_dir.is_dir():
		print(f"[ERROR] input_dir가 올바르지 않습니다: {input_dir}")
		return 1

	ensure_ollama_up(args.ollama_url, args.timeout)

	models = [m.strip() for m in args.models.split(",") if m.strip()]
	present_models, missing_models = ensure_models_available(args.ollama_url, args.timeout, models)

	if missing_models:
		print("[WARN] 아래 모델은 로컬에 없습니다:")
		for model in missing_models:
			print(f"  - {model}")
		print("[HINT] 예: ollama pull gemma2:9b")

	if not present_models:
		print("[ERROR] 사용 가능한 모델이 없습니다. 모델 pull 후 다시 실행하세요.")
		return 1

	files = list_text_files(input_dir, args.recursive)
	if not files:
		print("[ERROR] 처리할 텍스트 파일(.txt/.md/.text)이 없습니다.")
		return 1

	print(f"[INFO] 파일 {len(files)}개, 모델 {len(present_models)}개 처리 시작")

	results: list[SummaryResult] = []
	total_jobs = len(files) * len(present_models)
	done = 0

	for file_path in files:
		text = read_text_file(file_path)
		prompt = build_prompt(text, args.max_input_chars)

		for model in present_models:
			done += 1
			print(f"[RUN] ({done}/{total_jobs}) {file_path.name} | {model}")
			started = time.perf_counter()

			try:
				output = summarize_with_ollama(
					base_url=args.ollama_url,
					timeout=args.timeout,
					model=model,
					prompt=prompt,
					temperature=args.temperature,
				)
				elapsed = time.perf_counter() - started
				eval_count = output.get("eval_count")
				eval_duration_ns = output.get("eval_duration")
				category = classify_document(text, output.get("response", ""))

				result = SummaryResult(
					file_name=file_path.name,
					file_path=str(file_path),
					model=model,
					category=category,
					status="ok",
					elapsed_seconds=round(elapsed, 3),
					prompt_chars=len(prompt),
					summary=output.get("response", "").strip(),
					prompt_eval_count=output.get("prompt_eval_count"),
					eval_count=eval_count,
					total_duration_ns=output.get("total_duration"),
					eval_duration_ns=eval_duration_ns,
					tokens_per_second=ns_to_tps(eval_count, eval_duration_ns),
					error=None,
				)
			except Exception as exc:
				elapsed = time.perf_counter() - started
				category = classify_document(text, "")
				result = SummaryResult(
					file_name=file_path.name,
					file_path=str(file_path),
					model=model,
					category=category,
					status="error",
					elapsed_seconds=round(elapsed, 3),
					prompt_chars=len(prompt),
					summary="",
					prompt_eval_count=None,
					eval_count=None,
					total_duration_ns=None,
					eval_duration_ns=None,
					tokens_per_second=None,
					error=str(exc),
				)

			results.append(result)

	output_dir.mkdir(parents=True, exist_ok=True)
	json_path = output_dir / "summary_results.json"
	csv_path = output_dir / "summary_results.csv"
	save_json(json_path, results)
	if results:
		save_csv(csv_path, results)

	ok_count = sum(1 for r in results if r.status == "ok")
	err_count = len(results) - ok_count
	print(f"[DONE] 완료: 성공 {ok_count}, 실패 {err_count}")
	print(f"[DONE] JSON: {json_path}")
	print(f"[DONE] CSV : {csv_path}")

	db_url = args.db_url or os.getenv("DATABASE_URL")
	if db_url:
		try:
			batch_id, inserted = save_results_to_db(db_url, args.db_table, results)
			print(f"[DONE] DB  : 테이블 {args.db_table}에 {inserted}건 저장 완료 (batch_id={batch_id})")
		except Exception as exc:
			print(f"[WARN] DB 저장 실패: {exc}")
	else:
		print("[INFO] DATABASE_URL 또는 --db-url 미설정으로 DB 저장은 건너뜁니다.")

	return 0


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description=(
			"Ollama 기반 문서 요약 벤치마크 도구. "
			"OCR/파서가 만든 텍스트 파일을 모델별로 요약하고 성능을 비교합니다."
		)
	)
	parser.add_argument("--input-dir", default="./input_texts", help="입력 텍스트 폴더")
	parser.add_argument("--output-dir", default="./outputs", help="결과 저장 폴더")
	parser.add_argument(
		"--models",
		default=",".join(DEFAULT_MODELS),
		help="쉼표(,)로 구분된 Ollama 모델 목록",
	)
	parser.add_argument("--ollama-url", default="http://127.0.0.1:11434", help="Ollama 서버 URL")
	parser.add_argument("--timeout", type=int, default=300, help="요청 타임아웃(초)")
	parser.add_argument("--temperature", type=float, default=0.2, help="생성 온도")
	parser.add_argument(
		"--max-input-chars",
		type=int,
		default=16000,
		help="프롬프트에 포함할 최대 문자 수",
	)
	parser.add_argument("--db-url", default=None, help="PostgreSQL 연결 URL (없으면 환경변수 DATABASE_URL 사용)")
	parser.add_argument("--db-table", default="summary_results", help="요약 결과 저장 테이블명")
	parser.add_argument("--recursive", action="store_true", help="하위 폴더까지 탐색")
	return parser.parse_args()


if __name__ == "__main__":
	raise SystemExit(run(parse_args()))
