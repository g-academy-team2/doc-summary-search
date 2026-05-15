from typing import Any

import requests


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
