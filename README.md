# Music Viber — AI-Powered Music Recommendation System

## Original Project

**Project Name:** Music Viber

<!-- 2-3 sentences: what it did, what its goals were, and what it could do -->

Music Viber was a music recommendation system that recommends music to the users based on their user profile. User profile contained some characteristics like genre score, mood, energy, and so on. Based on the user profile and the recommendation mode (like genre-first, balance, or mood-first recommendation) the uses to cross check every single song stored in a custom file, and giv it a score, rerank the list, diversity the list with deterministic algorithm to finally generate the recommendation.

The problem with the previous version was it alwasy generated the same recommendation if the profile was same, the algorithm to find the match was very general, it did not consider the relationship between different genres, and it didnot have a feedback system.

---

## Title & Summary

<!-- What the final project does and why it matters -->

Title: Music Viber AI a.k.a MVI


MVI is an advance AI-powered recommendation platform with feedback enabled. The user provides certain details by which the AI system generates a profile for that user. The generated profile is checked by guardrails. After the following. The profile is sent along with system prompt for a vector search where the qdrant vectorDB responds with semantically similar songs. The songs are reranked using deterministic algorithms with MMR diversification to generate the final list. Now, if the user is unsatisfied with the response it can give a feed and retry the generation.

The new version introduces reliable way to generate user profile, implements feedback system, uses more amount of user data and songs, and implements advance diversification techniques.


---

## Architecture Overview

![Architecture Diagram](assets/architecture.svg)

**Step 1 — User provides input (one of three forms or all three forms)**
- **Profile** — structured sliders: genre, mood, energy, acoustic preference, decade, mood tag
- **Custom prompt** — free text like *"something chill for a late night drive"*
- **Song list** — names of songs or artists they have been listening to

**Step 2 — Gemini parses the input into a structured preference profile**
- Free text → `parse_preferences()` extracts genre, mood, energy, and other fields
- Song list → `analyze_songs()` infers preferences from known artist/song characteristics
- Profile + extras → `synthesize_inputs()` merges the base profile with the additional context
- Output is always the same shape: a preference dict with 6 fields

**Step 3 — Guardrails validate the generated profile**
- Checks for known conflicts (e.g. classical + high energy, acoustic + high energy)
- Flags unknown genres or moods that won't match catalog entries
- Non-blocking — warnings are collected and returned alongside results, never refusing a request

**Step 4 — Preference profile is embedded into a vector**
- `embed_preferences()` converts the preference dict into a 384-dimensional vector using a local sentence-transformer model (`all-MiniLM-L6-v2`)
- No API call needed — the model runs locally

**Step 5 — Vector search retrieves the top 50 candidate songs from Qdrant**
- The preference vector is compared against pre-embedded song vectors in Qdrant using cosine similarity
- Returns the 50 most semantically similar songs as candidates
- If Qdrant is unavailable, the full JSON catalog is used as a fallback

**Step 6 — Candidate songs are scored by `recommend_songs()`**
- Each candidate is scored against the preference profile using weighted rules: genre, mood, energy proximity, acoustic preference, popularity, decade, and mood tag
- Four scoring modes available: `balanced`, `genre_first`, `mood_first`, `energy_focused`
- Returns a ranked list of 30, with diversity filter disabled so MMR has a wide pool to work with

**Step 7 — MMR reranking diversifies the final list**
- Maximum Marginal Relevance (MMR) picks the top 10 songs that balance relevance (high scorer score) with diversity (low similarity to already-selected songs)
- Controlled by `lam=0.7` — slightly favors relevance over diversity
- If MMR fails, falls back to the deterministic per-artist/per-genre diversity filter

**Step 8 — Gemini generates natural language explanations**
- Top 5 results get a one-sentence AI explanation: *why this song fits what you asked for*
- Results 6–10 get the rule-based reason string from the scorer (e.g. `genre match, energy proximity +1.84`)

**Step 9 — Results are returned to the frontend**
- Response includes: ranked song list, per-song explanations, guardrail warnings, and the resolved preference profile

**Step 10 — Feedback loop (optional)**
- If the user is unsatisfied, they submit feedback (e.g. *"too energetic"*)
- `adjust_preferences()` sends the original query, feedback, and current prefs to Gemini, which returns an updated profile and a diff showing what changed
- The pipeline reruns with the adjusted profile


---

## Project Structure

