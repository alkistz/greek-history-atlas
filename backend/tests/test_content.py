"""Smoke tests over the corpus and the control invariants.

Not an exhaustive suite. These check the things that would be silently wrong
rather than loudly broken.
"""

from dataclasses import replace
from datetime import date

import pytest

from app.core.content import load_dir, validate
from app.core.exceptions import ContentError
from app.core.paths import EVENTS_DIR
from app.modules.control import crud as control
from app.modules.control.models import Control
from app.modules.events.models import Event


def test_corpus_loads_and_validates(corpus):
    assert len(corpus.atoms) == 25
    assert sum(a.external for a in corpus.atoms) == 5
    assert corpus.control
    assert corpus.events
    assert corpus.figures


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
    assert len(sovereign) == 19
    assert occupied == sovereign
    occupiers = {c.polity for c in rows if c.kind == "occupied"}
    assert occupiers == {"germany", "italy", "bulgaria"}


def test_external_atoms_have_no_baseline(corpus):
    """Smyrna is drawn only while Greece administers it; before and after it is land."""
    rows = control.control_on(corpus, date(1900, 1, 1))
    assert not any(c.atom == "smyrna" for c in rows)
    rows = control.control_on(corpus, date(1920, 1, 1))
    assert {(c.polity, c.kind) for c in rows if c.atom == "smyrna"} == {
        ("gr-kingdom", "administered")
    }


def test_cyprus_is_two_layered_before_1914(corpus):
    rows = {
        (c.polity, c.kind)
        for c in control.control_on(corpus, date(1900, 1, 1))
        if c.atom == "cyprus"
    }
    assert rows == {("ottoman", "sovereign"), ("britain", "administered")}


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
    problems = validate(replace(corpus, control=[*corpus.control, bad]))
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
    problems = validate(replace(corpus, control=[*corpus.control, bad]))
    assert any("overlapping 'occupied'" in p for p in problems)


def test_unknown_instrument_is_rejected(corpus):
    bad = Control.model_validate(
        {
            "atom": "crete",
            "polity": "gr-kingdom",
            "kind": "occupied",
            "from": "1900-01-01",
            "to": "1901-01-01",
            "instrument": "nope",
        }
    )
    problems = validate(replace(corpus, control=[*corpus.control, bad]))
    assert any("unknown instrument 'nope'" in p for p in problems)


def test_drawn_polity_needs_a_colour(corpus):
    """France signs treaties and has no colour; the moment it holds ground it needs one."""
    bad = Control.model_validate(
        {
            "atom": "crete",
            "polity": "france",
            "kind": "occupied",
            "from": "1900-01-01",
            "to": "1901-01-01",
        }
    )
    problems = validate(replace(corpus, control=[*corpus.control, bad]))
    assert any("'france' holds territory but has no colour" in p for p in problems)


def test_load_dir_requires_stem_to_match_id(tmp_path):
    (tmp_path / "wrong-name.yaml").write_text(
        "id: right-name\ntitle: {en: t}\nsummary: {en: s}\nperiod: [1900-01-01, 1900-01-02]\n"
        "precision: day\nsignificance: 1\n"
    )
    problems: list[str] = []
    load_dir(tmp_path, Event, problems)
    assert any("does not match file" in p for p in problems)


def test_every_event_file_is_named_after_its_id():
    problems: list[str] = []
    load_dir(EVENTS_DIR, Event, problems)
    assert problems == []


def test_content_error_reports_every_problem():
    with pytest.raises(ContentError) as e:
        raise ContentError(["one", "two"])
    assert len(e.value.problems) == 2
