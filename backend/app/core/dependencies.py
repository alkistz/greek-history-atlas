"""FastAPI dependencies.

The corpus is loaded once per process and shared. `CorpusDep` is the only way
routers reach it, so swapping the source later (a static export, a database) is
a one-line change here.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.core.content import Corpus, load


@lru_cache(maxsize=1)
def get_corpus() -> Corpus:
    return load()


CorpusDep = Annotated[Corpus, Depends(get_corpus)]
