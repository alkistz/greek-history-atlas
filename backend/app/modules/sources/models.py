from datetime import date
from typing import Literal

from app.core.models import Strict

SourceKind = Literal["book", "chapter", "article", "archive", "dataset", "web", "statistical"]


class Source(Strict):
    id: str
    kind: SourceKind
    title: str
    author: str | None = None
    year: int | None = None
    publisher: str | None = None
    url: str | None = None
    # A URL rots; an ISBN or a DOI does not. Both where both exist.
    isbn: str | None = None
    doi: str | None = None
    # When a web source was last read, since the page may change under the citation.
    accessed: date | None = None
