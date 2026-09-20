from app.core.content import Corpus
from app.core.models import Citation
from app.modules.sources.models import Source


def list_sources(corpus: Corpus) -> list[Source]:
    return sorted(corpus.sources, key=lambda s: (s.author or "", s.year or 0))


def get_source(corpus: Corpus, source_id: str) -> Source | None:
    return next((s for s in corpus.sources if s.id == source_id), None)


def resolve_citations(corpus: Corpus, citations: list[Citation]) -> list[dict]:
    """Citations with the source fields folded in, for detail responses."""
    out = []
    for cit in citations:
        source = get_source(corpus, cit.id)
        if source is not None:
            out.append({**source.model_dump(mode="json"), "locator": cit.locator})
    return out
