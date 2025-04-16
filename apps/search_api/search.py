from fastapi import FastAPI, HTTPException
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Prefetch,
    SparseVector,
    FusionQuery,
    Fusion,
)
from .bm25 import BM25
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION_NAME")
QDRANT_URL = os.environ.get("QDRANT_URL")

app = FastAPI()

model = SentenceTransformer("./apps/search_api/ml_model")
bm25 = BM25(
    stopwords_dir=os.path.abspath("./apps/search_api/stopwards"), languages=["english", "bengali"]
)
qdrant_client = QdrantClient(url=QDRANT_URL, timeout=600)


def search(query_text: str, query_type: str = "hybrid", limit: int = 5):

    dense_vector = model.encode([query_text])[0]
    sparse_vector = bm25.raw_embed([query_text])[0]

    prefetch = [
        Prefetch(query=dense_vector, using="dense_vector", limit=10),
        Prefetch(query=SparseVector(**sparse_vector), using="sparse_vector", limit=10),
    ]

    if query_type == "hybrid":
        results = qdrant_client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            prefetch=prefetch,
            query=FusionQuery(fusion=Fusion.RRF),
            with_payload=True,
            limit=limit,
        )

    elif query_type == "sparse":
        results = qdrant_client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            query=SparseVector(**sparse_vector),
            using="sparse_vector",
            with_payload=True,
            limit=limit,
        )

    elif query_type == "dense":
        results = qdrant_client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            query=dense_vector,
            using="dense_vector",
            with_payload=True,
            limit=limit,
        )

    return [
        {"score": point.score, "payload": point.payload} for point in results.points
    ]


@app.get("/products")
def search_product(query: str = None, query_type="dense", limit: int = 5):

    if query is None or len(query) == 0:
        raise HTTPException(status_code=400, detail="Query is required")
    if query_type not in ["hybrid", "sparse", "dense"]:
        raise HTTPException(status_code=400, detail="Query type invalid")

    limit = max(5, min(limit, 20))

    query_res = search(query_text=query, query_type=query_type, limit=limit)

    return query_res
