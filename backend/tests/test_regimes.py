from dataclasses import replace
from datetime import date

from conftest import swap

from app.core.content import validate
from app.modules.regimes import crud


def test_regimes_form_an_unbroken_chain(corpus):
    """The invariant the whole facet rests on: contiguous, so every date inside the
    chain resolves to exactly one regime and no event needs a regime field."""
    ordered = crud.list_regimes(corpus)
    for a, b in zip(ordered, ordered[1:], strict=False):
        assert a.end == b.start, f"{a.id} does not hand over to {b.id}"
    assert ordered[-1].end is None
    assert all(r.end is not None for r in ordered[:-1])


def test_every_event_resolves_to_a_regime(corpus):
    for event in corpus.events:
        assert crud.regime_on(corpus, event.start) is not None, (
            f"{event.id} at {event.start} falls outside every regime"
        )


def test_a_transition_date_belongs_to_the_new_regime(corpus):
    """Half-open [from, to), as in control.yaml: the coup happens under the junta,
    not under the democracy it ended."""
    assert crud.regime_on(corpus, date(1967, 4, 21)).id == "junta-1967"
    assert crud.regime_on(corpus, date(1967, 4, 20)).id == "crowned-democracy-1944"
    assert crud.regime_on(corpus, date(1974, 7, 24)).id == "metapolitefsi-1974"
    assert crud.regime_on(corpus, date(1974, 12, 8)).id == "third-republic-1974"


def test_the_corpus_reaches_past_the_last_map_epoch(corpus):
    """Why this file exists: control stops changing in 1960 and the events do not.
    Those events need an axis that still moves."""
    late = [e for e in corpus.events if e.start > date(1960, 8, 16)]
    kinds = {crud.regime_on(corpus, e.start).kind for e in late}
    assert len(late) > 20
    assert kinds == {"constitutional_monarchy", "dictatorship", "interregnum", "republic"}


def test_before_the_revolution_there_is_no_regime(corpus):
    """Not a hole: there was no Greek state to have a form. An event dated there
    behaves like an event with no atom under the region filter."""
    assert crud.regime_on(corpus, date(1814, 9, 14)) is None


def test_a_gap_in_the_chain_is_rejected(corpus):
    regime = crud.get_regime(corpus, "junta-1967")
    bad = regime.model_validate({**regime.model_dump(by_alias=True), "to": "1974-07-01"})
    problems = validate(replace(corpus, regimes=swap(corpus.regimes, bad)))
    assert any("gap between regimes" in p for p in problems)


def test_an_overlap_in_the_chain_is_rejected(corpus):
    regime = crud.get_regime(corpus, "junta-1967")
    bad = regime.model_validate({**regime.model_dump(by_alias=True), "to": "1975-01-01"})
    problems = validate(replace(corpus, regimes=swap(corpus.regimes, bad)))
    assert any("overlapping regimes" in p for p in problems)


def test_a_second_open_ended_regime_is_rejected(corpus):
    regime = crud.get_regime(corpus, "occupation-1941")
    bad = regime.model_validate({**regime.model_dump(by_alias=True), "to": None})
    problems = validate(replace(corpus, regimes=swap(corpus.regimes, bad)))
    assert any("only the last regime may be open-ended" in p for p in problems)


def test_an_unknown_polity_is_rejected(corpus):
    regime = crud.get_regime(corpus, "third-republic-1974")
    bad = regime.model_validate({**regime.model_dump(by_alias=True), "polity": "atlantis"})
    problems = validate(replace(corpus, regimes=swap(corpus.regimes, bad)))
    assert any("unknown polity 'atlantis'" in p for p in problems)


def test_regimes_ride_along_in_meta(client):
    body = client.get("/api/meta").json()
    ids = [r["id"] for r in body["regimes"]]
    assert ids == sorted(ids, key=lambda i: [r["from"] for r in body["regimes"] if r["id"] == i][0])
    junta = next(r for r in body["regimes"] if r["id"] == "junta-1967")
    assert junta["from"] == "1967-04-21"
    assert junta["to"] == "1974-07-24"
    assert junta["kind"] == "dictatorship"


def test_regimes_endpoint(client):
    body = client.get("/api/regimes").json()
    assert len(body) == 13
    assert body[0]["id"] == "provisional-1821"
    assert body[-1]["to"] is None
    assert body[-1]["name"]["el"] == "Γ΄ Ελληνική Δημοκρατία"