```
final-project-a110/
│
├── ── PROJECT 3  (original rule-based recommender — unchanged) ──────────────
│
├── src/
│   ├── recommender.py          # weighted scorer · 4 modes · diversity filter
│   └── main.py                 # original CLI entry point (no longer used)
│
├── data/
│   └── songs.csv               # original 18-song dataset
│
├── tests/
│   └── test_recommender.py     # unit tests for scorer and explain_recommendation
│
├── image/                      # screenshots from Project 3 submission
│
│
├── ── PROJECT 4  (AI layer · API · frontend — all new) ──────────────────────
│
├── ai/
│   ├── guardrails.py           # preference validation → warnings[]
│   ├── embeddings.py           # sentence-transformers wrapper + MMR reranker
│   ├── qdrant_db.py            # Qdrant vector search (local embedded or cloud)
│   └── gemini.py               # Gemini 2.5 Flash: synthesize · explain · adjust
│
├── server/
│   └── app.py                  # FastAPI: POST /recommend · /recommend/retry
│                               #          GET  /random-profile · /health
│
├── scripts/
│   └── build_index.py          # one-time: embeds songs.json → Qdrant index
│
├── data/
│   └── new_data/
│       └── songs.json          # 102-song dataset · 15 genres · 7 moods · 9 mood tags (and expanding)
│
├── client/                     # React + Vite frontend
│   └── src/
│       ├── App.jsx             # state management · submit · retry flow
│       ├── services/
│       │   └── api.js          # fetch wrappers for /recommend + /recommend/retry
│       └── components/
│           ├── Header.jsx
│           ├── InputPanel.jsx  # profile panel + optional add-ons (describe / songs)
│           ├── ResultsPanel.jsx# 10 song cards · score bars · AI explanations
│           └── FeedbackDialog.jsx # 👎 → free-text feedback → retry
│
├── tests/
│   ├── test_guardrails.py      # 5 guardrail edge-case tests
│   └── test_app.py             # FastAPI endpoint + pipeline tests (18 tests)
│
├── assets/
│   └── architecture.svg        # system architecture diagram
│
├── .env                        # GEMINI_API_KEY · QDRANT_URL · QDRANT_API_KEY
├── requirements.txt            # updated: fastapi · uvicorn · google-genai
│                               #          qdrant-client · sentence-transformers
└── tech_stack.md
```

> `src/recommender.py` is the only Project 3 file that Project 4 actively calls.
> It acts as Stage 2 of the pipeline — re-ranking the top-30 candidates returned by Qdrant.

---

## Setup Instructions

### Prerequisites

<!-- List anything that needs to be installed first (Python version, Node, Docker, etc.) -->

### Backend

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
.venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and fill in your environment variables
cp .env.example .env

# 4. Build the Qdrant vector index
python scripts/build_index.py  # This is important step

# 5. Open another tab in the terminal and Start the backend server 
uvicorn server.app:app --reload

# Alternative — no activation needed (use full path to .venv's uvicorn)
.venv/bin/uvicorn server.app:app --reload        # Mac/Linux
.venv\Scripts\uvicorn server.app:app --reload    # Windows
```

### Frontend

```bash
cd client
npm install
npm run dev
```

The app will be available at `http://localhost:5173`. The API runs on `http://localhost:8000`.

---

## Video Demo

