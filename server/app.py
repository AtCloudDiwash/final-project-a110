import json
import random
import sys
import os

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.recommender import recommend_songs
from ai.guardrails import validate_preferences, KNOWN_GENRES, KNOWN_MOODS, KNOWN_MOOD_TAGS
from ai.embeddings import embed_preferences, mmr_rerank
from ai.qdrant_db import search_songs
from ai.gemini import (
    parse_preferences,
    analyze_songs,
    generate_explanations,
    adjust_preferences,
    synthesize_inputs,
)

app = FastAPI(title="Music Viber AI")

_allowed_origins = os.environ.get("ALLOWED_ORIGIN", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

_songs_cache: list[dict] | None = None

_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "new_data", "songs.json")


def get_songs() -> list[dict]:
    global _songs_cache
    if _songs_cache is None:
        with open(_JSON_PATH) as f:
            _songs_cache = json.load(f)
    return _songs_cache


def _build_result(song: dict, score: float, reasons: str) -> dict:
    return {"song": song, "score": round(score, 2), "reasons": reasons}


def _run_pipeline(prefs: dict, mode: str = "balanced") -> dict:

    # Runs the guardrails there: Checks if the prefs matches the defined set of configs
    warnings = validate_preferences(prefs)

    vector = None
    try:

        # Vector embeddings conversion
        vector = embed_preferences(prefs)

        # Vector search
        candidates = search_songs(vector, top_k=50)
    except Exception:
        candidates = get_songs()

    if not candidates:
        candidates = get_songs()

    # Wide pool without hard diversity so MMR has enough to choose from
    raw = recommend_songs(prefs, candidates, k=30, mode=mode, diversity=False) # Notice: I disabled diversity so that the deterministic approach remains disabled

    if vector is not None:
        try:
            #Reranking while keeping the diversity
            raw = mmr_rerank(raw, vector, k=10, lam=0.7)
        except Exception:
            #Fallback method of ranking and diversification
            raw = recommend_songs(prefs, candidates, k=10, mode=mode, diversity=True)
    else:
        raw = recommend_songs(prefs, candidates, k=10, mode=mode, diversity=True)

    results = [_build_result(song, score, reasons) for song, score, reasons in raw]

    # AI explanations for the top 5; rule-based reasons for 6-10
    top5 = results[:5]
    try:
        explanations = generate_explanations("", top5, n=5)
        for i, exp in enumerate(explanations):
            results[i]["explanation"] = exp
    except Exception:
        for r in top5:
            r["explanation"] = r["reasons"]

    for r in results[5:]:
        r["explanation"] = r["reasons"]

    return {"results": results, "warnings": warnings}


# ── Request models ──────────────────────────────────────────────────────────

class TextRequest(BaseModel):
    query: str
    mode: str = "balanced"


class SongsRequest(BaseModel):
    songs: list[str]
    mode: str = "balanced"


class ProfileRequest(BaseModel):
    profile: dict
    mode: str = "balanced"


class RetryRequest(BaseModel):
    original_query: str
    feedback: str
    previous_prefs: dict
    mode: str = "balanced"


class RecommendRequest(BaseModel):
    profile: dict
    query: str | None = None
    songs: list[str] | None = None
    mode: str = "balanced"


# ── Endpoints ───────────────────────────────────────────────────────────────

# When you hit that recommend putting /recommend endpoint runs

@app.post("/recommend")
def recommend(req: RecommendRequest):
    has_addons = bool(req.query) or bool(req.songs)
    if has_addons:
        try:

            # This is where it synthesizes the details sent from frontend to call the gemini. 
            prefs = synthesize_inputs(req.profile, req.query, req.songs)
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))
    else:
        prefs = req.profile

    result = _run_pipeline(prefs, req.mode)
    result["prefs"] = prefs
    result["diff"] = None
    return result

@app.post("/recommend/from-text")
def recommend_from_text(req: TextRequest):
    try:
        prefs = parse_preferences(req.query)
    except (ValueError, Exception) as e:
        raise HTTPException(status_code=422, detail=str(e))
    result = _run_pipeline(prefs, req.mode)
    result["prefs"] = prefs
    result["diff"] = None
    return result


@app.post("/recommend/from-songs")
def recommend_from_songs(req: SongsRequest):
    if not req.songs:
        raise HTTPException(status_code=422, detail="Provide at least one song name.")
    try:
        prefs = analyze_songs(req.songs)
    except (ValueError, Exception) as e:
        raise HTTPException(status_code=422, detail=str(e))
    result = _run_pipeline(prefs, req.mode)
    result["prefs"] = prefs
    result["diff"] = None
    return result


@app.post("/recommend/from-profile")
def recommend_from_profile(req: ProfileRequest):
    result = _run_pipeline(req.profile, req.mode)
    result["prefs"] = req.profile
    result["diff"] = None
    return result


@app.post("/recommend/retry")
def recommend_retry(req: RetryRequest):
    try:
        adjusted = adjust_preferences(
            req.original_query, req.feedback, req.previous_prefs
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    new_prefs = adjusted.get("new_prefs", req.previous_prefs)
    diff = adjusted.get("diff", {})

    result = _run_pipeline(new_prefs, req.mode)
    result["prefs"] = new_prefs
    result["diff"] = diff
    return result


@app.get("/random-profile")
def random_profile():
    return {
        "genre": random.choice(KNOWN_GENRES),
        "mood": random.choice(KNOWN_MOODS),
        "energy": round(random.uniform(0.1, 1.0), 2),
        "likes_acoustic": random.choice([True, False]),
        "preferred_decade": random.choice([1990, 2000, 2010, 2020, None]),
        "preferred_mood_tag": random.choice(KNOWN_MOOD_TAGS + [None]),
    }


@app.get("/health")
def health():
    return {"status": "ok"}
