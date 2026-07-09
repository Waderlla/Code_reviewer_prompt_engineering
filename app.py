from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from llm import ReviewError, review_code_with_ollama
from models import CodeReviewResult, ReviewRequest

app = FastAPI(title="AI Code Reviewer - lokalnie i za darmo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PrivateNetworkAccessMiddleware(BaseHTTPMiddleware):
    """Pozwala przeglądarce łączyć się z tym localhost-owym API ze stron
    hostowanych publicznie (np. podgląd w AI Studio) — Chrome wymaga tego
    nagłówka przy żądaniach z publicznej sieci do prywatnej (Private Network Access)."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        return response


app.add_middleware(PrivateNetworkAccessMiddleware)


@app.post("/api/review", response_model=CodeReviewResult)
def review_api(payload: ReviewRequest):
    """Endpoint JSON dla frontendu (frontend/, zbudowanego w Google AI Studio)."""
    try:
        return review_code_with_ollama(payload.code, payload.language, payload.score_scale, payload.model)
    except ReviewError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
