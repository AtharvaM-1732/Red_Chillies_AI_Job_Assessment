import streamlit as st

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from langchain_qdrant import QdrantVectorStore
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import (
    EnsembleRetriever,
    ContextualCompressionRetriever,
)
from langchain_classic.retrievers.document_compressors import (
    CrossEncoderReranker,
)
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_ollama import OllamaLLM

from langchain_classic.chains import (
    create_retrieval_chain,
    create_history_aware_retriever,
)
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)

from src.config import (
    DB_DIR,
    LLM_MODEL,
    EMBED_MODEL,
    RERANKER_MODEL,
    COLLECTION_NAME,
    RETRIEVAL_K,
    RERANK_TOP_N,
    BM25_WEIGHT,
    VECTOR_WEIGHT,
)

from src.document_processor import get_embeddings


# QDRANT CLIENT
@st.cache_resource
def get_qdrant_client():
    """Reuse the local Qdrant client across Streamlit reruns."""

    return QdrantClient(
        path=DB_DIR,
    )


# VECTOR STORE
def setup_vector_store(chunks, collection_name):
    """
    Create a new, isolated collection for an indexing operation.

    Existing collections remain untouched until the new chain
    has been built successfully by the application.
    """

    if not chunks:
        raise ValueError("Cannot index an empty document collection.")

    if not collection_name.startswith(f"{COLLECTION_NAME}_"):
        raise ValueError(
            "Collection name must use the configured collection prefix."
        )

    client = get_qdrant_client()
    embeddings = get_embeddings()

    if client.collection_exists(collection_name):
        raise ValueError(
            f"Collection '{collection_name}' already exists. "
            "Choose a new collection name."
        )

    vector_size = len(
        embeddings.embed_query("vector dimension check")
    )

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )

    try:
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )

        vector_store.add_documents(chunks)

        return vector_store

    except Exception:
        # Clean up a partially populated collection on failure.
        if client.collection_exists(collection_name):
            client.delete_collection(collection_name)

        raise


# CACHED MODELS
@st.cache_resource
def get_reranker():
    """Load the local cross-encoder once."""

    return HuggingFaceCrossEncoder(
        model_name=RERANKER_MODEL,
        model_kwargs={
            "device": "cpu",
        },
    )


@st.cache_resource
def get_llm():
    """Create the local Ollama model wrapper."""

    return OllamaLLM(
        model=LLM_MODEL,
        temperature=0,
    )


# HYBRID RETRIEVAL + CONVERSATIONAL RAG
def build_conversational_retrieval_chain(chunks, qdrant_store):

    if not chunks:
        raise ValueError(
            "Cannot build the retrieval chain without document chunks."
        )

    # 1. BM25 KEYWORD RETRIEVER
    # Built from the same complete corpus used for Qdrant.
    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = RETRIEVAL_K

    # 2. QDRANT VECTOR RETRIEVER
    # Uses the Qdrant vector store to retrieve similar documents.
    qdrant_retriever = qdrant_store.as_retriever(
        search_kwargs={
            "k": RETRIEVAL_K,
        }
    )

    # 3. HYBRID ENSEMBLE
    # Combines the results of the BM25 and Qdrant retrievers.
    ensemble_retriever = EnsembleRetriever(
        retrievers=[
            bm25_retriever,
            qdrant_retriever,
        ],
        weights=[
            BM25_WEIGHT,
            VECTOR_WEIGHT,
        ],
    )

    # 4. CROSS-ENCODER RERANKER
    # Reranks the combined results using a cross-encoder model.
    reranker = get_reranker()

    compressor = CrossEncoderReranker(
        model=reranker,
        top_n=RERANK_TOP_N,
    )

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble_retriever,
    )

    llm = get_llm()

    # 5. HISTORY-AWARE QUESTION REFORMULATION
    # Reformulates the user's question to be a standalone question
    # using the conversation history when necessary.
    contextualize_system_prompt = (
        "Rewrite the latest user question as a standalone question "
        "using the conversation history when necessary.\n\n"
        "Preserve important names, dates, entities, and constraints.\n"
        "Do not answer the question.\n"
        "If the question is already standalone, return it unchanged."
    )

    contextualize_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            contextualize_system_prompt,
        ),
        MessagesPlaceholder(
            variable_name="chat_history"
        ),
        (
            "human",
            "{input}",
        ),
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm,
        compression_retriever,
        contextualize_prompt,
    )

    # 6. DOCUMENT CONTEXT FORMAT
    # All processed chunks should contain source and page metadata.
    document_prompt = PromptTemplate.from_template(
        "[Source: {source} | Page: {page}]\n"
        "{page_content}"
    )

    # 7. GROUNDED ANSWER GENERATION
    # Generates answers based on the retrieved document context.
    qa_system_prompt = (
        "You are a precise enterprise research assistant.\n\n"
        "Answer the user's question using ONLY the retrieved document "
        "context as evidence.\n\n"
        "The conversation history may help you interpret the question, "
        "but it is not evidence for factual claims about the documents.\n\n"
        "Follow these rules:\n"
        "1. Answer the question directly with providing details.\n"
        "2. Do not invent facts, quotations, sources, or page numbers.\n"
        "3. Cite supporting claims using [Source: filename, Page: number] "
        "whenever that metadata is available.\n"
        "4. If the evidence is insufficient, clearly say that the "
        "provided documents do not contain enough information.\n"
        "5. If retrieved sources disagree, explain the disagreement.\n"
        "6. Distinguish explicit facts from reasonable inferences.\n"
        "7. Use clear, structured Markdown when useful.\n\n"
        "Retrieved document context:\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            qa_system_prompt,
        ),
        MessagesPlaceholder(
            variable_name="chat_history"
        ),
        (
            "human",
            "{input}",
        ),
    ])

    answer_chain = create_stuff_documents_chain(
        llm,
        qa_prompt,
        document_prompt=document_prompt,
    )

    # 8. FINAL RETRIEVAL CHAIN
    # Combines the history-aware retriever and the answer chain.
    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        answer_chain,
    )

    return rag_chain