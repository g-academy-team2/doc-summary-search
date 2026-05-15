import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

try:
	from fpdf import FPDF
except ImportError:
	FPDF = None  # type: ignore[assignment,misc]


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


def save_txt(path: Path, data: list[SummaryResult]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	lines: list[str] = []
	for i, item in enumerate(data, 1):
		lines.append("=" * 60)
		lines.append(f"[{i}] {item.file_name}")
		lines.append(f"모델: {item.model}  |  카테고리: {item.category}  |  상태: {item.status}")
		lines.append(f"소요시간: {item.elapsed_seconds}초  |  토큰/초: {item.tokens_per_second}")
		lines.append("-" * 60)
		lines.append(item.summary or "(요약 없음)")
		if item.error:
			lines.append(f"[오류] {item.error}")
		lines.append("")
	path.write_text("\n".join(lines), encoding="utf-8")


def save_pdf(path: Path, data: list[SummaryResult]) -> None:
	if FPDF is None:
		raise RuntimeError(
			"fpdf2 패키지가 없습니다. `uv pip install fpdf2` 후 재시도하세요."
		)
	korean_font_path = Path("C:/Windows/Fonts/malgun.ttf")

	pdf = FPDF()
	pdf.set_auto_page_break(auto=True, margin=15)

	if korean_font_path.exists():
		pdf.add_font("Korean", fname=str(korean_font_path))
		font_name = "Korean"
	else:
		font_name = "Helvetica"

	for i, item in enumerate(data, 1):
		pdf.add_page()
		pdf.set_font(font_name, size=13)
		pdf.cell(0, 9, f"[{i}] {item.file_name}", new_x="LMARGIN", new_y="NEXT")
		pdf.set_font(font_name, size=9)
		pdf.cell(
			0,
			7,
			f"모델: {item.model}  |  카테고리: {item.category}  |  상태: {item.status}  |  소요: {item.elapsed_seconds}초",
			new_x="LMARGIN",
			new_y="NEXT",
		)
		pdf.ln(3)
		pdf.set_font(font_name, size=10)
		pdf.multi_cell(0, 7, item.summary or "(요약 없음)")
		if item.error:
			pdf.ln(3)
			pdf.set_font(font_name, size=9)
			pdf.multi_cell(0, 7, f"[오류] {item.error}")
	pdf.output(str(path))


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

	if scores["법안"] > 0 and scores["법안"] >= scores["법률"]:
		return "법안"

	best = max(scores.items(), key=lambda item: item[1])
	if best[1] == 0:
		return "IT"
	return best[0]


def validate_table_name(table_name: str) -> str:
	if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
		raise ValueError("db_table은 영문/숫자/언더스코어만 사용 가능하며 숫자로 시작할 수 없습니다.")
	return table_name


def normalize_postgres_url(db_url: str) -> str:
	if db_url.startswith("postgresql+psycopg://"):
		return db_url.replace("postgresql+psycopg://", "postgresql://", 1)
	if db_url.startswith("postgresql+psycopg2://"):
		return db_url.replace("postgresql+psycopg2://", "postgresql://", 1)
	return db_url


def export_results(data: list[SummaryResult], output_dir: Path, stem: str, fmt: str) -> None:
	if fmt in ("json", "all"):
		p = output_dir / f"{stem}.json"
		save_json(p, data)
		print(f"[DONE] JSON: {p}")
	if fmt in ("csv", "all") and data:
		p = output_dir / f"{stem}.csv"
		save_csv(p, data)
		print(f"[DONE] CSV : {p}")
	if fmt in ("txt", "all") and data:
		p = output_dir / f"{stem}.txt"
		save_txt(p, data)
		print(f"[DONE] TXT : {p}")
	if fmt in ("pdf", "all") and data:
		p = output_dir / f"{stem}.pdf"
		try:
			save_pdf(p, data)
			print(f"[DONE] PDF : {p}")
		except RuntimeError as exc:
			print(f"[WARN] PDF 저장 건너뜀: {exc}")
