"""Read-only API over the content files.

Every route is a pure read off an in-memory corpus loaded once at startup.
There is no database and no request-path computation worth the name.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.dependencies import get_corpus
from app.modules.atoms.router import router as atoms_router
from app.modules.control.router import router as control_router
from app.modules.events.router import router as events_router
from app.modules.meta.router import router as meta_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load eagerly so bad content fails the boot, not the first request.
    get_corpus()
    yield


app = FastAPI(
    title="after1821",
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
app.include_router(atoms_router, prefix=API)
app.include_router(meta_router, prefix=API)
app.include_router(control_router, prefix=API)
app.include_router(events_router, prefix=API)


@app.get("/")
def read_root():
    return {"message": "after1821 api"}
