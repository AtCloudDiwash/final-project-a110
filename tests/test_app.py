import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch
from fastapi.testclient import TestClient
from server.app import app, _run_pipeline

client = TestClient(app)

# ── Shared fixtures ──────────────────────────────────────────────────────────

FAKE_PREFS = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.8,
    "likes_acoustic": False,
    "preferred_decade": 2020,
    "preferred_mood_tag": "euphoric",
}

FAKE_SONGS = [
    {
        "id": i, "title": f"Song {i}", "artist": f"Artist {i % 3}",
        "genre": "pop", "mood": "happy", "energy": 0.8,
        "tempo_bpm": 120, "valence": 0.9, "danceability": 0.8,
        "acousticness": 0.2, "popularity": 70,
        "release_decade": 2020, "mood_tag": "euphoric",
    }
    for i in range(1, 12)
]

FAKE_VECTOR = [0.1] * 384
FAKE_EXPLANATIONS = ["Great match"] * 5


def _all_mocked(extra_patches=None):
    patches = {
        "server.app.validate_preferences": [],
        "server.app.embed_preferences": FAKE_VECTOR,
        "server.app.search_songs": FAKE_SONGS,
        "server.app.mmr_rerank": [(s, 5.0, "genre match") for s in FAKE_SONGS[:10]],
        "server.app.generate_explanations": FAKE_EXPLANATIONS,
    }
    if extra_patches:
        patches.update(extra_patches)
    return patches


# ── Layer 1: Basic endpoints (no external calls) ─────────────────────────────

def test_health_returns_ok():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_random_profile_has_required_keys():
    res = client.get("/random-profile")
    assert res.status_code == 200
    data = res.json()
    for key in ("genre", "mood", "energy", "likes_acoustic", "preferred_decade", "preferred_mood_tag"):
        assert key in data


def test_random_profile_energy_in_range():
    res = client.get("/random-profile")
    energy = res.json()["energy"]
    assert 0.0 <= energy <= 1.0


# ── Layer 2: _run_pipeline logic ─────────────────────────────────────────────

def test_pipeline_happy_path_returns_results_and_warnings():
    p = _all_mocked()
    with patch("server.app.validate_preferences", return_value=p["server.app.validate_preferences"]), \
         patch("server.app.embed_preferences", return_value=p["server.app.embed_preferences"]), \
         patch("server.app.search_songs", return_value=p["server.app.search_songs"]), \
         patch("server.app.mmr_rerank", return_value=p["server.app.mmr_rerank"]), \
         patch("server.app.generate_explanations", return_value=p["server.app.generate_explanations"]):
        result = _run_pipeline(FAKE_PREFS)

    assert "results" in result
    assert "warnings" in result
    assert len(result["results"]) > 0


def test_pipeline_top5_get_ai_explanations():
    p = _all_mocked()
    with patch("server.app.validate_preferences", return_value=[]), \
         patch("server.app.embed_preferences", return_value=FAKE_VECTOR), \
         patch("server.app.search_songs", return_value=FAKE_SONGS), \
         patch("server.app.mmr_rerank", return_value=p["server.app.mmr_rerank"]), \
         patch("server.app.generate_explanations", return_value=FAKE_EXPLANATIONS):
        result = _run_pipeline(FAKE_PREFS)

    for r in result["results"][:5]:
        assert r["explanation"] == "Great match"


def test_pipeline_results_6_to_10_get_rule_based_explanation():
    p = _all_mocked()
    with patch("server.app.validate_preferences", return_value=[]), \
         patch("server.app.embed_preferences", return_value=FAKE_VECTOR), \
         patch("server.app.search_songs", return_value=FAKE_SONGS), \
         patch("server.app.mmr_rerank", return_value=p["server.app.mmr_rerank"]), \
         patch("server.app.generate_explanations", return_value=FAKE_EXPLANATIONS):
        result = _run_pipeline(FAKE_PREFS)

    for r in result["results"][5:]:
        assert r["explanation"] == r["reasons"]


def test_pipeline_qdrant_down_falls_back_to_json_catalog():
    with patch("server.app.validate_preferences", return_value=[]), \
         patch("server.app.embed_preferences", side_effect=Exception("Qdrant down")), \
         patch("server.app.get_songs", return_value=FAKE_SONGS), \
         patch("server.app.generate_explanations", return_value=FAKE_EXPLANATIONS):
        result = _run_pipeline(FAKE_PREFS)

    assert "results" in result


def test_pipeline_mmr_failure_falls_back_to_diversity_filter():
    with patch("server.app.validate_preferences", return_value=[]), \
         patch("server.app.embed_preferences", return_value=FAKE_VECTOR), \
         patch("server.app.search_songs", return_value=FAKE_SONGS), \
         patch("server.app.mmr_rerank", side_effect=Exception("MMR failed")), \
         patch("server.app.generate_explanations", return_value=FAKE_EXPLANATIONS):
        result = _run_pipeline(FAKE_PREFS)

    assert "results" in result


def test_pipeline_surfaces_guardrail_warnings():
    warning_msg = "Classical + high energy: only 1 classical song in catalog."
    with patch("server.app.validate_preferences", return_value=[warning_msg]), \
         patch("server.app.embed_preferences", return_value=FAKE_VECTOR), \
         patch("server.app.search_songs", return_value=FAKE_SONGS), \
         patch("server.app.mmr_rerank", return_value=[(s, 5.0, "genre match") for s in FAKE_SONGS[:10]]), \
         patch("server.app.generate_explanations", return_value=FAKE_EXPLANATIONS):
        result = _run_pipeline({**FAKE_PREFS, "genre": "classical", "energy": 0.9})

    assert warning_msg in result["warnings"]


