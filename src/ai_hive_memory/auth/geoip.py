"""IP geo-block interface (Decision 12 MVP customer-scope EU/UK exclusion).

At MVP, the DefaultIPGeoBlocker is a no-op — it returns None for every lookup
and never blocks. Real geo-block (MaxMind GeoLite2) is deferred per Decision 12
sub-deferral: ToS attestation is the load-bearing legal mechanism; geo-block
is defense-in-depth that bolts on later.

Phase 7: implement MaxMindIPGeoBlocker that loads a GeoLite2-Country.mmdb file
and resolves IP → ISO-3166 country code.
"""
from typing import Protocol, runtime_checkable


class BlockedCountryError(Exception):
    """Raised when an IP resolves to a blocked country."""

    def __init__(self, country_code: str) -> None:
        self.country_code = country_code
        super().__init__(f"signup blocked: source country {country_code} is in the exclusion list")


@runtime_checkable
class IPGeoBlocker(Protocol):
    """Interface for IP → country resolution + block-list enforcement."""

    def lookup_country(self, ip: str) -> str | None:
        """Return ISO-3166 alpha-2 code for the IP, or None if unresolvable."""
        ...

    def assert_not_blocked(self, ip: str, blocked_countries: set[str]) -> None:
        """Raise BlockedCountryError if the IP resolves to a blocked country."""
        ...


class DefaultIPGeoBlocker:
    """No-op geo-blocker: never resolves, never blocks (MVP per Decision 12)."""

    def lookup_country(self, ip: str) -> str | None:
        return None

    def assert_not_blocked(self, ip: str, blocked_countries: set[str]) -> None:
        return None
