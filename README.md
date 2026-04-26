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

<!-- Short explanation of how data flows through your system — user input → backend → AI layer → response -->

Step 1 :  User inputs the data
            - there are three types of input
                - User profile
                - User custom prompt
                - List of songs you have listened
Step 2:  Backend receives the input
            - Gemini takes data and builds a profile

Step 3:  Guardrails check

Step 4:  The profile is embedded

Step 5:  The vector embeddings is sent to VectorDB 

Step 6:  Recommender.py reranks the returned results from Vector Search

Step 7:  Re-ranks via MMR diversificatoin

Step 8:  Results returned. 

Step 9:  If given feedback, the system repeats.


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

## Sample Interactions

### Example 1 — Natural Language Input

**Input:**
```
<!-- paste the text input you gave the system -->
```

**AI Output:**
```
<!-- paste the recommendations and explanation the system returned -->
```

---

### Example 2 — Structured Profile Input

**Input:**
```json
{
  "genre": "",
  "mood": "",
  "energy": 0.0,
  "likes_acoustic": false
}
```

**AI Output:**
```
<!-- paste the recommendations and explanation the system returned -->
```

---

### Example 3 — Edge Case / Guardrail Triggered

**Input:**
```
<!-- paste an input that triggers a guardrail warning -->
```

**AI Output:**
```
<!-- paste the warning message and how the system handled it -->
```

---

## Design Decisions

<!-- Why you built it this way. Cover: LLM choice, vector DB choice, why you kept the original re-ranker, what you deferred and why -->

| Decision | Choice | Reason |
|---|---|---|
| LLM | Gemini | <!-- why --> |
| Vector DB | Qdrant | <!-- why --> |
| Re-ranker | `src/recommender.py` | <!-- why --> |
| Deferred | Spotify Audio Features API | Deprecated for new apps |

---

## Testing Summary

| Test File | What It Covers | Result |
|---|---|---|
| `tests/test_recommender.py` | Original scorer logic | <!-- PASS/FAIL --> |
| `tests/test_guardrails.py` | Edge case preference validation | <!-- PASS/FAIL --> |

**What worked:**

<!-- describe what performed well -->

**What didn't work:**

<!-- describe what fell short and why -->

**What you learned:**

<!-- key takeaway from testing -->

---

## Reflection

<!-- What this project taught you about AI and problem-solving. Be honest and specific — this is the section employers actually read. -->
