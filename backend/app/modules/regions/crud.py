from app.core.content import Corpus
from app.modules.regions.models import Region


def list_regions(corpus: Corpus) -> list[Region]:
    return corpus.regions


def get_region(corpus: Corpus, region_id: str) -> Region | None:
    return next((r for r in corpus.regions if r.id == region_id), None)


def index(corpus: Corpus) -> dict[str, str]:
    """Atom id -> region id. A partition, so every atom appears exactly once."""
    return {atom: region.id for region in corpus.regions for atom in region.atoms}
