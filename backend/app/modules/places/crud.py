from datetime import date

from app.core.content import Corpus
from app.core.models import LangText
from app.core.periods import covers
from app.modules.places.models import Place


def list_places(corpus: Corpus) -> list[Place]:
    return corpus.places


def get_place(corpus: Corpus, place_id: str) -> Place | None:
    return next((p for p in corpus.places if p.id == place_id), None)


def name_on(place: Place, on: date) -> LangText:
    """The name in force on a date. Falls back to the first name listed."""
    for n in place.names:
        if covers(n.start or date.min, n.end, on):
            return n.name
    return place.names[0].name


def resolve(corpus: Corpus, place_id: str | None, on: date) -> dict | None:
    place = get_place(corpus, place_id) if place_id else None
    if place is None:
        return None
    return {
        "id": place.id,
        "kind": place.kind,
        "lon": place.lon,
        "lat": place.lat,
        "atom": place.atom,
        "name": name_on(place, on).model_dump(mode="json"),
    }
