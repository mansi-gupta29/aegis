"""Splits a Document into overlapping Chunks, preserving Markdown structure."""

from __future__ import annotations

import hashlib
import re

from app.ingestion.models import Chunk, Document, FileType

_MARKDOWN_HEADING_RE = re.compile(r"^#{1,6}\s+.*$", re.MULTILINE)
_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def make_chunk_id(document_id: str, chunk_index: int, content: str) -> str:
    """A short, deterministic id derived from the chunk's document, position, and content."""
    payload = f"{document_id}:{chunk_index}:{content}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _split_into_sections(content: str) -> list[tuple[str | None, str]]:
    """Split Markdown content on heading lines, keeping each heading with its body."""
    matches = list(_MARKDOWN_HEADING_RE.finditer(content))
    if not matches:
        return [(None, content)]

    sections: list[tuple[str | None, str]] = []

    preamble = content[: matches[0].start()].strip()
    if preamble:
        sections.append((None, preamble))

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        heading_text = match.group().lstrip("#").strip()
        section_text = content[start:end].strip()
        sections.append((heading_text, section_text))

    return sections


def _split_into_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in _PARAGRAPH_SPLIT_RE.split(text) if p.strip()]


def _split_long_paragraph(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Sliding-window split for a single paragraph that exceeds chunk_size on its own."""
    step = max(chunk_size - chunk_overlap, 1)
    pieces: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        pieces.append(text[start:end])
        if end >= len(text):
            break
        start += step
    return pieces


def _tail(text: str, length: int) -> str:
    return text[-length:] if length > 0 else ""


def _pack_paragraphs(
    paragraphs: list[str], chunk_size: int, chunk_overlap: int
) -> list[str]:
    """Greedily pack paragraphs into <=chunk_size windows, carrying overlap between them."""
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    def flush() -> None:
        nonlocal current, current_len
        if current:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            flush()
            chunks.extend(_split_long_paragraph(paragraph, chunk_size, chunk_overlap))
            continue

        added_len = len(paragraph) + (2 if current else 0)
        if current and current_len + added_len > chunk_size:
            flush()
            overlap_text = _tail(chunks[-1], chunk_overlap)
            if overlap_text:
                current = [overlap_text]
                current_len = len(overlap_text)

        current.append(paragraph)
        current_len += len(paragraph) + (2 if len(current) > 1 else 0)

    flush()
    return chunks


def chunk_document(
    document: Document,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Chunk]:
    """Split a Document into deterministic, metadata-carrying Chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size"
        )

    if document.file_type == FileType.MARKDOWN:
        sections = _split_into_sections(document.content)
    else:
        sections = [(None, document.content)]

    chunks: list[Chunk] = []
    for heading, section_text in sections:
        paragraphs = _split_into_paragraphs(section_text)
        for chunk_text in _pack_paragraphs(paragraphs, chunk_size, chunk_overlap):
            if not chunk_text.strip():
                continue
            index = len(chunks)
            chunks.append(
                Chunk(
                    chunk_id=make_chunk_id(document.document_id, index, chunk_text),
                    document_id=document.document_id,
                    chunk_index=index,
                    content=chunk_text,
                    heading=heading,
                    metadata=document.metadata,
                )
            )

    return chunks
