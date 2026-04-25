import os
import json
from google import genai

_client = None
MODEL = "gemini-2.5-flash"

KNOWN_GENRES = [
    "pop", "lofi", "rock", "ambient", "jazz", "synthwave",
    "indie pop", "hip-hop", "r&b", "classical", "edm",
    "country", "folk", "reggae", "metal",
]
KNOWN_MOODS = ["happy", "chill", "intense", "relaxed", "focused", "moody", "calm"]
KNOWN_MOOD_TAGS = [
    "euphoric", "focused", "peaceful", "aggressive", "energetic",
    "dreamy", "nostalgic", "melancholic", "uplifting",
]

_PARSE_SYSTEM = f"""You are a music preference parser. Given a user's natural language description,
extract their music preferences and return ONLY a valid JSON object with these exact keys:
- genre: one of {KNOWN_GENRES}
- mood: one of {KNOWN_MOODS}
- energy: float between 0.0 (very calm) and 1.0 (very intense)
- likes_acoustic: boolean
- preferred_decade: integer like 1990, 2000, 2010, 2020, or null
- preferred_mood_tag: one of {KNOWN_MOOD_TAGS} or null

Return only the JSON object. No explanation, no markdown, no code blocks."""

_ANALYZE_SYSTEM = f"""You are a music analyst. Given a list of songs or artists the user has listened to,
infer their music preferences and return ONLY a valid JSON object with these exact keys:
- genre: one of {KNOWN_GENRES} (pick the most dominant)
- mood: one of {KNOWN_MOODS}
- energy: float between 0.0 (very calm) and 1.0 (very intense)
- likes_acoustic: boolean
- preferred_decade: integer like 1990, 2000, 2010, 2020, or null
- preferred_mood_tag: one of {KNOWN_MOOD_TAGS} or null

Use your knowledge of those artists/songs to determine these values accurately.
Return only the JSON object. No explanation, no markdown, no code blocks."""

_REQUIRED_KEYS = {"genre", "mood", "energy", "likes_acoustic", "preferred_decade", "preferred_mood_tag"}


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set.")
        _client = genai.Client(api_key=api_key)
    return _client


def _parse_json_response(raw: str) -> dict:
    try:
        data = json.loads(raw.strip())
    except json.JSONDecodeError:
        raise ValueError(f"Gemini returned non-JSON: {raw}")
    missing = _REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"Gemini response missing keys: {missing}")
    return data


def parse_preferences(user_input: str) -> dict:
    client = _get_client()
    response = client.models.generate_content(
        model=MODEL,
        contents=user_input,
        config={"system_instruction": _PARSE_SYSTEM},
    )
    return _parse_json_response(response.text)


def analyze_songs(song_names: list[str]) -> dict:
    client = _get_client()
    prompt = "Songs/artists I've been listening to: " + ", ".join(song_names)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"system_instruction": _ANALYZE_SYSTEM},
    )
    return _parse_json_response(response.text)


def generate_explanations(user_input: str, top3: list[dict]) -> list[str]:
    client = _get_client()
    songs_text = "\n".join(
        f"{i+1}. {s['song']['title']} by {s['song']['artist']} "
        f"(score: {s['score']:.2f}, reasons: {s['reasons']})"
        for i, s in enumerate(top3)
    )
    system = (
        "You are a music recommendation assistant. "
        "Given what the user wants and a list of recommended songs, "
        "write one short conversational sentence (max 20 words) explaining why each song fits. "
        "Return a JSON array of exactly 3 strings, one per song. No markdown, no code blocks."
    )
    prompt = f"User wants: {user_input}\n\nRecommended songs:\n{songs_text}"
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"system_instruction": system},
    )
    try:
        explanations = json.loads(response.text.strip())
        if isinstance(explanations, list) and len(explanations) >= 3:
            return [str(e) for e in explanations[:3]]
    except (json.JSONDecodeError, TypeError):
        pass
    return [s["reasons"] for s in top3]


def synthesize_inputs(
    profile: dict,
    query: str | None = None,
    songs: list[str] | None = None,
) -> dict:
    client = _get_client()
    parts = [f"User's base profile: {json.dumps(profile)}"]
    if query:
        parts.append(f"User's current request: {query}")
    if songs:
        parts.append(f"Songs/artists they've been listening to: {', '.join(songs)}")

    system = f"""You are a music preference synthesizer.
You receive a user's base music profile and optional extra context (a text description and/or songs they've heard).
The base profile reflects their general taste. The extra context reflects what they want right now.
Synthesize all available information into one refined preference object.
Return ONLY a valid JSON object with these exact keys:
- genre: one of {KNOWN_GENRES}
- mood: one of {KNOWN_MOODS}
- energy: float between 0.0 and 1.0
- likes_acoustic: boolean
- preferred_decade: integer like 1990, 2000, 2010, 2020, or null
- preferred_mood_tag: one of {KNOWN_MOOD_TAGS} or null

No explanation, no markdown, no code blocks."""

    response = client.models.generate_content(
        model=MODEL,
        contents="\n".join(parts),
        config={"system_instruction": system},
    )
    return _parse_json_response(response.text)


def adjust_preferences(
    original_query: str,
    feedback: str,
    previous_prefs: dict,
) -> dict:
    client = _get_client()
    system = f"""You are a music preference adjuster. The user was not satisfied with recommendations.
Given their original request, their feedback, and their current preference settings,
return ONLY a valid JSON object with two keys:
- new_prefs: updated preferences object with keys {list(_REQUIRED_KEYS)}
- diff: object showing only the fields that changed, each as [old_value, new_value]

No explanation, no markdown, no code blocks."""
    prompt = (
        f"Original request: {original_query}\n"
        f"Feedback: {feedback}\n"
        f"Current prefs: {json.dumps(previous_prefs)}"
    )
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"system_instruction": system},
    )
    try:
        data = json.loads(response.text.strip())
        if "new_prefs" in data:
            return data
    except (json.JSONDecodeError, TypeError):
        pass
    return {"new_prefs": previous_prefs, "diff": {}}
