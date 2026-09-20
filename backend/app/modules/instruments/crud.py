from app.core.content import Corpus
from app.modules.control.models import Control
from app.modules.events.models import Event
from app.modules.instruments.models import Instrument


def list_instruments(corpus: Corpus) -> list[Instrument]:
    return sorted(corpus.instruments, key=lambda i: i.signed)


def get_instrument(corpus: Corpus, instrument_id: str) -> Instrument | None:
    return next((i for i in corpus.instruments if i.id == instrument_id), None)


def control_rows_of(corpus: Corpus, instrument_id: str) -> list[Control]:
    return [r for r in corpus.control if r.instrument == instrument_id]


def events_citing(corpus: Corpus, instrument_id: str) -> list[Event]:
    return [e for e in corpus.events if e.instrument == instrument_id]
