# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Music Viber

---

## 2. Intended Use  

This system suggests up to 5 songs from an 18-song catalog based on a user's preferred genre, mood, energy, and acoustic taste. It is built for classroom exploration only and is not meant for real users or production use.

---

## 3. How the Model Works  

Every song gets a score based on how well it matches what the user said they want. Genre and mood are checked for an exact match and add a fixed number of points each. Energy is scored by closeness — the nearer a song's energy is to the user's target, the more points it gets. Acoustic feel, popularity, release decade, and mood tag each add smaller bonuses on top. All scores are added up, every song in the catalog is ranked from highest to lowest, and the top 5 are returned.

---

## 4. Data  

The catalog has 18 songs. The original starter file had 10, and 8 more were added to cover missing genres including hip-hop, r&b, classical, edm, country, folk, reggae, and metal. Each song has attributes for genre, mood, energy, tempo, valence, danceability, acousticness, popularity, release decade, and mood tag. The dataset is small and has no lyrics, no listening history, and no real user feedback behind any of the numbers.

---

## 5. Strengths  

The system works best when the user's preferred genre has multiple songs in the catalog, like lofi or pop. The lofi/chill profile produced the most accurate results because genre, mood, and energy all pointed at the same songs. Every recommendation also comes with a clear breakdown of exactly why it scored the way it did, which makes the system easy to understand and debug.

---

## 6. Limitations and Bias 

The system over-prioritizes genre because it carries the highest weight. A great folk song that perfectly matches a user's target energy and mood will almost always lose to a mediocre pop song for a user who listed pop as their favorite. This is a classic filter bubble — the system never suggests anything outside the stated genre unless the catalog runs out of genre matches entirely.

The catalog is also very small at 18 songs. Some genres like rock and classical only have one song each, which means users with those preferences get one genre match and then the rest of the list is just whatever has the closest energy. That does not feel like a real recommendation.

The energy scoring treats all gaps linearly, but a jump from 0.8 to 0.6 feels very different to a listener than a jump from 0.3 to 0.1. The math does not capture that. The acoustic preference weight (1.0) is so low compared to everything else that it rarely changes the ranking — acoustic vs. electronic preference is effectively ignored in practice.

Finally, the system has no memory. It cannot learn from skips, replays, or feedback. Every run produces the same output for the same profile, which means it cannot improve or adapt the way a real recommender would.

---

## 7. Evaluation  

Four user profiles were tested: High-Energy Pop (genre: pop, mood: happy, energy: 0.85), Chill Lofi (genre: lofi, mood: chill, energy: 0.38, likes_acoustic: True), Deep Intense Rock (genre: rock, mood: intense, energy: 0.92), and an edge case of a Classical fan who wants high energy (genre: classical, mood: intense, energy: 0.90, likes_acoustic: True).

The pop profile surfaced Sunrise City and Gym Hero at the top, which felt correct. The lofi profile correctly ranked Library Rain and Midnight Coding highest, and the acoustic preference bonus pushed the more acoustic songs up slightly. The rock profile was the weakest result — only one rock song exists in the catalog, so after Storm Runner the rest of the list was just whatever had energy closest to 0.92, which happened to be EDM and metal songs. That does not feel like a real rock recommendation.

The most interesting result was the edge case. A user who listed classical as their genre but wanted very high energy (0.90) got almost no benefit from the genre weight because Morning Sonata (the only classical song) has energy 0.18. The energy gap penalty was so large that Iron Storm, a metal song, ranked above it. This showed that the system cannot handle contradictory preferences — it just does math and picks the least-bad option.

A weight shift experiment was also run: energy weight was doubled from 2.0 to 4.0 and genre weight was halved from 3.0 to 1.5. The result was more diverse top-5 lists across all profiles and the edge case felt slightly less broken. This suggests that energy is probably a stronger predictor of musical taste than genre label alone.

---

## 8. Future Work  

Expanding the catalog to a few hundred songs would make a noticeable difference, especially for genres that currently have only one song. Adding tempo and valence to the scoring would also help since both affect how a song feels but are currently ignored. A feedback loop where skips and replays adjust the user's profile over time would bring the system much closer to how real recommenders actually work.

---

## 9. Personal Reflection  

The biggest thing I learned is how much a single weight value shapes the entire output. Halving the genre weight and doubling the energy weight visibly changed which songs surfaced, and it felt more accurate in most cases. It also made it clear how filter bubbles form — the system never takes a risk on something outside the stated preference, so a user who says "pop" will mostly get pop forever. Building this made Spotify's recommendations feel less like magic and more like a very large version of the same idea.
