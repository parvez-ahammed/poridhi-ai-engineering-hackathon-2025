import os
import re
from collections import defaultdict
from transformers import AutoTokenizer


class BM25:
    def __init__(
        self,
        stopwords_dir: str,
        languages: list[str],
        k: float = 1.2,
        b: float = 0.75,
        avg_len: float = 256.0,
    ):
        self.stopwords = self._load_stopwords(stopwords_dir, languages)
        self.k = k
        self.b = b
        self.avg_len = avg_len
        self.tokenizer = AutoTokenizer.from_pretrained(
            "Cohere/multilingual-22-12", cache_dir=os.getcwd()
        )

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

    def _clean_text(self, text: str) -> str:
        clean_tokens: list[str] = []

        # remove punctuations
        text = re.sub(r"[^\w\s\u0980-\u09FF]", "", text)
        tokens = text.lower().strip().split()

        for token in tokens:
            if token in self.stopwords:
                continue

            clean_tokens.append(token)

        return " ".join(clean_tokens)

    def calculate_avg_doc_len(self, documents: list[str]) -> float:

        total_len: float = 0.0
        for document in documents:
            cleaned_text = self._clean_text(document)
            token_ids = self.tokenizer.encode(cleaned_text, add_special_tokens=False)
            total_len += len(token_ids)

        self.avg_len = total_len / len(documents)
        return self.avg_len

    def _term_frequency(self, text: str) -> dict[int, float]:
        tf_map: dict[str, list] = {"values": [], "indices": []}
        counter: defaultdict[int, int] = defaultdict(int)

        token_ids = self.tokenizer.encode(text, add_special_tokens=False)
        for token_id in token_ids:
            counter[token_id] += 1

        doc_len = len(token_ids)
        for token_id in counter:
            num_occurances = counter[token_id]
            score = num_occurances * (self.k + 1)
            score /= num_occurances + self.k * (
                1 - self.b + self.b * doc_len / self.avg_len
            )
            tf_map["values"].append(score)
            tf_map["indices"].append(token_id)

        return tf_map

    def raw_embed(self, documents: list[str]) -> list[dict]:
        embeddings: list[dict] = []

        for document in documents:
            cleaned_text = self._clean_text(document)
            token_id2value = self._term_frequency(cleaned_text)
            embeddings.append(token_id2value)
        return embeddings
