import json
import re
from typing import Any

import requests
from langfuse import observe
from pydantic import ValidationError

from models import CodeReviewResult
from prompts import build_user_prompt, get_system_prompt

OLLAMA_URL = "http://localhost:11434/api/chat"


class ReviewError(Exception):
    pass


def _extract_json(text: str) -> dict[str, Any]:
    """Model lokalny czasem doda tekst obok JSON-a. Wyciągamy pierwszy obiekt JSON."""
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        candidate = text
    else:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ReviewError("Model nie zwrócił JSON-a. Spróbuj ponownie albo użyj mocniejszego modelu.")
        candidate = match.group(0)

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ReviewError(
            "Model zwrócił niepoprawny JSON. Spróbuj ponownie albo użyj mocniejszego modelu."
        ) from exc


@observe()
def review_code_with_ollama(code: str, language: str, score_scale: str, model: str) -> CodeReviewResult:
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": build_user_prompt(language, score_scale, code)},
        ],
        "options": {
            "temperature": 0.2,
        },
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
    except requests.RequestException as exc:
        raise ReviewError(
            "Nie udało się połączyć z Ollamą. Sprawdź, czy Ollama jest uruchomiona: ollama serve"
        ) from exc

    if response.status_code != 200:
        raise ReviewError(f"Ollama zwróciła błąd {response.status_code}: {response.text}")

    data = response.json()
    content = data.get("message", {}).get("content", "")
    parsed = _extract_json(content)

    try:
        result = CodeReviewResult.model_validate(parsed)
    except ValidationError as exc:
        raise ReviewError(
            "Model zwrócił JSON niezgodny ze schematem CodeReviewResult. "
            "Spróbuj ponownie albo użyj mocniejszego modelu."
        ) from exc

    if not result.improved_code.strip():
        result.improved_code = code

    return result
