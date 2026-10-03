"""Ingest pipeline orchestrator (DIR-3.x).

Stages, in order:
  1. AdapterRouter.parse(format, raw)            — bytes → Message[]
  2. LitePIIScrubber.scrub_batch(...)            — redact SSN/CC
  3. _missing_domains(...)                       — drop messages every domain
     has processed; group the rest by the domains still missing
  4. Chunker.chunk(...)                          — Message[] → Chunk[]
  5. Extract per chunk                           — 6 concurrent extractors, each
     wrapped by ExtractionFailurePolicy.run_async (retry with back-off); a
     domain that still fails is recorded, and the chunk is accepted if at
     least 5 of 6 domains succeeded (DIR-3.9)
  6. PendingFactRepository.persist(...)          — write each fact

After processing all chunks, IngestJobRepository.update_status sets
status=DONE (or FAILED) plus per-domain extraction counts in domain_status.
The caller marks the job RUNNING before `run`, in a transaction of its own:
a status written in `conn` becomes visible only when `conn` commits.
"""
import asyncio
import hashlib
from contextlib import suppress

from pydantic import BaseModel as PydanticModel
from sqlalchemy.engine import Connection

from ai_hive_memory.ingest.adapters import AdapterRouter
from ai_hive_memory.ingest.adapters.email_mime import EmailMIMEAdapter
from ai_hive_memory.ingest.adapters.pdf import PDFAdapter
from ai_hive_memory.ingest.adapters.telegram import TelegramAdapter
from ai_hive_memory.ingest.adapters.voice import VoiceAdapter
from ai_hive_memory.ingest.adapters.whatsapp import WhatsAppAdapter
from ai_hive_memory.ingest.chunker import Chunk, Chunker
from ai_hive_memory.ingest.extractors.base import BaseExtractor, ExtractionFanout
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
    ALL_DOMAINS,
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

    def _missing_domains(
            self, conn: Connection, tenant_id: str, persona_id: str,
            messages: list[Message],
    ) -> dict[tuple[str, ...], list[Message]]:
        """Group the messages by the domains that have not processed them yet.

        Messages every domain has processed are dropped (US-2.3); so are
        repeats within this upload. Order is kept within each group.
        """
        seen = self._pf_repo.seen_domains_for_persona(conn, tenant_id, persona_id)
        work: dict[tuple[str, ...], list[Message]] = {}
        for msg in IdempotencyGuard().filter_unseen(messages):
            done = seen.get(_hash_message(msg), set())
            if ALL_DOMAINS in done:
                continue
            missing = tuple(d for d in DOMAINS if d not in done)
            if missing:
                work.setdefault(missing, []).append(msg)
        return work

    async def _extract(
            self, chunk: Chunk, domains: tuple[str, ...],
    ) -> tuple[dict[str, list[PydanticModel]], dict[str, Exception]]:
        """Run the extractors of `domains` on `chunk` under the failure policy.

        One domain's failure does not stop the others: it is returned in the
        second dict, and the partial-accept gate decides about the chunk.
        """
        loop = asyncio.get_running_loop()

        async def _one(
                ex: BaseExtractor,
        ) -> tuple[str, list[PydanticModel] | Exception]:
            try:
                facts: list[PydanticModel] = await self._policy.run_async(
                    ex.domain, lambda: loop.run_in_executor(None, ex.extract, chunk),
                )
            except Exception as e:
                return ex.domain, e
            return ex.domain, facts

        outcomes = await asyncio.gather(
            *[_one(ex) for ex in self._fanout.extractors if ex.domain in domains]
        )
        results = {d: o for d, o in outcomes if not isinstance(o, Exception)}
        errors = {d: o for d, o in outcomes if isinstance(o, Exception)}
        return results, errors

    async def run(  # noqa: PLR0913
            self, *, conn: Connection, tenant_id: str, persona_id: str,
            job_id: str, fmt: str, raw: bytes) -> None:
        try:
            messages: list[Message] = self._router.parse(fmt, raw)
            scrubbed = list(self._scrubber.scrub_batch(messages))
            work = self._missing_domains(conn, tenant_id, persona_id, scrubbed)
            chunks = [
                (domains, chunk)
                for domains, msgs in work.items()
                for chunk in self._chunker.chunk(msgs, persona_id=persona_id)
            ]

            domain_status: dict[str, str] = {d: "PENDING" for d in DOMAINS}
            for domains, chunk in chunks:
                results, extract_errors = await self._extract(chunk, domains)
                for domain, err in extract_errors.items():
                    domain_status[domain] = f"FAILED: {err}"
                # Compute source_hash per chunk from first message's canonical signature.
                source_hash = (
                    _hash_message(chunk.messages[0])
                    if chunk.messages else "empty"
                )
                succeeded: list[str] = []
                for domain, facts in results.items():
                    try:
                        # A savepoint per domain: a database error here undoes
                        # only this domain's rows and leaves the transaction
                        # usable, so the other domains can still be kept.
                        with conn.begin_nested():
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
                # 5/6 partial accept gate per chunk; domains that processed
                # these messages in an earlier upload count as succeeded.
                failed = [d for d in domains if d not in succeeded]
                self._policy.assert_partial_accept(
                    succeeded_domains=[d for d in DOMAINS if d not in failed],
                    all_domains=list(DOMAINS),
                )
                # Only the domains that succeeded: a re-upload retries the rest.
                self._pf_repo.mark_seen(
                    conn, tenant_id, persona_id,
                    [_hash_message(m) for m in chunk.messages], succeeded,
                )

            self._job_repo.update_status(
                conn, tenant_id, job_id, status="DONE",
                domain_status=domain_status,
            )
        except Exception as e:
            # After a database error the transaction is aborted and this update
            # fails too. Keep the original error; the caller then marks the
            # job FAILED in a new transaction.
            with suppress(Exception):
                self._job_repo.update_status(
                    conn, tenant_id, job_id, status="FAILED",
                    error=str(e),
                )
            raise
