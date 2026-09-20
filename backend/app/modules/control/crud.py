from datetime import date

from app.core.content import Corpus
from app.modules.control.models import Control


def list_control(corpus: Corpus) -> list[Control]:
    return corpus.control


def control_on(corpus: Corpus, on: date) -> list[Control]:
    return [c for c in corpus.control if c.covers(on)]


def epochs(corpus: Corpus) -> list[date]:
    """Every date on which any control row starts or ends.

    This is the complete set of dates on which the map changes: between two
    consecutive epochs the picture is identical.
    """
    ds: set[date] = set()
    for c in corpus.control:
        ds.add(c.start)
        if c.end is not None:
            ds.add(c.end)
    return sorted(ds)
