"""Download the raw NUTS3 boundaries. Run once; the output is gitignored.

Eurostat Nuts2json, 2021 edition, EPSG:4326, 03M resolution. 03M rather than the
coarser 10M because this atlas is mostly Aegean coastline: at 10M, Zakynthos is an
eleven-sided polygon.
"""

import sys
import urllib.request

from app.core.paths import NUTS3_RAW, RAW

URL = (
    "https://raw.githubusercontent.com/eurostat/Nuts2json/master/pub/v2/2021/4326/03M/nutsrg_3.json"
)


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    if NUTS3_RAW.exists():
        print(f"already present: {NUTS3_RAW} ({NUTS3_RAW.stat().st_size:,} bytes)")
        return 0
    print(f"fetching {URL}")
    with urllib.request.urlopen(URL, timeout=60) as r:
        body = r.read()
    NUTS3_RAW.write_bytes(body)
    print(f"wrote {NUTS3_RAW} ({len(body):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
