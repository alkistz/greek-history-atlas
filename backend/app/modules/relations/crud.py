from app.core.content import Corpus
from app.modules.relations.models import INVERSE, Relation


def list_relations(corpus: Corpus) -> list[Relation]:
    return list(corpus.relations)


def relations_of(corpus: Corpus, figure_id: str) -> list[tuple[str, str, Relation]]:
    """Every tie a figure has, as (other, what the other is to this figure, row).

    A tie is authored from one end only, so the half that was not written is
    derived here: on George I's page Constantine is his child, on Constantine's
    George is his parent, from the same row.
    """
    out = []
    for r in corpus.relations:
        if r.source == figure_id:
            out.append((r.target, INVERSE[r.kind], r))
        elif r.target == figure_id:
            out.append((r.source, r.kind, r))
    return out
