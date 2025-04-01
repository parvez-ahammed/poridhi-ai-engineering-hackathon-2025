from fastembed.sparse.bm25 import Bm25
import tiktoken
from pprint import pprint


def sparse_embedding(texts: list[str]):
    bm25_embed_model = Bm25("Qdrant/bm25", cache_dir="./bm25_cache")
    embedding = list(bm25_embed_model.passage_embed(texts))
    return embedding


if __name__ == "__main__":
    print(sparse_embedding(["I eat rice"]))
    # enc = tiktoken.get_encoding("o200k_base")
    # enc = tiktoken.encoding_for_model("gpt-4o")
    # text = "I eat rice, আমি ভাত আর মাছ খাই।"
    # encoded = enc.encode(text)
    # decoded = enc.decode(encoded)
    # print(text, encoded, decoded)
    # print(enc.decode_single_token_bytes(encoded[0]))
