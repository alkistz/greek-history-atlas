"""Export the read API to static JSON under frontend/static/api/.

Every route is a pure read off a corpus that changes only when someone edits
content/, so the whole API is a few hundred kilobytes of files. Writing them at
build time removes the deployed server without removing the backend: the same
models, the same validation and the same serialiser still stand between the
YAML and the browser, they just run once per deploy instead of once per boot.

The export drives the real app through TestClient and writes each response body
verbatim, so it cannot drift from what `make api` serves. Output is committed,
like data/*.geojson, so deploying the frontend needs no Python.

Run `make export` after editing content/. `make check` fails if you forget.
"""

import re
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.content import Corpus
from app.core.dependencies import get_corpus
from app.core.paths import API_EXPORT, STATIC
from app.main import app

API = "/api"
PARAM = re.compile(r"\{[^}]+\}")

# Routes with a path parameter, and where their ids come from. A parameterised
# route that is not listed here fails the export rather than quietly going
# missing from the deployed site.
COLLECTIONS: dict[str, Callable[[Corpus], list[str]]] = {
    "/api/events/{event_id}": lambda c: [e.id for e in c.events],
    "/api/figures/{figure_id}": lambda c: [f.id for f in c.figures],
    "/api/instruments/{instrument_id}": lambda c: [i.id for i in c.instruments],
}


def plan(corpus: Corpus) -> tuple[list[str], list[str]]:
    """Every URL to export, expanded from the app's own route table.

    Read off the OpenAPI schema rather than a list here, so a new module's routes
    are exported the day they exist. (`app.routes` keeps included routers nested,
    and the schema is the flat, version-stable view of the same thing.)

    Returns the URLs and any parameterised paths it cannot expand.
    """
    urls: list[str] = []
    unknown: list[str] = []

    for path, operations in app.openapi()["paths"].items():
        if not path.startswith(API) or "get" not in operations:
            continue
        if "{" not in path:
            urls.append(path)
            continue
        ids = COLLECTIONS.get(path)
        if ids is None or len(PARAM.findall(path)) != 1:
            unknown.append(path)
            continue
        urls.extend(PARAM.sub(item_id, path) for item_id in ids(corpus))

    return urls, unknown


def destination(url: str) -> Path:
    """/api/events -> frontend/static/api/events.json, and /api/events/{id} below it."""
    return STATIC / f"{url.lstrip('/')}.json"


def main() -> int:
    # Bad content raises here, which is the point: the build fails, not the site.
    corpus = get_corpus()
    urls, unknown = plan(corpus)
    if unknown:
        for path in unknown:
            print(f"ERROR: cannot expand {path}; add it to COLLECTIONS", file=sys.stderr)
        return 1

    # Rebuilt from scratch, so a deleted event cannot linger as a stale file.
    shutil.rmtree(API_EXPORT, ignore_errors=True)

    written = 0
    with TestClient(app) as client:
        for url in urls:
            r = client.get(url)
            if r.status_code != 200:
                print(f"ERROR: {url} returned {r.status_code}", file=sys.stderr)
                return 1
            path = destination(url)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(r.content)  # verbatim: the API's own bytes
            written += len(r.content)

    print(f"wrote {len(urls)} files to {API_EXPORT} ({written:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
