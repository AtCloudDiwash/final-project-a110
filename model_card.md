# Model Card: Music Viber AI (MVI)

## 1. Model Name

Music Viber AI — MVI

---

## 2. Intended Use

MVI recommends music based on a user's taste profile, an optional free-text description, and an optional list of artists or songs they have been listening to. It is built as a Codepath capstone project and demonstrates how LLM-based preference parsing, vector search, and a deterministic re-ranker can be combined into a working recommendation pipeline. Not intended for production use.

---

## 3. How the Model Works

Input can arrive in three forms — a structured profile, a text description, a list of artists/songs — or any combination. When add-ons are present, Gemini synthesizes all inputs into one preference dict (`genre`, `mood`, `energy`, `likes_acoustic`, `preferred_decade`, `preferred_mood_tag`). That dict is validated by guardrails, converted to a 384-dim vector by a local sentence-transformer, and queried against a Qdrant vector index of pre-embedded songs. The top 50 candidate songs are re-ranked by a weighted scorer, then Maximum Marginal Relevance (MMR) selects the final 10 by balancing relevance with diversity. Gemini writes a one-sentence explanation for each of the top 5 results. If the user is not satisfied, they can submit free-text feedback; Gemini adjusts the preference profile and the pipeline reruns once.

---

## 4. Data

The catalog is 102 songs stored in `data/new_data/songs.json`. Each song has: `title`, `artist`, `genre` (15 genres), `mood` (7 moods), `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`, `popularity`, `release_decade`, and `mood_tag` (9 tags). The dataset was manually curated to ensure every genre, mood, and mood tag has multiple representatives so no preference hits a dead end. There are no real play counts, no user history, and no audio files — all numeric features are hand-assigned to reflect typical values for each genre.

---

## 5. Strengths

- **Flexible input:** the system handles a structured profile, a freeform prompt, or a song list — and blends all three when all are provided. Users who cannot describe their taste in sliders can describe it in words instead.
- **Semantic retrieval:** Qdrant finds songs that are close in the embedding space even when genre labels do not match exactly, which reduces the filter bubble effect of the original rule-based version.
- **Explainability:** every result comes with either a Gemini-written sentence or a rule-based breakdown of which scoring factors fired, so the user always knows why a song was returned.
- **Feedback loop:** one retry with free-text feedback is enough to meaningfully shift the results — the diff banner shows exactly what changed.
- **Relation between genres:** Previous implementation of this project did not consider relation between genres, which is improved in this system. Gemini is sytem prompted to consider the relation between genres, which also improves the diversity.

---

## 6. Limitations and Bias

- **Small catalog:** 102 songs is still small. For niche genres like reggae or classical, the top 10 list will exhaust the genre and fill remaining spots with close-but-not-matching alternatives.
- **Gemini output variability:** the same text prompt can produce slightly different preference profiles across runs because the LLM is non-deterministic. Guardrails catch hard errors but not subtle drift (e.g. `energy: 0.4` vs `energy: 0.45`).
- **Hand-assigned features:** all song attributes were manually set, not extracted from audio. The `energy` and `acousticness` values reflect assumptions about genre conventions, not measurements. A lofi song labeled `energy: 0.3` might feel more energetic to some listeners than the number implies.
- **One retry cap:** the feedback loop allows only one adjustment. If the retry is still wrong, the user has no further recourse except starting over.
- **No personalisation over time:** the system has no memory between sessions. It cannot learn from which songs a user skipped or replayed.

---

## 7. Evaluation

Four preference profiles were tested against the full pipeline:

| Profile | Expected top genre | Outcome |
|---|---|---|
| `lofi / chill / energy 0.3 / acoustic` | lofi | Top 5 all lofi or ambient; MMR introduced one folk entry at position 8 |
| `synthwave / focused / energy 0.75 / decade 1980` | synthwave | Top 4 synthwave; position 5 was EDM (only 4 synthwave songs in catalog) |
| `r&b / relaxed / energy 0.5 / melancholic` | r&b | Top 3 r&b, positions 4–6 indie pop (shared emotional register) |
| `classical / intense / energy 0.9` | classical | Guardrail warning fired; only 1 classical song exists so positions 2–10 were ambient and folk — the warning correctly told the user why |

The guardrail test confirmed that non-blocking warnings are more useful than hard rejections: the classical user still got results and understood why they were imperfect.

---

## 8. Future Work

- Expand the catalog to 1000+ songs using a Kaggle Spotify dataset and a conversion script
- Add a `λ` slider to the UI so users can control the relevance/diversity tradeoff in MMR directly
- Persist a lightweight session history (last 3 profiles) so the feedback loop can compare against the user's full session, not just the last request
- Add Last.fm tag enrichment for the song list add-on so Gemini has richer context when inferring from artist names

---

## 9. Personal Reflection

The most surprising thing was how much the two-stage pipeline (Qdrant → scorer) outperforms either stage alone. Qdrant alone returns semantically close songs but ignores the fine-grained scoring weights the user set. The scorer alone is fast but blind to relationships between genres. Together they complement each other — Qdrant narrows the field to plausible candidates and the scorer applies precise user preferences on top of that narrowed set.

The feedback loop also forced a design decision I had not anticipated: how many retries to allow. Unlimited retries cause the profile to drift further from the user's original intent with each round because Gemini adjusts based on the adjusted profile, not the original. Capping at one retry was the right call — it is enough to course-correct without losing the signal.
