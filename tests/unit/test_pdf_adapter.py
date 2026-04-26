"""PDFAdapter — extract text from PDF bytes; speaker = filename stem."""
from pathlib import Path

from ai_hive_memory.ingest.adapters.pdf import PDFAdapter


def test_parse_extracts_text_from_pdf_fixture() -> None:
    fixture = Path(__file__).parent.parent / "fixtures" / "sample.pdf"
    raw = fixture.read_bytes()
    msgs = PDFAdapter(speaker_label="Document").parse(raw)
    assert len(msgs) >= 1
    combined = "\n".join(m.text for m in msgs)
    assert "Hello PDF World" in combined
    assert msgs[0].speaker == "Document"


def test_fmt_attribute_is_pdf() -> None:
    assert PDFAdapter().fmt == "pdf"


def test_default_speaker_label_is_document() -> None:
    assert PDFAdapter().speaker_label == "Document"
