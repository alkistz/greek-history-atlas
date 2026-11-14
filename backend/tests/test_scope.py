"""The atlas ends where `SCOPE_END` says, and nothing dated past it gets in."""

from dataclasses import replace
from datetime import date

from conftest import swap

from app.core.content import validate
from app.core.scope import SCOPE_END


def test_the_timeline_ends_at_the_scope(client):
    assert client.get("/api/meta").json()["range"]["to"] == SCOPE_END.isoformat()


def test_the_last_event_is_the_1975_constitution(corpus):
    last = max(corpus.events, key=lambda e: e.period[0])
    assert last.id == "constitution-1975"
    assert last.period[0] < SCOPE_END


def test_an_event_after_the_end_is_rejected(corpus):
    event = next(e for e in corpus.events if e.id == "constitution-1975")
    late = event.model_copy(update={"period": (date(1981, 1, 1), date(1981, 1, 2))})
    problems = validate(replace(corpus, events=swap(corpus.events, late)))
    assert any("event 'constitution-1975'" in p and "after the atlas ends" in p for p in problems)


def test_an_instrument_after_the_end_is_rejected(corpus):
    inst = corpus.instruments[-1]
    late = inst.model_copy(update={"signed": date(1979, 5, 28)})
    problems = validate(replace(corpus, instruments=swap(corpus.instruments, late)))
    assert any(f"instrument {inst.id!r}" in p and "after the atlas ends" in p for p in problems)
