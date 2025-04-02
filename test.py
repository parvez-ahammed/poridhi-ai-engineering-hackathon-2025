import os

PATH = os.getcwd() + "/.cache/huggingface"
os.environ["HF_HOME"] = PATH
os.environ["HF_DATASETS_CACHE"] = PATH
os.environ["TORCH_HOME"] = PATH

from fastembed import SparseTextEmbedding

bm25_embedding_model = SparseTextEmbedding("Qdrant/bm25", cache_dir="./bm25_cache")

next(bm25_embedding_model.query_embed("I eat rice, আমি ভাত খাই"))
