from dataclasses import replace

from conftest import swap

from app.core.content import validate
from app.core.models import Citation
from app.modules.sources import crud


def test_every_citation_resolves(corpus):
    known = {s.id for s in corpus.sources}
    cited = {c.id for e in corpus.events for c in e.sources}
    cited |= {c.id for f in corpus.figures for c in f.sources}
    cited |= {c.id for i in corpus.instruments for c in i.sources}
    assert cited <= known


def test_unknown_citation_is_rejected(corpus):
    event = next(e for e in corpus.events if e.id == "chios-massacre")
    bad = event.model_validate(
        {**event.model_dump(exclude={"body_html"}), "sources": [{"id": "nope"}]}
    )
    problems = validate(replace(corpus, events=swap(corpus.events, bad)))
    assert any("unknown source 'nope'" in p for p in problems)


def test_resolved_citations_carry_the_locator(corpus):
    resolved = crud.resolve_citations(corpus, [Citation(id="clogg-2021", locator="p. 1")])
    assert resolved[0]["author"] == "Richard Clogg"
    assert resolved[0]["locator"] == "p. 1"
