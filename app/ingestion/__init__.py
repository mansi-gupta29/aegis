"""Document ingestion pipeline: load -> extract metadata -> chunk."""

from pathlib import Path

from app.ingestion.chunker import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    chunk_document,
)
from app.ingestion.loader import discover_files, load_document, load_documents
from app.ingestion.metadata import extract_metadata
from app.ingestion.models import Chunk, Document, DocumentType, FileType, RawDocument

__all__ = [
    "DEFAULT_CHUNK_OVERLAP",
    "DEFAULT_CHUNK_SIZE",
    "Chunk",
    "Document",
    "DocumentType",
    "FileType",
    "RawDocument",
    "chunk_document",
    "discover_files",
    "extract_metadata",
    "ingest_documents",
    "load_document",
    "load_documents",
]


def ingest_documents(
    documents_root: Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Chunk]:
    """Run the full pipeline: discover -> load -> extract metadata -> chunk."""
    chunks: list[Chunk] = []
    for raw_document in load_documents(documents_root):
        document = extract_metadata(raw_document, documents_root)
        chunks.extend(
            chunk_document(document, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        )
    return chunks
