"""IPGeoBlocker interface contract + DefaultIPGeoBlocker behavior."""
from ai_hive_memory.auth.geoip import (
    BlockedCountryError,
    DefaultIPGeoBlocker,
    IPGeoBlocker,
)


def test_default_impl_implements_interface() -> None:
    blocker = DefaultIPGeoBlocker()
    assert isinstance(blocker, IPGeoBlocker)


def test_default_blocker_returns_none_country_for_any_ip() -> None:
    """Default no-op impl: looks up nothing, returns country=None for every IP."""
    blocker = DefaultIPGeoBlocker()
    assert blocker.lookup_country("1.2.3.4") is None
    assert blocker.lookup_country("2001:db8::1") is None


def test_default_blocker_does_not_raise_for_eu_country() -> None:
    """Default impl never blocks (no .mmdb available; fail-open per MVP per Decision 12)."""
    blocker = DefaultIPGeoBlocker()
    blocker.assert_not_blocked("1.2.3.4", blocked_countries={"GB", "DE", "FR"})


def test_blocked_country_error_carries_iso_code() -> None:
    err = BlockedCountryError("GB")
    assert err.country_code == "GB"
    assert "GB" in str(err)
