from typing import Any

from app.core.content import Corpus
from app.modules.atoms.models import Atom


def list_atoms(corpus: Corpus) -> list[Atom]:
    return corpus.atoms


def get_atom(corpus: Corpus, atom_id: str) -> Atom | None:
    return next((a for a in corpus.atoms if a.id == atom_id), None)


def geojson(corpus: Corpus) -> dict[str, Any]:
    """The atom geometry as a GeoJSON FeatureCollection."""
    return corpus.geojson