# ── Layer 3: Endpoints that call Gemini ──────────────────────────────────────

def test_from_text_success():
    p = _all_mocked()
    with patch("server.app.parse_preferences", return_value=FAKE_PREFS), \
         patch("server.app.validate_preferences", return_value=[]), \
         patch("server.app.embed_preferences", return_value=FAKE_VECTOR), \
         patch("server.app.search_songs", return_value=FAKE_SONGS), \
         patch("server.app.mmr_rerank", return_value=p["server.app.mmr_rerank"]), \
         patch("server.app.generate_explanations", return_value=FAKE_EXPLANATIONS):
        res = client.post("/recommend/from-text", json={"query": "upbeat pop for my morning run"})

    assert res.status_code == 200
    assert "results" in res.json()


def test_from_text_gemini_failure_returns_422():
    with patch("server.app.parse_preferences", side_effect=ValueError("bad JSON from Gemini")):
        res = client.post("/recommend/from-text", json={"query": "something"})

    assert res.status_code == 422


def test_from_songs_success():
    p = _all_mocked()
    with patch("server.app.analyze_songs", return_value=FAKE_PREFS), \
         patch("server.app.validate_preferences", return_value=[]), \
         patch("server.app.embed_preferences", return_value=FAKE_VECTOR), \
         patch("server.app.search_songs", return_value=FAKE_SONGS), \
         patch("server.app.mmr_rerank", return_value=p["server.app.mmr_rerank"]), \
         patch("server.app.generate_explanations", return_value=FAKE_EXPLANATIONS):
        res = client.post("/recommend/from-songs", json={"songs": ["Blinding Lights", "Levitating"]})

    assert res.status_code == 200
    assert "results" in res.json()


def test_from_songs_empty_list_returns_422():
    res = client.post("/recommend/from-songs", json={"songs": []})
    assert res.status_code == 422


def test_from_profile_skips_gemini():
    p = _all_mocked()
    with patch("server.app.validate_preferences", return_value=[]), \
         patch("server.app.embed_preferences", return_value=FAKE_VECTOR), \
         patch("server.app.search_songs", return_value=FAKE_SONGS), \
         patch("server.app.mmr_rerank", return_value=p["server.app.mmr_rerank"]), \
         patch("server.app.generate_explanations", return_value=FAKE_EXPLANATIONS), \
         patch("server.app.parse_preferences", side_effect=Exception("should not be called")) as mock_parse:
        res = client.post("/recommend/from-profile", json={"profile": FAKE_PREFS})

    assert res.status_code == 200
    mock_parse.assert_not_called()


def test_retry_returns_diff():
    adjusted = {"new_prefs": {**FAKE_PREFS, "energy": 0.4}, "diff": {"energy": [0.8, 0.4]}}
    p = _all_mocked()
    with patch("server.app.adjust_preferences", return_value=adjusted), \
         patch("server.app.validate_preferences", return_value=[]), \
         patch("server.app.embed_preferences", return_value=FAKE_VECTOR), \
         patch("server.app.search_songs", return_value=FAKE_SONGS), \
         patch("server.app.mmr_rerank", return_value=p["server.app.mmr_rerank"]), \
         patch("server.app.generate_explanations", return_value=FAKE_EXPLANATIONS):
        res = client.post("/recommend/retry", json={
            "original_query": "upbeat pop",
            "feedback": "too energetic",
            "previous_prefs": FAKE_PREFS,
        })

    data = res.json()
    assert res.status_code == 200
    assert data["diff"] == {"energy": [0.8, 0.4]}


def test_retry_gemini_failure_returns_422():
    with patch("server.app.adjust_preferences", side_effect=Exception("Gemini error")):
        res = client.post("/recommend/retry", json={
            "original_query": "upbeat pop",
            "feedback": "too loud",
            "previous_prefs": FAKE_PREFS,
        })

    assert res.status_code == 422


def test_recommend_with_query_calls_synthesize():
    p = _all_mocked()
    with patch("server.app.synthesize_inputs", return_value=FAKE_PREFS) as mock_synth, \
         patch("server.app.validate_preferences", return_value=[]), \
         patch("server.app.embed_preferences", return_value=FAKE_VECTOR), \
         patch("server.app.search_songs", return_value=FAKE_SONGS), \
         patch("server.app.mmr_rerank", return_value=p["server.app.mmr_rerank"]), \
         patch("server.app.generate_explanations", return_value=FAKE_EXPLANATIONS):
        res = client.post("/recommend", json={
            "profile": FAKE_PREFS,
            "query": "something chill for tonight",
        })

    assert res.status_code == 200
    mock_synth.assert_called_once()


def test_recommend_without_addons_skips_synthesize():
    p = _all_mocked()
    with patch("server.app.synthesize_inputs", side_effect=Exception("should not be called")) as mock_synth, \
         patch("server.app.validate_preferences", return_value=[]), \
         patch("server.app.embed_preferences", return_value=FAKE_VECTOR), \
         patch("server.app.search_songs", return_value=FAKE_SONGS), \
         patch("server.app.mmr_rerank", return_value=p["server.app.mmr_rerank"]), \
         patch("server.app.generate_explanations", return_value=FAKE_EXPLANATIONS):
        res = client.post("/recommend", json={"profile": FAKE_PREFS})

    assert res.status_code == 200
    mock_synth.assert_not_called()
