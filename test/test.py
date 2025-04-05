from fastembed import LateInteractionTextEmbedding
import os

print(os.getcwd())

late_interaction_embedding_model = LateInteractionTextEmbedding(
    "colbert-ir/colbertv2.0",
    cache_dir="/media/atiqur-rahman/Extra/Projects/poridhi-ai-engineering-hackathon-2025/test/.cache",
    providers=["ROCMExecutionProvider"],
)

embedding = late_interaction_embedding_model.passage_embed(["Hello"] * 1000)
# print(embedding)
