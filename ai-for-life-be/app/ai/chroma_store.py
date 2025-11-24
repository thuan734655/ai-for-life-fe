from functools import lru_cache
import chromadb
from app.core.config import settings


@lru_cache(maxsize=1)
def get_client():
    # Use persistent client by default; can be switched to HttpClient via settings later
    return chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)


@lru_cache(maxsize=1)
def get_jobs_collection():
    client = get_client()
    name = settings.CHROMA_COLLECTION_JOBS
    try:
        col = client.get_collection(name=name)
    except  Exception as e:
        print(f"Creating Chroma collection: {e}")
        col = client.create_collection(name=name, metadata={"hnsw:space": "cosine"})
    return col
