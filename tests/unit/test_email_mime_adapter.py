"""EmailMIMEAdapter — parse raw MIME email bytes into canonical Messages."""
import textwrap
from email.utils import formatdate

from ai_hive_memory.ingest.adapters.email_mime import EmailMIMEAdapter


def _make_simple_email(
    from_: str = "Alice <alice@example.com>",
    subject: str = "Hello",
    body: str = "Hi Bob, how are you?",
    date: str | None = None,
) -> bytes:
    date_header = date or formatdate(localtime=False)
    raw = textwrap.dedent(f"""\
        From: {from_}
        To: bob@example.com
        Subject: {subject}
        Date: {date_header}
        Content-Type: text/plain; charset=utf-8

        {body}
    """)
    return raw.encode()


def test_parse_simple_email_produces_one_message() -> None:
    raw = _make_simple_email(body="Hi Bob, how are you?")
    msgs = EmailMIMEAdapter().parse(raw)
    assert len(msgs) == 1
    assert msgs[0].speaker == "Alice <alice@example.com>"
    assert "Hi Bob, how are you?" in msgs[0].text


def test_subject_appears_in_metadata() -> None:
    raw = _make_simple_email(subject="Meeting tomorrow")
    msgs = EmailMIMEAdapter().parse(raw)
    assert msgs[0].metadata.get("subject") == "Meeting tomorrow"


def test_fmt_attribute_is_email() -> None:
    assert EmailMIMEAdapter().fmt == "email"
