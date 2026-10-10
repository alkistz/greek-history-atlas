from dataclasses import replace

from app.core.content import validate
from app.modules.relations import crud
from app.modules.relations.models import INVERSE, Relation


def test_every_kind_has_an_inverse_that_inverts():
    for kind, other in INVERSE.items():
        assert INVERSE[other] == kind


def test_a_tie_is_read_from_both_ends(corpus):
    """Written once, from George I's side; Constantine sees the inverse."""
    george = {other: kind for other, kind, _ in crud.relations_of(corpus, "george-i")}
    constantine = {other: kind for other, kind, _ in crud.relations_of(corpus, "constantine-i")}
    assert george["constantine-i"] == "child"
    assert constantine["george-i"] == "parent"
    assert constantine["venizelos"] == "rival"


def test_unknown_self_and_duplicate_ties_are_rejected(corpus):
    bad = [
        *corpus.relations,
        Relation.model_validate({"from": "venizelos", "to": "atlantis", "kind": "ally"}),
        Relation.model_validate({"from": "venizelos", "to": "venizelos", "kind": "ally"}),
        Relation.model_validate({"from": "constantine-i", "to": "venizelos", "kind": "ally"}),
    ]
    problems = validate(replace(corpus, relations=bad))
    assert any("unknown figure 'atlantis'" in p for p in problems)
    assert any("tied to itself" in p for p in problems)
    assert any("'constantine-i' -- 'venizelos' written 2 times" in p for p in problems)


def test_a_parent_born_after_the_child_is_rejected(corpus):
    backwards = Relation.model_validate(
        {"from": "constantine-i", "to": "george-i", "kind": "parent"}
    )
    problems = validate(replace(corpus, relations=[backwards]))
    assert any("not born before child" in p for p in problems)


def test_relations_index(client):
    body = client.get("/api/relations").json()
    assert {"from", "to", "kind"} <= body[0].keys()
    assert len(body) == 39
