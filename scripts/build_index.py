"""
One-time setup script: embeds all songs and loads them into Qdrant.

Run from project root:
    python scripts/build_index.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

import json

from ai.embeddings import embed_song
from ai.qdrant_db import upsert_songs

JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "new_data", "songs.json")


def main():
    print("Loading songs...")
    with open(JSON_PATH) as f:
        songs = json.load(f)
    print(f"  {len(songs)} songs loaded.")

    print("Embedding songs (this may take a moment on first run)...")
    vectors = [embed_song(song) for song in songs]
    print(f"  {len(vectors)} vectors created (dim={len(vectors[0])}).")

    print("Upserting into Qdrant...")
    upsert_songs(songs, vectors)
    print(f"  Done. Indexed {len(songs)} songs into Qdrant collection 'songs'.")


if __name__ == "__main__":
    main()
