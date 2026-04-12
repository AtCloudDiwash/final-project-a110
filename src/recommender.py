from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

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

@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """OOP implementation of the recommendation logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns top k songs sorted by weighted score against the user profile."""
        def song_score(song: Song) -> float:
            score = 0.0
            if song.genre == user.favorite_genre:
                score += 3.0
            if song.mood == user.favorite_mood:
                score += 2.0
            score += 2.0 * (1 - abs(user.target_energy - song.energy))
            acoustic_pref = 0.8 if user.likes_acoustic else 0.2
            score += 1.0 * (1 - abs(acoustic_pref - song.acousticness))
            return score
        return sorted(self.songs, key=song_score, reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a plain-language explanation of why a song matched the user profile."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append('genre match (+3.0)')
        if song.mood == user.favorite_mood:
            reasons.append('mood match (+2.0)')
        energy_score = 2.0 * (1 - abs(user.target_energy - song.energy))
        reasons.append(f'energy proximity (+{energy_score:.2f})')
        acoustic_pref = 0.8 if user.likes_acoustic else 0.2
        acoustic_score = 1.0 * (1 - abs(acoustic_pref - song.acousticness))
        reasons.append(f'acoustic match (+{acoustic_score:.2f})')
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
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores one song against user preferences and returns (total_score, reasons)."""
    score = 0.0
    reasons = []

    if song['genre'] == user_prefs.get('genre'):
        score += 3.0
        reasons.append('genre match (+3.0)')

    if song['mood'] == user_prefs.get('mood'):
        score += 2.0
        reasons.append('mood match (+2.0)')

    target_energy = user_prefs.get('energy', 0.5)
    energy_score = 2.0 * (1 - abs(target_energy - song['energy']))
    score += energy_score
    reasons.append(f'energy proximity (+{energy_score:.2f})')

    likes_acoustic = user_prefs.get('likes_acoustic', False)
    acoustic_pref = 0.8 if likes_acoustic else 0.2
    acoustic_score = 1.0 * (1 - abs(acoustic_pref - song['acousticness']))
    score += acoustic_score
    reasons.append(f'acoustic match (+{acoustic_score:.2f})')

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores all songs, sorts by score descending, and returns the top k with explanations."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ', '.join(reasons)))
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
