from app.ingestion.chunker import chunk_document, make_chunk_id
from app.ingestion.models import Document, DocumentType, FileType


def _make_document(content: str, file_type: FileType = FileType.MARKDOWN) -> Document:
    return Document(
        document_id="doc-1",
        title="Test Doc",
        source="data/documents/test.md",
        document_type=DocumentType.ENGINEERING_DOC,
        file_type=file_type,
        content=content,
        metadata={"title": "Test Doc"},
    )


def test_chunk_document_returns_empty_list_for_empty_content() -> None:
    document = _make_document("")

    assert chunk_document(document) == []


def test_chunk_document_does_not_split_small_document() -> None:
    document = _make_document(
        "# Heading\n\nA short paragraph that easily fits in one chunk."
    )

    chunks = chunk_document(document, chunk_size=1000, chunk_overlap=100)

    assert len(chunks) == 1
    assert "A short paragraph" in chunks[0].content


def test_chunk_document_preserves_markdown_headings() -> None:
    content = (
        "# Intro\n\nIntro text.\n\n"
        "## Details\n\nDetails text that describes things in depth.\n\n"
        "## More Details\n\nEven more details here."
    )
    document = _make_document(content)

    chunks = chunk_document(document, chunk_size=1000, chunk_overlap=0)

    headings = [c.heading for c in chunks]
    assert "Intro" in headings
    assert "Details" in headings
    assert "More Details" in headings


def test_chunk_document_splits_large_content_by_size() -> None:
    paragraphs = [
        f"Paragraph number {i} with some filler words to add length." for i in range(20)
    ]
    content = "\n\n".join(paragraphs)
    document = _make_document(content, file_type=FileType.TEXT)

    chunks = chunk_document(document, chunk_size=200, chunk_overlap=0)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.content) <= 200


def test_chunk_document_overlap_repeats_trailing_content_in_next_chunk() -> None:
    paragraphs = [
        f"Paragraph {i} has some unique filler content to pad it out nicely."
        for i in range(10)
    ]
    content = "\n\n".join(paragraphs)
    document = _make_document(content, file_type=FileType.TEXT)

    chunks = chunk_document(document, chunk_size=150, chunk_overlap=50)

    assert len(chunks) > 1
    first_tail = chunks[0].content[-50:]
    assert first_tail in chunks[1].content


def test_chunk_document_produces_deterministic_chunk_ids() -> None:
    document = _make_document(
        "# Heading\n\nSome content that will be chunked consistently."
    )

    first_run = chunk_document(document, chunk_size=1000, chunk_overlap=100)
    second_run = chunk_document(document, chunk_size=1000, chunk_overlap=100)

    assert [c.chunk_id for c in first_run] == [c.chunk_id for c in second_run]


def test_make_chunk_id_is_deterministic_and_content_sensitive() -> None:
    id_a = make_chunk_id("doc-1", 0, "some content")
    id_b = make_chunk_id("doc-1", 0, "some content")
    id_c = make_chunk_id("doc-1", 0, "different content")

    assert id_a == id_b
    assert id_a != id_c


def test_chunk_document_preserves_document_id_and_metadata() -> None:
    document = _make_document("# Heading\n\nSome body text here.")

    chunks = chunk_document(document)

    for chunk in chunks:
        assert chunk.document_id == document.document_id
        assert chunk.metadata == document.metadata


def test_chunk_document_rejects_overlap_not_smaller_than_chunk_size() -> None:
    document = _make_document("# Heading\n\nBody text.")

    try:
        chunk_document(document, chunk_size=100, chunk_overlap=100)
        assert False, "expected ValueError"
    except ValueError:
        pass
