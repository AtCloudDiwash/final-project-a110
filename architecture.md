# System Architecture

## Component Overview

```mermaid
flowchart TD
    A([User]) --> B[Profile Sliders\ngenre · mood · energy · acoustic · decade · mood_tag]
    A --> C[Describe Add-on\nfree-text prompt]
    A --> D[Songs Add-on\nartist / song tags]

    B & C & D --> E{Add-ons active?}

    E -- Yes --> F[Gemini: synthesize_inputs\nblends all three into one prefs dict]
    E -- No --> G[Use profile dict directly]

    F --> H[Guardrails: validate_preferences\ncheck genre · mood · energy range]
    G --> H

    H -- warnings --> W[Warning banner in UI\nnon-blocking]
    H --> I[Embed: sentence-transformers\nall-MiniLM-L6-v2 → 384-dim vector]

    I --> J[(Qdrant Vector DB\npre-embedded song catalog)]
    J --> K[Top 50 candidate songs\ncosine similarity]

    K --> L[recommender.py\nweighted scorer · 4 modes]
    L --> M[Top 30 ranked songs]

    M --> N[MMR Reranker\nlambda=0.7]
    N --> O[Final 10 songs]

    O --> P[Gemini: generate_explanations\ntop 5 get AI sentences\npositions 6-10 get rule-based reasons]

    P --> Q[Results Panel\n10 songs · scores · explanations · warnings]

    Q --> R{Satisfied?}
    R -- Yes --> S([Done])
    R -- No --> T[FeedbackDialog\nfree-text complaint]

    T --> U[Gemini: adjust_preferences\noriginal query + feedback + prev prefs]
    U --> V[Updated prefs + diff]
    V --> H
```

## Data Flow

1. User submits profile + optional add-ons
2. Gemini synthesizes all inputs into one preference dict — skipped if no add-ons
3. Guardrails validate the dict and collect non-blocking warnings
4. sentence-transformers embeds the dict into a 384-dim vector
5. Qdrant returns top 50 semantically similar songs
6. recommender.py scores all 50, returns top 30
7. MMR reranker picks the final 10 balancing relevance and diversity
8. Gemini writes explanations for the top 5
9. Results returned to frontend with warnings and resolved prefs
10. If user rejects, Gemini adjusts the profile and pipeline reruns from step 3

## Components

| Component | File | Role |
|---|---|---|
| Input synthesis | `ai/gemini.py` | Blends profile + text + songs into prefs dict |
| Guardrails | `ai/guardrails.py` | Validates prefs, surfaces warnings |
| Embeddings + MMR | `ai/embeddings.py` | Encodes prefs/songs, MMR reranking |
| Vector search | `ai/qdrant_db.py` | ANN search over pre-embedded catalog |
| Scorer | `src/recommender.py` | Weighted re-rank of top 50 candidates |
| Explanations + Feedback | `ai/gemini.py` | AI explanations, preference adjustment |
| API | `server/app.py` | FastAPI — POST /recommend, /recommend/retry |
| Frontend | `client/src/` | React + Vite UI |
```
