from app.core.content import Corpus
from app.modules.events.models import Event
from app.modules.figures.models import Figure


def list_figures(corpus: Corpus) -> list[Figure]:
    return sorted(corpus.figures, key=lambda f: f.born.date if f.born else f.name.en)


def get_figure(corpus: Corpus, figure_id: str) -> Figure | None:
    return next((f for f in corpus.figures if f.id == figure_id), None)


def events_of(corpus: Corpus, figure_id: str) -> list[tuple[Event, str]]:
    """Every event the figure took part in, with their role, in date order.

    Links are authored on the event; this is the derived inverse."""
    out = [(e, p.role) for e in corpus.events for p in e.figures if p.figure == figure_id]
    return sorted(out, key=lambda pair: pair[0].period[0])
