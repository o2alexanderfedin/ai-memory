"""Ingest pipeline orchestrator (DIR-3.x).

Stages, in order:
  1. AdapterRouter.parse(format, raw)            — bytes → Message[]
  2. LitePIIScrubber.scrub_batch(...)            — redact SSN/CC
  3. IdempotencyGuard.filter_unseen(...)         — drop already-seen hashes
  4. Chunker.chunk(...)                          — Message[] → Chunk[]
  5. ExtractionFanout.run(chunk)  per chunk      — 6 concurrent extractors
     wrapped by ExtractionFailurePolicy.run_async
  6. PendingFactRepository.persist(...)          — write each fact

After processing all chunks, IngestJobRepository.update_status sets
status=DONE (or FAILED) plus per-domain extraction counts in domain_status.
"""
import hashlib

from pydantic import BaseModel as PydanticModel
from sqlalchemy.engine import Connection

from ai_hive_memory.ingest.adapters import AdapterRouter
from ai_hive_memory.ingest.adapters.email_mime import EmailMIMEAdapter
from ai_hive_memory.ingest.adapters.pdf import PDFAdapter
from ai_hive_memory.ingest.adapters.telegram import TelegramAdapter
from ai_hive_memory.ingest.adapters.voice import VoiceAdapter
from ai_hive_memory.ingest.adapters.whatsapp import WhatsAppAdapter
from ai_hive_memory.ingest.chunker import Chunker
from ai_hive_memory.ingest.extractors.base import ExtractionFanout
from ai_hive_memory.ingest.extractors.biography import BiographyExtractor
from ai_hive_memory.ingest.extractors.experiences import ExperiencesExtractor
from ai_hive_memory.ingest.extractors.preferences import PreferencesExtractor
from ai_hive_memory.ingest.extractors.psychometrics import PsychometricsExtractor
from ai_hive_memory.ingest.extractors.social_circle import SocialCircleExtractor
from ai_hive_memory.ingest.extractors.work import WorkExtractor
from ai_hive_memory.ingest.failure_policy import ExtractionFailurePolicy
from ai_hive_memory.ingest.idempotency import IdempotencyGuard
from ai_hive_memory.ingest.messages import Message
from ai_hive_memory.ingest.pii import LitePIIScrubber
from ai_hive_memory.llm.gateway import LLMGateway
from ai_hive_memory.storage.ingest_repository import (
    IngestJobRepository,
    PendingFactRepository,
)

DOMAINS = ("biography", "experiences", "preferences",
           "social_circle", "work", "psychometrics")


def _default_router(_gateway: LLMGateway) -> AdapterRouter:
    r = AdapterRouter()
    r.register("whatsapp", WhatsAppAdapter())
    r.register("telegram", TelegramAdapter())
    r.register("pdf", PDFAdapter())
    r.register("email", EmailMIMEAdapter())
    r.register("voice", VoiceAdapter())
    return r


def _default_fanout(gateway: LLMGateway) -> ExtractionFanout:
    return ExtractionFanout(extractors=[
        BiographyExtractor(gateway=gateway),
        ExperiencesExtractor(gateway=gateway),
        PreferencesExtractor(gateway=gateway),
        SocialCircleExtractor(gateway=gateway),
        WorkExtractor(gateway=gateway),
        PsychometricsExtractor(gateway=gateway),
    ])


def _hash_message(msg: Message) -> str:
    """Return SHA-256 hex digest of the message's canonical signature."""
    return hashlib.sha256(msg.canonical_signature().encode()).hexdigest()


def _fact_has_content(fact: object) -> bool:
    """Return True if the fact's `fields` block contains at least one non-null/non-empty value.

    Facts built from an empty LLM response ({}) have all-None fields and should
    not be persisted — they carry no information.
    """
    if not isinstance(fact, PydanticModel):
        return True  # unknown type — accept conservatively
    fields_obj = getattr(fact, "fields", None)
    if fields_obj is None:
        return False
    if not isinstance(fields_obj, PydanticModel):
        return True
    empty_sentinels: tuple[None | list[object] | dict[object, object], ...] = (None, [], {})
    return any(v not in empty_sentinels for v in fields_obj.model_dump().values())


class IngestPipeline:
    """Stateless orchestrator. Inject `gateway` for testing."""

    def __init__(
        self,
        gateway: LLMGateway | None = None,
        chunker: Chunker | None = None,
        scrubber: LitePIIScrubber | None = None,
        failure_policy: ExtractionFailurePolicy | None = None,
    ) -> None:
        self._gateway = gateway or LLMGateway()
        self._router = _default_router(self._gateway)
        self._fanout = _default_fanout(self._gateway)
        self._chunker = chunker or Chunker()
        self._scrubber = scrubber or LitePIIScrubber()
        self._policy = failure_policy or ExtractionFailurePolicy()
        self._job_repo = IngestJobRepository()
        self._pf_repo = PendingFactRepository()

    async def run(  # noqa: PLR0913
            self, *, conn: Connection, tenant_id: str, persona_id: str,
            job_id: str, fmt: str, raw: bytes) -> None:
        try:
            self._job_repo.update_status(conn, tenant_id, job_id, status="RUNNING")
            messages: list[Message] = self._router.parse(fmt, raw)
            scrubbed = list(self._scrubber.scrub_batch(messages))
            seen = self._pf_repo.seen_hashes_for_persona(conn, tenant_id, persona_id)
            guard = IdempotencyGuard(seen_hashes=seen)
            unseen = list(guard.filter_unseen(scrubbed))
            chunks = list(self._chunker.chunk(unseen, persona_id=persona_id))

            domain_status: dict[str, str] = {d: "PENDING" for d in DOMAINS}
            for chunk in chunks:
                results = await self._fanout.run(chunk)
                # Compute source_hash per chunk from first message's canonical signature.
                source_hash = (
                    _hash_message(chunk.messages[0])
                    if chunk.messages else "empty"
                )
                succeeded: list[str] = []
                for domain, facts in results.items():
                    try:
                        for fact in facts:
                            if not _fact_has_content(fact):
                                continue
                            self._pf_repo.persist(
                                conn, tenant_id, persona_id, job_id,
                                domain=domain, fact=fact, source_hash=source_hash,
                            )
                        succeeded.append(domain)
                        domain_status[domain] = "DONE"
                    except Exception as e:
                        domain_status[domain] = f"FAILED: {e}"
                # 5/6 partial accept gate per chunk
                self._policy.assert_partial_accept(
                    succeeded_domains=succeeded,
                    all_domains=list(DOMAINS),
                )
                self._pf_repo.mark_seen(
                    conn, tenant_id, persona_id,
                    [_hash_message(m) for m in chunk.messages],
                )

            self._job_repo.update_status(
                conn, tenant_id, job_id, status="DONE",
                domain_status=domain_status,
            )
        except Exception as e:
            self._job_repo.update_status(
                conn, tenant_id, job_id, status="FAILED",
                error=str(e),
            )
            raise
