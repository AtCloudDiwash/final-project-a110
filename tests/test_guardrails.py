import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai.guardrails import validate_preferences


def test_classical_high_energy_warns():
    warnings = validate_preferences({"genre": "classical", "mood": "intense", "energy": 0.9, "likes_acoustic": False})
    assert any("classical" in w.lower() for w in warnings)


def test_acoustic_high_energy_warns():
    warnings = validate_preferences({"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": True})
    assert any("acoustic" in w.lower() for w in warnings)


def test_unknown_genre_warns():
    warnings = validate_preferences({"genre": "bluegrass", "mood": "chill", "energy": 0.4, "likes_acoustic": False})
    assert any("not in the catalog" in w for w in warnings)


def test_unknown_mood_warns():
    warnings = validate_preferences({"genre": "pop", "mood": "sad", "energy": 0.5, "likes_acoustic": False})
    assert any("mood" in w.lower() for w in warnings)


def test_valid_prefs_no_warnings():
    warnings = validate_preferences({
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.4,
        "likes_acoustic": True,
        "preferred_decade": 2020,
        "preferred_mood_tag": "peaceful",
    })
    assert warnings == []
