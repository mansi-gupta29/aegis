"""Discovers and loads supported files from a documents directory."""

from __future__ import annotations

import logging
from pathlib import Path

from app.ingestion.models import FileType, RawDocument

logger = logging.getLogger(__name__)

_EXTENSION_TO_FILE_TYPE: dict[str, FileType] = {
    ".md": FileType.MARKDOWN,
    ".markdown": FileType.MARKDOWN,
    ".txt": FileType.TEXT,
}


def discover_files(root: Path) -> list[Path]:
    """Recursively find all supported files under `root`, sorted for determinism."""
    if not root.exists():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in _EXTENSION_TO_FILE_TYPE
    )


def load_document(path: Path) -> RawDocument | None:
    """Read a single file into a RawDocument, or None if it's invalid/empty."""
    file_type = _EXTENSION_TO_FILE_TYPE.get(path.suffix.lower())
    if file_type is None:
        logger.warning("Skipping unsupported file type: %s", path)
        return None

    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        logger.warning("Skipping unreadable file %s: %s", path, exc)
        return None

    if not content.strip():
        logger.warning("Skipping empty file: %s", path)
        return None

    return RawDocument(source=str(path), file_type=file_type, content=content)


def load_documents(root: Path) -> list[RawDocument]:
    """Discover and load all supported files under `root`, skipping invalid ones."""
    documents: list[RawDocument] = []
    for path in discover_files(root):
        raw_document = load_document(path)
        if raw_document is not None:
            documents.append(raw_document)
    return documents
