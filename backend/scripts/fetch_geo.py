"""Download the raw boundaries. Run once; the output is gitignored.

Eurostat Nuts2json, 2021 edition, EPSG:4326, 03M resolution. 03M rather than the
coarser 10M because this atlas is mostly Aegean coastline: at 10M, Zakynthos is an
eleven-sided polygon.

Also every OpenHistoricalMap relation that content/cuts.yaml names, as Overpass JSON
with geometry: the historical frontiers that split a NUTS3 unit. A file already
present is kept, so a rebuild uses the same lines until it is deleted and fetched
again.
"""

import sys
import urllib.parse
import urllib.request

import yaml

from app.core.paths import CUTS_YAML, NUTS3_RAW, RAW, ohm_raw

URL = (
    "https://raw.githubusercontent.com/eurostat/Nuts2json/master/pub/v2/2021/4326/03M/nutsrg_3.json"
)
OVERPASS = "https://overpass-api.openhistoricalmap.org/api/interpreter"
# Overpass refuses the default urllib agent.
AGENT = "greek-history-atlas/0.1 (build script; https://github.com/alkistz/greek-history-atlas)"


def fetch(url: str, path, data: bytes | None = None) -> None:
    if path.exists():
        print(f"already present: {path} ({path.stat().st_size:,} bytes)")
        return
    print(f"fetching {url}")
    req = urllib.request.Request(url, data=data, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=180) as r:
        body = r.read()
    path.write_bytes(body)
    print(f"wrote {path} ({len(body):,} bytes)")


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    fetch(URL, NUTS3_RAW)
    for cut in yaml.safe_load(CUTS_YAML.read_text()):
        if "ohm" not in cut:
            continue
        query = f"[out:json][timeout:120];relation({cut['ohm']});out geom meta;"
        fetch(OVERPASS, ohm_raw(cut["ohm"]), urllib.parse.urlencode({"data": query}).encode())
    return 0


if __name__ == "__main__":
    sys.exit(main())
