import os

PATH = os.getcwd() + "/.cache/huggingface"
os.environ["HF_HOME"] = PATH
os.environ["HF_DATASETS_CACHE"] = PATH
os.environ["TORCH_HOME"] = PATH

import torch
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Prefetch,
    SparseVector,
    FusionQuery,
    Fusion,
)
from BM25 import BM25
from pprint import pprint


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# set from environment variables
MODEL_PATH = os.path.join(os.getcwd(), "trained_models/all_mpnet_base_v2")
STOPWORDS_PATH = os.path.join(os.getcwd(), "stopwords")
COLLECTION_NAME = "product_collection_all_mpnet_base_v2_trained"
QDRANT_URL = "http://localhost:6333"

qdrant_client = QdrantClient(url=QDRANT_URL, timeout=600)

model = SentenceTransformer(MODEL_PATH, device=DEVICE)
bm25 = BM25(stopwords_dir=STOPWORDS_PATH, languages=["english", "bengali"])


def query(query_text: str, query_type: str = "hybrid"):
    dense_vector = model.encode([query_text])[0]
    sparse_vector = bm25.raw_embed([query_text])[0]

    prefetch = [
        Prefetch(query=dense_vector, using="dense_vector", limit=10),
        Prefetch(query=SparseVector(**sparse_vector), using="sparse_vector", limit=10),
    ]

    if query_type == "hybrid":
        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            prefetch=prefetch,
            query=FusionQuery(fusion=Fusion.RRF),
            with_payload=True,
            limit=5,
        )

    elif query_type == "sparse":
        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=SparseVector(**sparse_vector),
            using="sparse_vector",
            with_payload=True,
            limit=15,
        )

    elif query_type == "dense":
        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=dense_vector,
            using="dense_vector",
            with_payload=True,
            limit=15,
        )

    return [
        {"score": point.score, "payload": point.payload} for point in results.points
    ]


if __name__ == "__main__":
    query_result = query("small dji drone", "dense")
    pprint(query_result)
