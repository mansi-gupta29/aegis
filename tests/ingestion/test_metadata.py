from pathlib import Path

from app.ingestion.metadata import (
    extract_metadata,
    infer_document_type,
    make_document_id,
)
from app.ingestion.models import DocumentType, FileType, RawDocument


def test_make_document_id_is_deterministic() -> None:
    assert make_document_id("data/documents/a.md") == make_document_id(
        "data/documents/a.md"
    )


def test_make_document_id_differs_by_source() -> None:
    assert make_document_id("a.md") != make_document_id("b.md")


def test_extract_metadata_uses_first_markdown_heading_as_title() -> None:
    raw = RawDocument(
        source="data/documents/architecture/overview.md",
        file_type=FileType.MARKDOWN,
        content="# System Overview\n\nSome intro text.",
    )

    document = extract_metadata(raw, Path("data/documents"))

    assert document.title == "System Overview"


def test_extract_metadata_falls_back_to_filename_for_text_files() -> None:
    raw = RawDocument(
        source="data/documents/engineering-docs/api_guidelines.txt",
        file_type=FileType.TEXT,
        content="Just some plain notes, no heading here.",
    )

    document = extract_metadata(raw, Path("data/documents"))

    assert document.title == "api guidelines"


def test_infer_document_type_from_folder_name() -> None:
    assert (
        infer_document_type("data/documents/runbooks/deploy.md", Path("data/documents"))
        == DocumentType.RUNBOOK
    )
    assert (
        infer_document_type(
            "data/documents/incidents/outage.md", Path("data/documents")
        )
        == DocumentType.INCIDENT
    )


def test_infer_document_type_unknown_for_unrecognized_folder() -> None:
    assert (
        infer_document_type("data/documents/misc/notes.md", Path("data/documents"))
        == DocumentType.UNKNOWN
    )


def test_extract_metadata_populates_all_required_fields() -> None:
    raw = RawDocument(
        source="data/documents/troubleshooting/latency.md",
        file_type=FileType.MARKDOWN,
        content="# High Latency\n\nDetails.",
    )

    document = extract_metadata(raw, Path("data/documents"))

    assert document.document_id == make_document_id(raw.source)
    assert document.title == "High Latency"
    assert document.source == raw.source
    assert document.document_type == DocumentType.TROUBLESHOOTING
    assert document.file_type == FileType.MARKDOWN
    assert document.metadata["document_type"] == DocumentType.TROUBLESHOOTING.value
