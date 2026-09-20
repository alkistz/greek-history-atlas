from dataclasses import replace
from datetime import date

from conftest import swap

from app.core.content import validate
from app.modules.places import crud


def test_name_in_force_changes_over_time(corpus):
    smyrna = crud.get_place(corpus, "smyrna")
    assert crud.name_on(smyrna, date(1919, 5, 15)).en == "Smyrna"
    assert crud.name_on(smyrna, date(1950, 1, 1)).en == "İzmir"


def test_overlapping_name_periods_are_rejected(corpus):
    place = crud.get_place(corpus, "smyrna")
    bad = place.model_validate(
        {
            **place.model_dump(by_alias=True, exclude={"names"}),
            "names": [
                {"name": {"en": "A"}, "from": "1900-01-01", "to": "1950-01-01"},
                {"name": {"en": "B"}, "from": "1940-01-01", "to": None},
            ],
        }
    )
    problems = validate(replace(corpus, places=swap(corpus.places, bad)))
    assert any("'A' and 'B' overlap in time" in p for p in problems)


def test_point_must_lie_inside_its_atom(corpus):
    athens = crud.get_place(corpus, "athens")
    bad = athens.model_validate({**athens.model_dump(by_alias=True), "atom": "crete"})
    problems = validate(replace(corpus, places=swap(corpus.places, bad)))
    assert any("not inside atom 'crete'" in p for p in problems)
