from pathlib import Path

from app.ingestion.loader import discover_files, load_document, load_documents
from app.ingestion.models import FileType


def test_discover_files_finds_markdown_and_text_recursively(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.md").write_text("# A")
    (tmp_path / "sub" / "b.txt").write_text("hello")
    (tmp_path / "c.png").write_bytes(b"\x89PNG")

    found = discover_files(tmp_path)

    assert found == sorted(found)
    assert {p.name for p in found} == {"a.md", "b.txt"}


def test_discover_files_on_missing_root_returns_empty(tmp_path: Path) -> None:
    assert discover_files(tmp_path / "does-not-exist") == []


def test_load_document_reads_markdown_file(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text("# Title\n\nSome content.")

    raw_document = load_document(path)

    assert raw_document is not None
    assert raw_document.file_type == FileType.MARKDOWN
    assert raw_document.source == str(path)
    assert "Some content." in raw_document.content


def test_load_document_reads_plain_text_file(tmp_path: Path) -> None:
    path = tmp_path / "doc.txt"
    path.write_text("Just plain text.")

    raw_document = load_document(path)

    assert raw_document is not None
    assert raw_document.file_type == FileType.TEXT
    assert raw_document.content == "Just plain text."


def test_load_document_returns_none_for_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.md"
    path.write_text("   \n\n  ")

    assert load_document(path) is None


def test_load_document_returns_none_for_unsupported_extension(tmp_path: Path) -> None:
    path = tmp_path / "image.png"
    path.write_bytes(b"\x89PNG")

    assert load_document(path) is None


def test_load_document_returns_none_for_undecodable_file(tmp_path: Path) -> None:
    path = tmp_path / "bad.txt"
    path.write_bytes(b"\xff\xfe\x00\x00invalid utf-8 \xff")

    assert load_document(path) is None


def test_load_documents_skips_invalid_and_loads_valid(tmp_path: Path) -> None:
    (tmp_path / "good.md").write_text("# Good\n\nContent")
    (tmp_path / "empty.txt").write_text("")
    (tmp_path / "image.png").write_bytes(b"\x89PNG")

    documents = load_documents(tmp_path)

    assert len(documents) == 1
    assert documents[0].source.endswith("good.md")
