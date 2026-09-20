from dataclasses import replace

from conftest import swap

from app.core.content import validate
from app.modules.regions import crud


def test_regions_partition_the_atoms(corpus):
    """The invariant the whole feature rests on: an event's region is a lookup
    from its atom, so every atom needs exactly one region."""
    by_atom = crud.index(corpus)
    assert set(by_atom) == {a.id for a in corpus.atoms}
    assert sum(len(r.atoms) for r in corpus.regions) == len(by_atom)


def test_every_event_resolves_to_a_region(corpus):
    by_atom = crud.index(corpus)
    for event in corpus.events:
        if event.atom is not None:
            assert event.atom in by_atom, f"{event.id} sits in an unmapped atom"


def test_external_atoms_are_grouped_too(corpus):
    by_atom = crud.index(corpus)
    assert by_atom["smyrna"] == "asia-minor"
    assert by_atom["thrace-east"] == "thrace"
    assert by_atom["epirus-north"] == "epirus"


def test_an_unknown_atom_is_rejected(corpus):
    region = crud.get_region(corpus, "crete")
    bad = region.model_validate({**region.model_dump(), "atoms": ["crete", "atlantis"]})
    problems = validate(replace(corpus, regions=swap(corpus.regions, bad)))
    assert any("unknown atom 'atlantis'" in p for p in problems)


def test_an_atom_in_no_region_is_rejected(corpus):
    region = crud.get_region(corpus, "thessaly")
    bad = region.model_validate({**region.model_dump(), "atoms": ["thessaly"]})
    problems = validate(replace(corpus, regions=swap(corpus.regions, bad)))
    assert any("atom 'sporades' belongs to no region" in p for p in problems)


def test_an_atom_in_two_regions_is_rejected(corpus):
    region = crud.get_region(corpus, "crete")
    bad = region.model_validate({**region.model_dump(), "atoms": ["crete", "cyclades"]})
    problems = validate(replace(corpus, regions=swap(corpus.regions, bad)))
    assert any("'cyclades' belongs to more than one region" in p for p in problems)


def test_regions_ride_along_in_meta(client):
    body = client.get("/api/meta").json()
    ids = [r["id"] for r in body["regions"]]
    assert "macedonia" in ids
    macedonia = next(r for r in body["regions"] if r["id"] == "macedonia")
    assert macedonia["atoms"] == ["macedonia-west", "macedonia-central", "macedonia-east"]


def test_regions_endpoint(client):
    body = client.get("/api/regions").json()
    assert len(body) == 11
    assert next(r for r in body if r["id"] == "cyprus")["frame"] == "cyprus"
