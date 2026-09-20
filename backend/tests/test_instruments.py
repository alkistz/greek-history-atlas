from dataclasses import replace

from conftest import swap

from app.core.content import validate
from app.modules.instruments import crud


def test_control_rows_cite_instruments_by_id(corpus):
    rows = crud.control_rows_of(corpus, "constantinople-1832")
    assert {r.atom for r in rows} == {
        "peloponnese",
        "attica",
        "sterea",
        "evvoia",
        "aitoloakarnania",
        "cyclades",
        "sporades",
    }


def test_events_cite_instruments(corpus):
    assert [e.id for e in crud.events_citing(corpus, "lausanne-1923")] == [
        "treaty-of-lausanne-1923"
    ]


def test_unknown_party_is_rejected(corpus):
    inst = crud.get_instrument(corpus, "paris-1815")
    bad = inst.model_validate({**inst.model_dump(), "parties": ["atlantis"]})
    problems = validate(replace(corpus, instruments=swap(corpus.instruments, bad)))
    assert any("unknown party 'atlantis'" in p for p in problems)
