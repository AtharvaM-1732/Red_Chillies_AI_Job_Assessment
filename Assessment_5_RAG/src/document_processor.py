import os
import tempfile

import pymupdf4llm
import streamlit as st

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from src.config import (
    EMBED_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


# EMBEDDINGS
@st.cache_resource
def get_embeddings():
    """Load and cache the local embedding model."""

    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )


# RAW DOCUMENT EXTRACTION
def extract_documents(uploaded_files):
    """Extract text while retaining source and page metadata."""

    documents = []

    with tempfile.TemporaryDirectory() as temp_dir:

        for file_index, uploaded_file in enumerate(uploaded_files):
            filename = os.path.basename(uploaded_file.name)
            extension = os.path.splitext(filename)[1].lower()

            if extension not in {".pdf", ".txt"}:
                continue

            temp_path = os.path.join(
                temp_dir,
                f"{file_index}_{filename}",
            )

            with open(temp_path, "wb") as file:
                file.write(uploaded_file.getbuffer())

            # PDF EXTRACTION
            if extension == ".pdf":

                page_chunks = pymupdf4llm.to_markdown(
                    temp_path,
                    page_chunks=True,
                )

                for page_index, page_data in enumerate(page_chunks):

                    page_text = page_data.get("text", "").strip()

                    if not page_text:
                        continue

                    documents.append(
                        Document(
                            page_content=page_text,
                            metadata={
                                "source": filename,
                                # Use a consistent, one-based page number.
                                "page": page_index + 1,
                                "file_type": "pdf",
                            },
                        )
                    )

            # TXT EXTRACTION
            elif extension == ".txt":

                with open(
                    temp_path,
                    "r",
                    encoding="utf-8-sig",
                    errors="replace",
                ) as file:
                    text = file.read().strip()

                if text:
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": filename,
                                "page": "N/A",
                                "file_type": "txt",
                            },
                        )
                    )

    return documents


# STRUCTURAL SPLITTING
def split_by_structure(documents):
    """Split PDF Markdown by headings without losing source metadata."""

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )

    structural_documents = []

    for document in documents:

        if document.metadata.get("file_type") != "pdf":
            structural_documents.append(document)
            continue

        try:
            splits = markdown_splitter.split_text(
                document.page_content
            )
        except Exception:
            splits = []

        if not splits:
            structural_documents.append(document)
            continue

        for split in splits:

            metadata = {
                **document.metadata,
                **split.metadata,
            }

            # Never let structural splitting lose these fields.
            metadata["source"] = document.metadata["source"]
            metadata["page"] = document.metadata["page"]
            metadata["file_type"] = document.metadata["file_type"]

            structural_documents.append(
                Document(
                    page_content=split.page_content,
                    metadata=metadata,
                )
            )

    return structural_documents


# CHUNKING
def chunk_documents(documents):
    """Apply semantic chunking with a recursive fallback."""

    embeddings = get_embeddings()

    semantic_chunker = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile",
    )

    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
        strip_whitespace=True,
    )

    final_chunks = []

    for document in documents:

        if not document.page_content.strip():
            continue

        # Pre-split extremely long sections to limit CPU and memory usage.
        pre_chunks = recursive_splitter.split_documents([document])

        for pre_chunk in pre_chunks:

            if not pre_chunk.page_content.strip():
                continue

            try:
                semantic_chunks = semantic_chunker.split_documents(
                    [pre_chunk]
                )
            except Exception:
                semantic_chunks = []

            if not semantic_chunks:
                semantic_chunks = [pre_chunk]

            for chunk in semantic_chunks:

                # Preserve the original source and page metadata.
                metadata = {
                    **pre_chunk.metadata,
                    **chunk.metadata,
                }

                metadata["source"] = document.metadata["source"]
                metadata["page"] = document.metadata["page"]
                metadata["file_type"] = document.metadata["file_type"]

                chunk = Document(
                    page_content=chunk.page_content.strip(),
                    metadata=metadata,
                )

                if not chunk.page_content:
                    continue

                # Semantic boundaries can produce a long chunk.
                # Split oversized chunks while retaining metadata.
                if len(chunk.page_content) > CHUNK_SIZE * 1.5:

                    smaller_chunks = recursive_splitter.split_documents(
                        [chunk]
                    )

                    final_chunks.extend(
                        smaller_chunks
                    )
                else:
                    final_chunks.append(chunk)

    return final_chunks


# PUBLIC PROCESSING FUNCTION
def process_documents(uploaded_files):
    """Complete local document-processing pipeline."""

    if not uploaded_files:
        return []

    raw_documents = extract_documents(uploaded_files)

    if not raw_documents:
        return []

    structural_documents = split_by_structure(raw_documents)

    if not structural_documents:
        return []

    return chunk_documents(structural_documents)