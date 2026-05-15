import argparse
import os
import sys
import time
from pathlib import Path

try:
	from .api import ensure_models_available, ensure_ollama_up, summarize_with_ollama
	from .db import save_results_to_db, search_results_in_db
	from .util import (
		DEFAULT_MODELS,
		SummaryResult,
		build_prompt,
		classify_document,
		export_results,
		list_text_files,
		ns_to_tps,
		read_text_file,
	)
except ImportError:
	sys.path.append(str(Path(__file__).resolve().parents[2]))
	from llm.prompts.api import ensure_models_available, ensure_ollama_up, summarize_with_ollama
	from llm.prompts.db import save_results_to_db, search_results_in_db
	from llm.prompts.util import (
		DEFAULT_MODELS,
		SummaryResult,
		build_prompt,
		classify_document,
		export_results,
		list_text_files,
		ns_to_tps,
		read_text_file,
	)


def run(args: argparse.Namespace) -> int:
	input_dir = Path(args.input_dir)
	output_dir = Path(args.output_dir)

	if getattr(args, "search", False):
		db_url = args.db_url or os.getenv("DATABASE_URL")
		if not db_url:
			print("[ERROR] 검색 모드에서는 --db-url 또는 DATABASE_URL 환경변수가 필요합니다.")
			return 1
		try:
			rows = search_results_in_db(
				db_url,
				args.db_table,
				keyword=getattr(args, "search_keyword", None),
				category=getattr(args, "search_category", None),
				start_date=getattr(args, "search_start", None),
				end_date=getattr(args, "search_end", None),
				limit=getattr(args, "search_limit", 100),
			)
		except Exception as exc:
			print(f"[ERROR] 검색 실패: {exc}")
			return 1

		if not rows:
			print("[INFO] 검색 결과가 없습니다.")
			return 0

		print(f"[INFO] {len(rows)}건 검색됨")
		for row in rows:
			print(f"\n{'='*60}")
			print(f"파일: {row.get('file_name')}  |  모델: {row.get('model')}  |  카테고리: {row.get('category')}")
			print(f"생성일: {row.get('created_at')}  |  상태: {row.get('status')}")
			print(f"{'─'*60}")
			print(row.get("summary") or "(요약 없음)")

		search_results_data = [
			SummaryResult(
				file_name=str(row.get("file_name", "")),
				file_path=str(row.get("file_path", "")),
				model=str(row.get("model", "")),
				category=str(row.get("category", "")),
				status=str(row.get("status", "")),
				elapsed_seconds=float(row.get("elapsed_seconds") or 0.0),
				prompt_chars=int(row.get("prompt_chars") or 0),
				summary=str(row.get("summary") or ""),
				prompt_eval_count=row.get("prompt_eval_count"),
				eval_count=row.get("eval_count"),
				total_duration_ns=row.get("total_duration_ns"),
				eval_duration_ns=row.get("eval_duration_ns"),
				tokens_per_second=row.get("tokens_per_second"),
				error=row.get("error"),
			)
			for row in rows
		]
		output_dir.mkdir(parents=True, exist_ok=True)
		export_results(search_results_data, output_dir, "search_results", getattr(args, "export_format", "all"))
		return 0

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
	ok_count = sum(1 for r in results if r.status == "ok")
	err_count = len(results) - ok_count
	print(f"[DONE] 완료: 성공 {ok_count}, 실패 {err_count}")
	export_results(results, output_dir, "summary_results", getattr(args, "export_format", "all"))

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
	parser.add_argument(
		"--db-url",
		default="postgresql://developer:global22!@13.125.122.39:5432/global_db",
		help="PostgreSQL 연결 URL (기본값: global_db/developer)",
	)
	parser.add_argument("--db-table", default="summary_results", help="요약 결과 저장 테이블명")
	parser.add_argument("--recursive", action="store_true", help="하위 폴더까지 탐색")
	parser.add_argument(
		"--export-format",
		choices=["json", "csv", "txt", "pdf", "all"],
		default="all",
		help="출력 파일 형식 (기본값: all)",
	)
	parser.add_argument("--search", action="store_true", help="DB에서 요약 결과 검색 모드")
	parser.add_argument("--search-keyword", default=None, help="검색할 키워드 (요약 내용 또는 파일명)")
	parser.add_argument(
		"--search-category",
		default=None,
		choices=["IT", "법률", "법안", "교육"],
		help="검색 카테고리 필터",
	)
	parser.add_argument("--search-start", default=None, help="검색 시작 날짜 (예: 2025-01-01)")
	parser.add_argument("--search-end", default=None, help="검색 종료 날짜 (예: 2025-12-31)")
	parser.add_argument("--search-limit", type=int, default=100, help="검색 결과 최대 개수")
	return parser.parse_args()


def main() -> int:
	return run(parse_args())


if __name__ == "__main__":
	raise SystemExit(main())
