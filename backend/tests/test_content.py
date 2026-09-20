"""Smoke tests over the corpus.

Not an exhaustive suite. These check the things that would be silently wrong
rather than loudly broken.
"""

from datetime import date

import pytest

from app.core.content import Corpus, load, validate
from app.core.exceptions import ContentError
from app.modules.control import crud as control
from app.modules.control.models import Control


@pytest.fixture(scope="module")
def corpus():
    return load()


def test_corpus_loads_and_validates(corpus):
    assert len(corpus.atoms) == 19
    assert corpus.control
    assert corpus.events


def test_every_atom_has_geometry(corpus):
    geo = {f["properties"]["id"] for f in corpus.geojson["features"]}
    assert {a.id for a in corpus.atoms} == geo


def test_periods_are_half_open(corpus):
    """A transfer date belongs to the new holder, so nothing is held twice."""
    handover = date(1864, 6, 2)
    holders = {
        c.polity
        for c in control.control_on(corpus, handover)
        if c.atom == "ionian" and c.kind == "sovereign"
    }
    assert holders == {"gr-kingdom"}


def test_occupation_layers_over_sovereignty(corpus):
    """The point of the model: in 1942 Greece is still sovereign everywhere."""
    on = date(1942, 6, 1)
    rows = control.control_on(corpus, on)
    sovereign = {c.atom for c in rows if c.kind == "sovereign" and c.polity == "gr-kingdom"}
    occupied = {c.atom for c in rows if c.kind == "occupied"}
    assert len(sovereign) == 18
    assert occupied == sovereign
    occupiers = {c.polity for c in rows if c.kind == "occupied"}
    assert occupiers == {"germany", "italy", "bulgaria"}


def test_dodecanese_is_not_greek_in_1914(corpus):
    """The detail naive maps get wrong."""
    rows = control.control_on(corpus, date(1914, 1, 1))
    holder = next(c.polity for c in rows if c.atom == "dodecanese" and c.kind == "sovereign")
    assert holder == "italy"


def test_revolution_is_insurgency_not_sovereignty(corpus):
    """1821-32 must never assert Greek sovereignty."""
    rows = control.control_on(corpus, date(1826, 4, 22))
    kinds = {c.kind for c in rows if c.polity == "gr-provisional"}
    assert kinds == {"insurgent"}
    peloponnese = next(c.polity for c in rows if c.atom == "peloponnese" and c.kind == "sovereign")
    assert peloponnese == "ottoman"


def test_overlapping_sovereignty_is_rejected(corpus):
    """The invariant a PostGIS EXCLUDE constraint would have enforced."""
    bad = Control.model_validate(
        {
            "atom": "crete",
            "polity": "turkey",
            "kind": "sovereign",
            "from": "1900-01-01",
            "to": "1905-01-01",
        }
    )
    broken = Corpus(
        atoms=corpus.atoms,
        polities=corpus.polities,
        control=[*corpus.control, bad],
        events=corpus.events,
        geojson=corpus.geojson,
    )
    problems = validate(broken)
    assert any("overlapping 'sovereign'" in p for p in problems)
    assert any("crete" in p for p in problems)


def test_simultaneous_occupiers_are_also_rejected(corpus):
    """`occupied` is exclusive too: two occupiers at once is a modelling error."""
    bad = Control.model_validate(
        {
            "atom": "attica",
            "polity": "bulgaria",
            "kind": "occupied",
            "from": "1942-01-01",
            "to": "1943-01-01",
        }
    )
    broken = Corpus(
        atoms=corpus.atoms,
        polities=corpus.polities,
        control=[*corpus.control, bad],
        events=corpus.events,
        geojson=corpus.geojson,
    )
    assert any("overlapping 'occupied'" in p for p in validate(broken))


def test_content_error_reports_every_problem(corpus):
    with pytest.raises(ContentError) as e:
        raise ContentError(["one", "two"])
    assert len(e.value.problems) == 2
