import numpy as np
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



# Something suggested by AI to diversity the ranked list. Previously a deterministic count based diversity filter was used

def mmr_rerank(
    candidates: list[tuple],
    prefs_vector: list[float],
    k: int = 10,
    lam: float = 0.7,
) -> list[tuple]:
    """Maximum Marginal Relevance reranking.

    Picks k songs that balance relevance (weighted scorer) with diversity
    (low cosine similarity to already-selected songs). lam controls the
    tradeoff: 1.0 = pure relevance, 0.0 = pure diversity.
    """
    if len(candidates) <= k:
        return candidates

    # Batch-embed all candidates in one model call for speed
    texts = [_to_text(item[0]) for item in candidates]
    vecs = _model.encode(texts, convert_to_numpy=True)  # shape (n, 384)
    q = np.array(prefs_vector)

    # Normalise all vectors once
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    vecs_normed = vecs / norms

    q_norm = q / (np.linalg.norm(q) or 1.0)

    # Scale raw scorer scores to [0, 1] to use as relevance signal
    scores = np.array([item[1] for item in candidates])
    s_min, s_max = scores.min(), scores.max()
    rel = (scores - s_min) / (s_max - s_min) if s_max != s_min else np.ones(len(scores))

    selected: list[int] = []
    remaining = list(range(len(candidates)))

    for _ in range(min(k, len(candidates))):
        best_i, best_mmr = None, -float("inf")

        for i in remaining:
            relevance = lam * rel[i]
            if selected:
                # Max cosine sim to any already-selected song
                sims = vecs_normed[selected] @ vecs_normed[i]
                redundancy = float(sims.max())
            else:
                redundancy = 0.0
            mmr = relevance - (1 - lam) * redundancy
            if mmr > best_mmr:
                best_mmr = mmr
                best_i = i

        selected.append(best_i)
        remaining.remove(best_i)

    return [candidates[i] for i in selected]
