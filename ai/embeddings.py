from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")


def _to_text(d: dict) -> str:
    return (
        f"genre:{d.get('genre', '')} "
        f"mood:{d.get('mood', '')} "
        f"energy:{d.get('energy', 0.5)} "
        f"acoustic:{'yes' if d.get('likes_acoustic') or d.get('acousticness', 0) > 0.5 else 'no'} "
        f"decade:{d.get('preferred_decade', d.get('release_decade', ''))} "
        f"mood_tag:{d.get('preferred_mood_tag', d.get('mood_tag', ''))}"
    )


def embed_preferences(prefs: dict) -> list[float]:
    return _model.encode(_to_text(prefs)).tolist()


def embed_song(song: dict) -> list[float]:
    return _model.encode(_to_text(song)).tolist()
