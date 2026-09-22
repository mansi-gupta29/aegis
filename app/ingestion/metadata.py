"""Derives document-level metadata from a raw, freshly-loaded document."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from app.ingestion.models import Document, DocumentType, RawDocument

_MARKDOWN_HEADING_RE = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)

# Folder name (relative to the documents root) -> document type.
_FOLDER_TO_DOCUMENT_TYPE: dict[str, DocumentType] = {
    "architecture": DocumentType.ARCHITECTURE,
    "runbooks": DocumentType.RUNBOOK,
    "troubleshooting": DocumentType.TROUBLESHOOTING,
    "incidents": DocumentType.INCIDENT,
    "engineering-docs": DocumentType.ENGINEERING_DOC,
    "source-code": DocumentType.SOURCE_CODE,
}


def make_document_id(source: str) -> str:
    """A short, deterministic id derived from the document's source path."""
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]


def extract_title(raw_document: RawDocument) -> str:
    """Use the first Markdown heading if present, otherwise the filename stem."""
    match = _MARKDOWN_HEADING_RE.search(raw_document.content)
    if match:
        return match.group(1).strip()
    return Path(raw_document.source).stem.replace("_", " ").replace("-", " ").strip()


def infer_document_type(
    source: str, documents_root: Path | None = None
) -> DocumentType:
    """Infer the document type from the top-level folder under the documents root."""
    path = Path(source)
    parts = path.parts
    if documents_root is not None:
        try:
            relative_parts = path.relative_to(documents_root).parts
        except ValueError:
            relative_parts = parts
    else:
        relative_parts = parts

    for part in relative_parts[:-1]:
        document_type = _FOLDER_TO_DOCUMENT_TYPE.get(part.lower())
        if document_type is not None:
            return document_type
    return DocumentType.UNKNOWN


def extract_metadata(
    raw_document: RawDocument, documents_root: Path | None = None
) -> Document:
    """Build a fully-parsed Document from a RawDocument."""
    document_id = make_document_id(raw_document.source)
    title = extract_title(raw_document)
    document_type = infer_document_type(raw_document.source, documents_root)

    return Document(
        document_id=document_id,
        title=title,
        source=raw_document.source,
        document_type=document_type,
        file_type=raw_document.file_type,
        content=raw_document.content,
        metadata={
            "title": title,
            "document_type": document_type.value,
            "file_type": raw_document.file_type.value,
        },
    )
