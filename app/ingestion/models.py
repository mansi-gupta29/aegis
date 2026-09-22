"""Pydantic models shared across the ingestion pipeline."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class FileType(str, Enum):
    MARKDOWN = "markdown"
    TEXT = "text"


class DocumentType(str, Enum):
    ARCHITECTURE = "architecture"
    RUNBOOK = "runbook"
    TROUBLESHOOTING = "troubleshooting"
    INCIDENT = "incident"
    ENGINEERING_DOC = "engineering_doc"
    SOURCE_CODE = "source_code"
    UNKNOWN = "unknown"


class RawDocument(BaseModel):
    """A file as read from disk, before metadata extraction."""

    source: str
    file_type: FileType
    content: str


class Document(BaseModel):
    """A fully parsed document, ready for chunking."""

    document_id: str
    title: str
    source: str
    document_type: DocumentType
    file_type: FileType
    content: str
    metadata: dict[str, str] = Field(default_factory=dict)


class Chunk(BaseModel):
    """A chunk of a document, ready for downstream embedding/retrieval."""

    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    heading: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