| Part | Link |
|---|---|
| Part 1 — Overview & Setup | [Watch on Loom](https://www.loom.com/share/cccd4abcf74d487e987b85fd2310ab80) |
| Part 2 — Features & Feedback Loop | [Watch on Loom](https://www.loom.com/share/7908f5a14cd74884b1dcf1000e060d45) |

---

## Sample Interactions

### Example 1 — Natural Language Description Add-on

Profile set to lofi / chill / energy 0.3, then the **"Describe what you want"** add-on is toggled on.

**Input:**
```
Something calm and dreamy to study to late at night — no lyrics, just atmosphere.
```

Gemini synthesizes the add-on text with the base profile and refines it:

**Resolved preference profile:**
```json
{
  "genre": "lofi",
  "mood": "chill",
  "energy": 0.25,
  "likes_acoustic": true,
  "preferred_decade": null,
  "preferred_mood_tag": "dreamy"
}
```

**Top 3 results (with AI explanations):**
```
#1  Rainfall Study Session – Cozy Beats Co.   [lofi]  score 9.4
    ✦ Gentle rain textures and slow tempo match your late-night, no-distraction vibe perfectly.

#2  Midnight Pages – Lo-fi Cafe               [lofi]  score 8.9
    ✦ Soft piano loops with dreamy pads are ideal for deep focus without lyrics pulling attention.

#3  Floating Thoughts – ChillHop Collective   [ambient]  score 8.1
    ✦ Ambient drones and minimal percussion create exactly the atmospheric, no-lyric study space you described.
```

---

### Example 2 — Structured Profile Input Only (no add-ons)

No add-ons active — Gemini is skipped entirely, profile goes straight into the pipeline.

**Input profile:**
```json
{
  "genre": "synthwave",
  "mood": "focused",
  "energy": 0.75,
  "likes_acoustic": false,
  "preferred_decade": 1980,
  "preferred_mood_tag": "energetic"
}
```

**Top 3 results:**
```
#1  Neon Grid – Retrowave Drive               [synthwave]  score 10.2
    ✦ Heavy synth arpeggios and 80s production style hit every point of your profile.

#2  Chrome and Circuits – Digital Horizon     [synthwave]  score 9.6
    ✦ Driving bassline and retro-futuristic pads match your high-energy, focused 80s preference.

#3  Laser Highway – Synth City                [edm]  score 7.8
    ✦ High-BPM energy and electronic texture keep momentum even though it drifts slightly from pure synthwave.
```

---

### Example 3 — Guardrail Triggered

Profile submitted with `genre: classical` and `energy: 0.9`.

**Input profile:**
```json
{
  "genre": "classical",
  "mood": "intense",
  "energy": 0.9,
  "likes_acoustic": true,
  "preferred_decade": null,
  "preferred_mood_tag": null
}
```

**Response — warnings banner shown in UI:**
```
⚠  Classical + high energy: only 1 classical song in catalog, results may be poor.
⚠  Acoustic + high energy conflict: most acoustic songs are low energy.
```

The system still returns results — it does not block. The top result is the single classical track in the catalog; remaining slots are filled by the next-closest matches (ambient, folk) since no other classical songs exist.

---

### Example 4 — Feedback Loop (Retry)

Initial request returns rock / intense results. User clicks **👎 Not Satisfied** and types feedback.

**Initial profile:**
```json
{
  "genre": "rock",
  "mood": "intense",
  "energy": 0.85,
  "likes_acoustic": false,
  "preferred_decade": 2010,
  "preferred_mood_tag": "aggressive"
}
```

**User feedback:**
```
These are too aggressive and loud. I want something intense but more melodic — like rock but with emotion.
```

Gemini runs `adjust_preferences()` and returns an updated profile with a diff:

**Adjusted profile + diff banner shown in UI:**
```
🔄 Adjusted:  mood_tag: aggressive → melancholic   energy: 0.85 → 0.65   mood: intense → moody
```

```json
{
  "genre": "rock",
  "mood": "moody",
  "energy": 0.65,
  "likes_acoustic": false,
  "preferred_decade": 2010,
  "preferred_mood_tag": "melancholic"
}
```

**New top 3 results:**
```
#1  The Weight of Wings – Atlas Sound         [rock]  score 9.1
    ✦ Emotional guitar work and moody dynamics match your shift toward melodic intensity.

#2  Broken Frequencies – Hollow Ground        [indie pop]  score 8.4
    ✦ Slower, textured rock with melancholic vocals fits the emotional but not aggressive direction.

#3  Glass Roads – The Still                   [rock]  score 8.0
    ✦ Mid-tempo rock with strong melodic hooks — intense without being abrasive.
```

---

## Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| LLM | Gemini 2.5 Flash | Free tier with generous quota, reliable JSON-mode output, and the `google-genai` SDK makes multi-turn structured calls straightforward. Flash specifically was chosen over Pro because latency matters more than raw capability for preference parsing — the tasks (parse, synthesize, explain, adjust) are all short structured outputs, not complex reasoning. |
| Vector DB | Qdrant | Runs fully local via `QdrantClient(path=...)` with no Docker dependency — critical for a dev environment. Also supports a hosted cloud cluster by just swapping `QDRANT_URL` in `.env`, so scaling requires zero code changes. |
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers) | 384-dim vectors, ~80 MB, runs on CPU in under 50ms per batch. No API key needed, no cost per call. The vector space is consistent for both songs and preference queries since both go through the same `_to_text()` serialization before encoding. |
| Diversity | MMR over hard caps | The original hard cap (max 2 per genre) punished users who explicitly asked for a specific genre — if you want lofi, you should be able to get 4 lofi songs if they are all genuinely different. MMR solves this by penalizing semantic similarity rather than label repetition, so two near-identical lofi tracks get penalized while a lofi track with a different energy profile gets through. |
| Re-ranker | `src/recommender.py` (Project 3) | The weighted scorer gives precise, explainable control over what matters most per request (scoring modes). Pure vector similarity alone would lose the ability to say "give me this exact mood and energy level." Keeping the scorer as Stage 2 means the system combines semantic retrieval (Qdrant) with rule-based precision (scorer) — each doing what it is best at. |
| Feedback cap | 1 retry only | Allowing unlimited retries leads to prompt drift — each round Gemini adjusts based on the previous adjustment, not the original intent, and the profile can end up far from what the user actually wanted. One retry is enough to course-correct without losing the original signal. |
| Deferred | Spotify Audio Features API | The `/audio-features` endpoint was deprecated for new app registrations in late 2024. Using it would block any new developer trying to run the project. The 102-song `songs.json` dataset was built manually with equivalent fields (`energy`, `valence`, `danceability`, `acousticness`, `tempo`) so the pipeline works identically. |

---

## Testing Summary

MVI uses three layers of tests that mirror the architecture of the system.

### Layer 1 — Routing Tests
Basic endpoint checks with no external dependencies. Verifies that `/health`
returns `200`, `/random-profile` returns all required keys, and that energy
values stay within the valid `0.0–1.0` range. These run instantly and require
no API keys or environment setup.

### Layer 2 — Pipeline Tests (`_run_pipeline`)
Tests the core logic of the system with all external services mocked
(Gemini, Qdrant, sentence-transformers). Each test patches only what it
needs and lets the real `recommend_songs` and `mmr_rerank` run. This layer
covers:

- **Happy path** — full flow returns `results` and `warnings`
- **Top 5 explanations** — Gemini-generated sentences appear on results 1–5
- **Results 6–10** — fall back to rule-based reasons from the scorer
- **Qdrant down** — if embedding or vector search crashes, the system falls
  back to the full JSON catalog without returning an error
- **MMR failure** — if MMR reranking crashes, the system falls back to the
  deterministic diversity filter in `recommend_songs`
- **Guardrail warnings** — warnings from `validate_preferences` are
  surfaced in the response, not swallowed

### Layer 3 — Endpoint + Gemini Tests
Tests each of the five API endpoints through FastAPI's `TestClient`, with
Gemini mocked at the `server.app` import level. Covers:

- `/recommend/from-text` — Gemini parses the query; crashes return `422`
- `/recommend/from-songs` — Gemini infers preferences from song names; empty
  list returns `422`
- `/recommend/from-profile` — skips Gemini entirely; confirmed via
  `assert_not_called()`
- `/recommend/retry` — `adjust_preferences` result is passed back as `diff`
  in the response
- `/recommend` — calls `synthesize_inputs` only when a query or song list is
  present; skips it for plain profile requests

### Test Files

| File | What It Covers |
|---|---|
| `tests/test_recommender.py` | Original scorer: sorting, scoring modes, diversity filter |
| `tests/test_guardrails.py` | Preference validation edge cases |
| `tests/test_app.py` | All three layers above (18 tests) |

### Running the Tests

Make sure your virtual environment is active and dependencies are installed first.

```bash
# Run all tests
pytest

# Run only the new AI pipeline tests
pytest tests/test_app.py

# Run with verbose output (shows each test name)
pytest tests/test_app.py -v

# Run a single specific test
pytest tests/test_app.py::test_health_returns_ok

# Stop at the first failure
pytest tests/test_app.py -x
```

> No API keys required — all external services (Gemini, Qdrant, embeddings) are mocked in `test_app.py`.
---

## Guardrails

MVI validates every generated preference profile before it reaches the vector
search. The guardrail layer runs after Gemini parses the user's input and
before the embedding is created. It is non-blocking — warnings are collected
and returned to the frontend alongside the results, so the system never
refuses a request.

### What is checked

| Check | Condition | Warning returned |
|---|---|---|
| Classical + high energy | `genre == "classical"` and `energy > 0.7` | Only 1 classical song in catalog, results may be poor |
| Acoustic + high energy conflict | `likes_acoustic == True` and `energy > 0.8` | Most acoustic songs are low energy, results may conflict |
| Unknown genre | `genre` not in the 15 known genres | Genre not in catalog, results may be empty |
| Unknown mood | `mood` not in the 7 known moods | Mood may not match any songs directly |
| Energy out of range | `energy` outside `0.0–1.0` | Energy must be between 0.0 and 1.0 |

### Known genres
`pop`, `lofi`, `rock`, `ambient`, `jazz`, `synthwave`, `indie pop`,
`hip-hop`, `r&b`, `classical`, `edm`, `country`, `folk`, `reggae`, `metal`

### Known moods
`happy`, `chill`, `intense`, `relaxed`, `focused`, `moody`, `calm`

### Why non-blocking
A blocking guardrail would refuse requests when Gemini picks a valid-sounding
but slightly off value. Since the catalog is small (edge cases like classical
or metal only have a handful of songs), it is more useful to warn the user
and show imperfect results than to return nothing.


---

## Reflection

<!-- What this project taught you about AI and problem-solving. Be honest and specific — this is the section employers actually read. -->
