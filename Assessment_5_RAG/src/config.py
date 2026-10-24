import os

# PATHS
ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
DB_DIR = os.path.join(ROOT_DIR, "qdrant_local_db")
os.makedirs(DB_DIR, exist_ok=True)



# MODELS
LLM_MODEL = "qwen2.5:3b"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
RERANKER_MODEL = "BAAI/bge-reranker-base"


# QDRANT
COLLECTION_NAME = "rag_docs"

# DOCUMENT PROCESSING
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150

RETRIEVAL_K = 15 # Maximum candidates retrieved from each retriever.

RERANK_TOP_N = 4 # Number of passages retained after reranking.

# Hybrid retrieval weights.
BM25_WEIGHT = 0.3
VECTOR_WEIGHT = 0.7