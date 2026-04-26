import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

COLLECTION = "songs"
VECTOR_SIZE = 384


def get_client() -> QdrantClient:
    # Use cloud URL if set, otherwise fall back to local embedded mode (no Docker needed)
    url = os.environ.get("QDRANT_URL", "")
    if url:
        api_key = os.environ.get("QDRANT_API_KEY") or None
        return QdrantClient(url=url, api_key=api_key)
    local_path = os.path.join(os.path.dirname(__file__), "..", "qdrant_data")
    return QdrantClient(path=local_path)


def ensure_collection(client: QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


#Action: insertion of the embedded records

def upsert_songs(songs: list[dict], vectors: list[list[float]]) -> None:
    client = get_client()
    ensure_collection(client)
    points = [
        PointStruct(id=i, vector=vec, payload=song)
        for i, (song, vec) in enumerate(zip(songs, vectors))
    ]
    client.upsert(collection_name=COLLECTION, points=points)


# Action: Vector search in the remote qdrant cluster called music_viber

def search_songs(vector: list[float], top_k: int = 50) -> list[dict]:
    client = get_client()
    results = client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        limit=top_k,
        with_payload=True,
    )
    return [hit.payload for hit in results]
