"""
Command line runner for the Music Recommender Simulation.
"""

from .recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")

    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    }

    print("User profile:")
    for key, val in user_prefs.items():
        print(f"  {key}: {val}")

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    print(f"{'#':<3} {'Title':<25} {'Artist':<20} {'Score':<7} Reasons")
    print("-" * 90)
    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{i:<3} {song['title']:<25} {song['artist']:<20} {score:<7.2f} {explanation}")


if __name__ == "__main__":
    main()
