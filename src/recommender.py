from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import csv

# Challenge 2: scoring mode weight sets
SCORING_MODES = {
    "balanced": {
        "genre": 1.5, "mood": 2.0, "energy": 4.0, "acoustic": 1.0,
        "popularity": 0.5, "decade": 1.0, "mood_tag": 1.5,
    },
    "genre_first": {
        "genre": 5.0, "mood": 1.0, "energy": 1.5, "acoustic": 0.5,
        "popularity": 0.3, "decade": 0.5, "mood_tag": 0.7,
    },
    "mood_first": {
        "genre": 1.0, "mood": 5.0, "energy": 1.5, "acoustic": 0.5,
        "popularity": 0.3, "decade": 0.5, "mood_tag": 2.0,
    },
    "energy_focused": {
        "genre": 0.8, "mood": 1.0, "energy": 6.0, "acoustic": 0.5,
        "popularity": 0.3, "decade": 0.5, "mood_tag": 0.7,
    },
}


@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2020
    mood_tag: str = "unknown"


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    preferred_decade: Optional[int] = None
    preferred_mood_tag: Optional[str] = None


class Recommender:
    """OOP implementation of the recommendation logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5, mode: str = "balanced", diversity: bool = True) -> List[Song]:
        """Returns top k songs sorted by weighted score, with optional diversity filtering."""
        weights = SCORING_MODES.get(mode, SCORING_MODES["balanced"])

        def song_score(song: Song) -> float:
            score = 0.0
            if song.genre == user.favorite_genre:
                score += weights["genre"]
            if song.mood == user.favorite_mood:
                score += weights["mood"]
            score += weights["energy"] * (1 - abs(user.target_energy - song.energy))
            acoustic_pref = 0.8 if user.likes_acoustic else 0.2
            score += weights["acoustic"] * (1 - abs(acoustic_pref - song.acousticness))
            score += weights["popularity"] * (song.popularity / 100)
            if user.preferred_decade and song.release_decade == user.preferred_decade:
                score += weights["decade"]
            if user.preferred_mood_tag and song.mood_tag == user.preferred_mood_tag:
                score += weights["mood_tag"]
            return score

        ranked = sorted(self.songs, key=song_score, reverse=True)

        if diversity:
            ranked = self._apply_diversity(ranked)

        return ranked[:k]

    def _apply_diversity(self, songs: List[Song], max_per_artist: int = 2, max_per_genre: int = 2) -> List[Song]:
        """Filters a ranked list to limit songs per artist and genre."""
        artist_counts: Dict[str, int] = {}
        genre_counts: Dict[str, int] = {}
        result = []
        for song in songs:
            a = artist_counts.get(song.artist, 0)
            g = genre_counts.get(song.genre, 0)
            if a < max_per_artist and g < max_per_genre:
                result.append(song)
                artist_counts[song.artist] = a + 1
                genre_counts[song.genre] = g + 1
        return result

    def explain_recommendation(self, user: UserProfile, song: Song, mode: str = "balanced") -> str:
        """Returns a plain-language explanation of why a song matched the user profile."""
        weights = SCORING_MODES.get(mode, SCORING_MODES["balanced"])
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f'genre match (+{weights["genre"]})')
        if song.mood == user.favorite_mood:
            reasons.append(f'mood match (+{weights["mood"]})')
        energy_score = weights["energy"] * (1 - abs(user.target_energy - song.energy))
        reasons.append(f'energy proximity (+{energy_score:.2f})')
        acoustic_pref = 0.8 if user.likes_acoustic else 0.2
        acoustic_score = weights["acoustic"] * (1 - abs(acoustic_pref - song.acousticness))
        reasons.append(f'acoustic match (+{acoustic_score:.2f})')
        pop_score = weights["popularity"] * (song.popularity / 100)
        reasons.append(f'popularity (+{pop_score:.2f})')
        if user.preferred_decade and song.release_decade == user.preferred_decade:
            reasons.append(f'decade match (+{weights["decade"]})')
        if user.preferred_mood_tag and song.mood_tag == user.preferred_mood_tag:
            reasons.append(f'mood tag match (+{weights["mood_tag"]})')
        return ', '.join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file and returns a list of dicts with typed numeric values."""
    songs = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['id'] = int(row['id'])
            row['energy'] = float(row['energy'])
            row['tempo_bpm'] = float(row['tempo_bpm'])
            row['valence'] = float(row['valence'])
            row['danceability'] = float(row['danceability'])
            row['acousticness'] = float(row['acousticness'])
            row['popularity'] = int(row['popularity'])
            row['release_decade'] = int(row['release_decade'])
            songs.append(row)
    return songs


def apply_diversity_filter(results: List[Tuple], max_per_artist: int = 2, max_per_genre: int = 2) -> List[Tuple]:
    """Filters scored results to limit representation per artist and genre."""
    artist_counts: Dict[str, int] = {}
    genre_counts: Dict[str, int] = {}
    filtered = []
    for item in results:
        song = item[0]
        a = artist_counts.get(song['artist'], 0)
        g = genre_counts.get(song['genre'], 0)
        if a < max_per_artist and g < max_per_genre:
            filtered.append(item)
            artist_counts[song['artist']] = a + 1
            genre_counts[song['genre']] = g + 1
    return filtered


def score_song(user_prefs: Dict, song: Dict, mode: str = "balanced") -> Tuple[float, List[str]]:
    """Scores one song against user preferences using the specified scoring mode."""
    weights = SCORING_MODES.get(mode, SCORING_MODES["balanced"])
    score = 0.0
    reasons = []

    if song['genre'] == user_prefs.get('genre'):
        score += weights["genre"]
        reasons.append(f'genre match (+{weights["genre"]})')

    if song['mood'] == user_prefs.get('mood'):
        score += weights["mood"]
        reasons.append(f'mood match (+{weights["mood"]})')

    target_energy = user_prefs.get('energy', 0.5)
    energy_score = weights["energy"] * (1 - abs(target_energy - song['energy']))
    score += energy_score
    reasons.append(f'energy proximity (+{energy_score:.2f})')

    likes_acoustic = user_prefs.get('likes_acoustic', False)
    acoustic_pref = 0.8 if likes_acoustic else 0.2
    acoustic_score = weights["acoustic"] * (1 - abs(acoustic_pref - song['acousticness']))
    score += acoustic_score
    reasons.append(f'acoustic match (+{acoustic_score:.2f})')

    pop_score = weights["popularity"] * (song.get('popularity', 50) / 100)
    score += pop_score
    reasons.append(f'popularity (+{pop_score:.2f})')

    preferred_decade = user_prefs.get('preferred_decade')
    if preferred_decade and song.get('release_decade') == preferred_decade:
        score += weights["decade"]
        reasons.append(f'decade match (+{weights["decade"]})')

    preferred_mood_tag = user_prefs.get('preferred_mood_tag')
    if preferred_mood_tag and song.get('mood_tag') == preferred_mood_tag:
        score += weights["mood_tag"]
        reasons.append(f'mood tag match (+{weights["mood_tag"]})')

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, mode: str = "balanced", diversity: bool = True) -> List[Tuple[Dict, float, str]]:
    """Scores all songs, applies optional diversity filter, and returns top k with explanations."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        scored.append((song, score, ', '.join(reasons)))

    scored = sorted(scored, key=lambda x: x[1], reverse=True)

    if diversity:
        scored = apply_diversity_filter(scored)

    return scored[:k]
