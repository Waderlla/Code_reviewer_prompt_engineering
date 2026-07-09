# AI Code Reviewer — wersja lokalna, darmowa

Aplikacja na zaliczenie zadania z tygodnia 3: Prompt Engineering.

🇬🇧 English version: [README.md](README.md)

## Co robi

- Przyjmuje kod projektu jako dane wejściowe.
- Ma prompt z dwoma parametrami: język projektu i skala oceny.
- Wykonuje code review lokalnym modelem przez Ollama.
- Zwraca wynik w strukturze `CodeReviewResult`:
  - `overall_score`
  - `found_issues`
  - `improved_code`
- Prompt zarządzany jest w LangFuse (Prompt Management) zamiast na sztywno w kodzie.
- Każde wywołanie modelu jest logowane w LangFuse (observability).
- Frontend zbudowany w Google AI Studio (narzędzie do prototypowania — "vibe coding").

Krok z platformą OpenAI ("Reusable Prompts") został celowo pominięty — zadanie
wykonano w całości bez płatnych usług, zgodnie z podejściem 100% lokalnym/darmowym
(lokalny model przez Ollamę zamiast OpenAI API).

## Struktura projektu

```
app.py, llm.py, models.py, prompts.py   -> backend FastAPI (tylko JSON API, bez HTML)
frontend/                                -> frontend React/Vite, wygenerowany w Google AI Studio
push_prompts_to_langfuse.py              -> jednorazowy skrypt wgrywający prompty do LangFuse
```

## 1. Instalacja Ollama

Pobierz i zainstaluj Ollama:

https://ollama.com/download

Po instalacji pobierz model:

```bash
ollama pull qwen2.5-coder:7b
```

Jeśli komputer jest słabszy, możesz użyć mniejszego modelu:

```bash
ollama pull qwen2.5-coder:3b
```

## 2. LangFuse (prompt management + observability)

Załóż darmowe konto na https://cloud.langfuse.com, stwórz projekt i pobierz klucze API.

Stwórz plik `.env` w folderze projektu:

```
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_HOST="https://cloud.langfuse.com"
```

Jednorazowo wgraj prompty do LangFuse:

```bash
python push_prompts_to_langfuse.py
```

## 3. Uruchomienie backendu

W folderze projektu:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Instalacja zależności:

```bash
pip install -r requirements.txt
```

Uruchomienie:

```bash
uvicorn app:app --reload
```

Backend działa na `http://127.0.0.1:8000` i udostępnia endpoint `POST /api/review` (JSON).

## 4. Uruchomienie frontendu

Wymaga Node.js (https://nodejs.org).

```bash
cd frontend
npm install
npm run dev
```

Otwórz adres, który wypisze Vite (domyślnie `http://localhost:3000`). Łączy się z
backendem pod `http://127.0.0.1:8000/api/review` — oba muszą działać lokalnie, na
tym samym komputerze, w tym samym czasie. Potwierdzone jako działające od początku
do końca (realne wywołanie Ollamy, realny wynik wyrenderowany w UI).

## 5. Gdzie jest prompt?

Treść promptów (fallback + źródło do wgrania do LangFuse) jest w pliku `prompts.py`.
Docelowo prompty pobierane są z LangFuse (Prompt Management), z lokalnym fallbackiem
na wypadek gdyby LangFuse był nieosiągalny.

Zmiennymi w promptcie są: `language`, `score_scale`, `code`.

## 6. Uwaga o Structured Outputs

Lokalne modele nie mają tak ścisłego `response_format: json_schema` jak OpenAI API,
dlatego aplikacja wymusza JSON w promptcie, używa trybu `format: "json"` w Ollama
i waliduje wynik przez Pydantic (`CodeReviewResult`).
