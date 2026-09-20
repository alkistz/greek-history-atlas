from datetime import date

from app.core.content import Corpus
from app.modules.regimes.models import Regime


def list_regimes(corpus: Corpus) -> list[Regime]:
    return sorted(corpus.regimes, key=lambda r: r.start)


def get_regime(corpus: Corpus, regime_id: str) -> Regime | None:
    return next((r for r in corpus.regimes if r.id == regime_id), None)


def regime_on(corpus: Corpus, on: date) -> Regime | None:
    """The regime in force on a date.

    `None` only before the chain begins: there was no Greek state to have a form
    until the revolution made one, and saying so is better than inventing a row.
    """
    return next((r for r in corpus.regimes if r.covers(on)), None)
