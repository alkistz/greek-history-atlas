"""Read-only API over the content files.

Every route is a pure read off an in-memory corpus loaded once at startup.
There is no database and no request-path computation worth the name.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.dependencies import get_corpus
from app.modules.atoms.router import router as atoms_router
from app.modules.control.router import router as control_router
from app.modules.events.router import router as events_router
from app.modules.figures.router import router as figures_router
from app.modules.figures.validate import lifetime_warnings
from app.modules.instruments.router import router as instruments_router
from app.modules.meta.router import router as meta_router
from app.modules.places.router import router as places_router
from app.modules.regions.router import router as regions_router
from app.modules.sources.router import router as sources_router

log = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load eagerly so bad content fails the boot, not the first request.
    corpus = get_corpus()
    for warning in lifetime_warnings(corpus):
        log.warning("content: %s", warning)
    yield


app = FastAPI(
    title="Greek History Atlas",
    description="An atlas of Greek history from 1821.",
    version="0.1.0",
    lifespan=lifespan,
)

# The Vite dev server. Not needed once the frontend proxies /api, but harmless
# and it keeps the API usable from a scratch page.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

API = "/api"
for router in (
    atoms_router,
    meta_router,
    control_router,
    events_router,
    figures_router,
    instruments_router,
    places_router,
    regions_router,
    sources_router,
):
    app.include_router(router, prefix=API)


@app.get("/")
def read_root():
    return {"message": "greek history atlas api"}
