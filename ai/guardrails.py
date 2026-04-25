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


def validate_preferences(prefs: dict) -> list[str]:
    warnings = []

    genre = prefs.get("genre", "")
    mood = prefs.get("mood", "")
    energy = prefs.get("energy", 0.5)
    likes_acoustic = prefs.get("likes_acoustic", False)

    if genre == "classical" and energy > 0.7:
        warnings.append(
            "Classical + high energy: only 1 classical song in catalog, results may be poor."
        )

    if likes_acoustic and energy > 0.8:
        warnings.append(
            "Acoustic + high energy conflict: most acoustic songs are low energy."
        )

    if genre not in KNOWN_GENRES:
        warnings.append(f"Genre '{genre}' is not in the catalog — results may be empty.")

    if mood not in KNOWN_MOODS:
        warnings.append(f"Mood '{mood}' may not match any songs directly.")

    if not (0.0 <= energy <= 1.0):
        warnings.append("Energy must be between 0.0 and 1.0.")

    return warnings
