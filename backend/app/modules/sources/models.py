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
