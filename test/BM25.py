import re
import sys
import unicodedata
import os
from collections import defaultdict
import mmh3
import tiktoken


class BM25:
    def __init__(
        self,
        stopwords_dir: str,
        languages: list[str],
        k: float = 1.2,
        b: float = 0.75,
        avg_len: float = 256.0,
    ):
        self.punctuations = self._get_all_punctuation()
        self.stopwords = self._load_stopwords(stopwords_dir, languages)
        self.k = k
        self.b = b
        self.avg_len = avg_len
        self.tiktoken_encoder = tiktoken.encoding_for_model("gpt-4o")

    @classmethod
    def compute_token_id(cls, token: str) -> int:
        return abs(mmh3.hash(token))

    # @classmethod
    # def compute_token_id_gpt(cls, token:)
    @classmethod
    def _load_stopwords(cls, model_dir: str, languages: list[str]) -> list[str]:
        stopword_paths = [
            os.path.join(model_dir, f"{language}.txt") for language in languages
        ]
        stopwords: list[str] = []

        for stopword_path in stopword_paths:
            with open(stopword_path, "r") as f:
                stopwords.extend(f.read().splitlines())

        return set(stopwords)

    def _get_all_punctuation(self) -> set[str]:
        return list(
            set(
                chr(i)
                for i in range(sys.maxunicode)
                if unicodedata.category(chr(i)).startswith("P")
            )
        )

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower().strip()
        return text.strip().split()

    def _clean_text(self, text: str) -> str:
        clean_tokens: list[str] = []
        text = re.sub(r"[^\w\s\u0980-\u09FF]", "", text)
        tokens = text.lower().strip().split()

        for token in tokens:
            if token in self.punctuations:
                continue

            if token in self.stopwords:
                continue

            clean_tokens.append(token)

        return " ".join(clean_tokens)

    def _term_frequency(self, text: str) -> dict[int, float]:
        tf_map: dict[int, float] = {}
        counter: defaultdict[int, int] = defaultdict(int)

        token_ids = self.tiktoken_encoder.encode(text)
        for token_id in token_ids:
            counter[token_id] += 1

        doc_len = len(token_ids)
        for token_id in counter:
            num_occurances = counter[token_id]
            tf_map[token_id] = num_occurances * (self.k + 1)
            tf_map[token_id] /= num_occurances + self.k * (
                1 - self.b + self.b * doc_len / self.avg_len
            )
        return tf_map

    def raw_embed(self, documents: list[str]) -> list[dict]:
        embeddings: list[dict] = []

        for document in documents:
            cleaned_text = self._clean_text(document)
            token_id2value = self._term_frequency(cleaned_text)
            embeddings.append(token_id2value)
        return embeddings


if __name__ == "__main__":
    bm25 = BM25(
        stopwords_dir=os.path.abspath("./stopwords"),
        languages=["english", "bengali"],
    )
    texts = ["I eat rice, "]
    embedding = bm25.raw_embed(texts)
    print(embedding)
