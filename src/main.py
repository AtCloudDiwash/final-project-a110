"""
Command line runner for the Music Recommender Simulation.
"""

from .recommender import load_songs, recommend_songs
from tabulate import tabulate

# Challenge 2: change this to switch scoring strategies
# options: balanced, genre_first, mood_first, energy_focused
SCORING_MODE = "balanced"

# Challenge 3: set to False to disable diversity filtering
DIVERSITY = True

PROFILES = [
    {
        "name": "High-Energy Pop",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "likes_acoustic": False,
        "preferred_decade": 2020,
        "preferred_mood_tag": "euphoric",
    },
    {
        "name": "Chill Lofi",
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.38,
        "likes_acoustic": True,
        "preferred_decade": 2020,
        "preferred_mood_tag": "peaceful",
    },
    {
        "name": "Deep Intense Rock",
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "likes_acoustic": False,
        "preferred_decade": 2010,
        "preferred_mood_tag": "aggressive",
    },
    {
        "name": "Edge Case - Classical Fan Who Wants High Energy",
        "genre": "classical",
        "mood": "intense",
        "energy": 0.90,
        "likes_acoustic": True,
        "preferred_decade": 1990,
        "preferred_mood_tag": "peaceful",
    },
]


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.")
    print(f"Scoring mode: {SCORING_MODE} | Diversity filter: {'on' if DIVERSITY else 'off'}\n")

    for profile in PROFILES:
        name = profile["name"]
        user_prefs = {k: v for k, v in profile.items() if k != "name"}

        print(f"=== Profile: {name} ===")
        recommendations = recommend_songs(user_prefs, songs, k=5, mode=SCORING_MODE, diversity=DIVERSITY)

        table = []
        for i, (song, score, explanation) in enumerate(recommendations, start=1):
            table.append([i, song['title'], song['artist'], f"{score:.2f}", explanation])

        print(tabulate(table, headers=["#", "Title", "Artist", "Score", "Reasons"], tablefmt="rounded_outline"))
        print()


if __name__ == "__main__":
    main()
