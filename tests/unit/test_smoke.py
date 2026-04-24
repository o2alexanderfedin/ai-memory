"""Smoke test — confirm pytest collection works."""

def test_smoke(smoke: bool) -> None:
    assert smoke is True
