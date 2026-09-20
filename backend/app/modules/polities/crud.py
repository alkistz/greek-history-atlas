from app.core.content import Corpus
from app.modules.polities.models import Polity


def list_polities(corpus: Corpus) -> list[Polity]:
    return corpus.polities


def get_polity(corpus: Corpus, polity_id: str) -> Polity | None:
    return next((p for p in corpus.polities if p.id == polity_id), None)
