"""The geometry checked against published areas, and the frontier cuts that made it
agree.

The tolerances are a ratchet on the README's table. NUTS3 units at 1:3 million agree
with the present-day and 1914 figures to a fraction of a percent; 1833 is looser
because its frontier comes from a small-scale map, and it was +2.7% before the 1832
line was cut through Fthiotida, Evrytania and Magnesia.
"""

from dataclasses import replace
from datetime import date

import pytest
from conftest import swap
from pydantic import ValidationError

from app.core.content import validate
from app.modules.atoms.models import Part
from app.modules.control import crud as control


def greek_km2(corpus, on: date) -> float:
    """Area held in sovereignty by a Greek polity on `on`, as the map's caption sums it."""
    km2 = {f["properties"]["id"]: f["properties"]["area_km2"] for f in corpus.geojson["features"]}
    external = {a.id for a in corpus.atoms if a.external}
    return sum(
        km2[r.atom]
        for r in control.control_on(corpus, on)
        if r.kind == "sovereign" and r.polity.startswith("gr-") and r.atom not in external
    )


@pytest.mark.parametrize(
    ("on", "published", "tolerance"),
    [
        (date(2000, 1, 1), 131_957, 0.005),
        (date(1914, 1, 1), 120_308, 0.005),
        (date(1833, 1, 1), 47_516, 0.015),
    ],
)
def test_area_matches_published(corpus, on, published, tolerance):
    assert abs(greek_km2(corpus, on) - published) / published < tolerance


def holder(corpus, atom: str, on: date, kind: str = "sovereign") -> str | None:
    rows = control.control_on(corpus, on)
    return next((r.polity for r in rows if r.atom == atom and r.kind == kind), None)


def test_the_1832_line_runs_through_fthiotida_and_magnesia(corpus):
    """Domokos stayed Ottoman until 1881; the Othrys coast at Pteleos did not."""
    assert holder(corpus, "sterea-north", date(1850, 1, 1)) == "ottoman"
    assert holder(corpus, "pteleos", date(1850, 1, 1)) == "gr-kingdom"
    assert holder(corpus, "sterea-north", date(1882, 1, 1)) == "gr-kingdom"


def test_the_1881_line_leaves_preveza_and_elassona_ottoman(corpus):
    on = date(1900, 1, 1)
    assert holder(corpus, "arta", on) == "gr-kingdom"
    assert holder(corpus, "preveza", on) == "ottoman"
    assert holder(corpus, "thessaly-north", on) == "ottoman"


def test_northern_cyprus_is_occupied_not_annexed(corpus):
    on = date(1974, 9, 1)
    assert holder(corpus, "cyprus-north", on) == "cyprus-republic"
    assert holder(corpus, "cyprus-north", on, kind="occupied") == "turkey"
    assert holder(corpus, "cyprus", on, kind="occupied") is None
    assert holder(corpus, "cyprus-north", date(1974, 7, 1), kind="occupied") is None


def test_a_part_takes_one_kind_of_cut():
    with pytest.raises(ValidationError):
        Part(nuts3="EL644")
    with pytest.raises(ValidationError):
        Part(nuts3="EL644", bbox=(0, 0, 1, 1), cut="kingdom-1832", side="inside")
    with pytest.raises(ValidationError):
        Part(nuts3="EL644", cut="kingdom-1832")


def test_an_unknown_cut_is_rejected(corpus):
    atom = next(a for a in corpus.atoms if a.id == "preveza")
    bad = atom.model_validate(
        {**atom.model_dump(), "parts": [{"nuts3": "EL541", "cut": "atlantis", "side": "outside"}]}
    )
    problems = validate(replace(corpus, atoms=swap(corpus.atoms, bad)))
    assert any("unknown cut 'atlantis'" in p for p in problems)


def test_an_unused_cut_is_rejected(corpus):
    cut = corpus.cuts[0]
    spare = cut.model_validate({**cut.model_dump(), "id": "spare"})
    problems = validate(replace(corpus, cuts=[*corpus.cuts, spare]))
    assert any("cut 'spare' is used by no atom" in p for p in problems)
