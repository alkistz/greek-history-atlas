"""Build data/atoms.geojson from content/atoms.yaml and the raw NUTS3 boundaries.

Run once; the output is committed so nothing downstream needs the network.

v0 dissolves whole NUTS3 units only. Sub-NUTS3 cuts come later, and when they do
they belong here rather than in the frontend.
"""

import json
import sys
from typing import Any

import yaml
from pyproj import Geod
from shapely.geometry import mapping, shape
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from atlas.paths import ATOMS_GEOJSON, ATOMS_YAML, NUTS3_RAW

GEOD = Geod(ellps="WGS84")
PRECISION = 6


def round_coords(obj: Any) -> Any:
    """Round every coordinate in a GeoJSON coordinate tree to PRECISION places."""
    if isinstance(obj, (int, float)):
        return round(obj, PRECISION)
    if isinstance(obj, (list, tuple)):
        return [round_coords(x) for x in obj]
    return obj


def oriented(geom):
    """Normalise to RFC 7946 winding: exterior counter-clockwise, holes clockwise.

    pyproj's geodesic area is signed and assumes this convention. Nuts2json does
    not guarantee it, and getting it wrong silently subtracts islands.
    """
    if geom.geom_type == "Polygon":
        return orient(geom, sign=1.0)
    if geom.geom_type == "MultiPolygon":
        from shapely.geometry import MultiPolygon

        return MultiPolygon([orient(p, sign=1.0) for p in geom.geoms])
    return geom


def area_km2(geom) -> float:
    area, _ = GEOD.geometry_area_perimeter(geom)
    return abs(area) / 1e6


def main() -> int:
    if not NUTS3_RAW.exists():
        print(f"missing {NUTS3_RAW}. Run `make fetch` first.", file=sys.stderr)
        return 1

    raw = json.loads(NUTS3_RAW.read_text())
    nuts: dict[str, Any] = {}
    for f in raw["features"]:
        code = f["properties"]["id"]
        if code.startswith("EL"):
            nuts[code] = shape(f["geometry"])
    print(f"loaded {len(nuts)} Greek NUTS3 units from {NUTS3_RAW.name}")

    atoms = yaml.safe_load(ATOMS_YAML.read_text())

    seen: dict[str, str] = {}
    features = []
    errors = []
    rows = []

    for a in atoms:
        aid = a["id"]
        members = a["nuts3"]

        missing = [c for c in members if c not in nuts]
        if missing:
            errors.append(f"atom {aid!r}: unknown NUTS3 codes {missing}")
            continue
        for c in members:
            if c in seen:
                errors.append(f"NUTS3 {c} claimed by both {seen[c]!r} and {aid!r}")
            seen[c] = aid

        geom = unary_union([nuts[c] for c in members])
        if not geom.is_valid:
            from shapely import make_valid

            print(f"  make_valid applied to {aid}")
            geom = make_valid(geom)
        geom = oriented(geom)

        km2 = area_km2(geom)
        rows.append((aid, km2, len(members)))

        features.append(
            {
                "type": "Feature",
                "id": aid,
                "properties": {
                    "id": aid,
                    "name": a["name"],
                    "nuts3": members,
                    "area_km2": round(km2, 1),
                },
                "geometry": round_coords(mapping(geom)),
            }
        )

    unassigned = sorted(set(nuts) - set(seen))
    if unassigned:
        errors.append(f"NUTS3 units assigned to no atom: {unassigned}")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    features.sort(key=lambda f: f["id"])
    out = {
        "type": "FeatureCollection",
        "features": features,
        "_meta": {
            "source": "Eurostat Nuts2json v2 / 2021 / 4326 / 03M",
            "licence": "Nuts2json EUPL 1.2; boundaries (c) EuroGeographics for the "
            "administrative boundaries",
            "note": "Whole NUTS3 units only. See README.md for known simplifications.",
        },
    }
    ATOMS_GEOJSON.parent.mkdir(parents=True, exist_ok=True)
    ATOMS_GEOJSON.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")))

    rows.sort(key=lambda r: -r[1])
    print()
    print(f"{'atom':22} {'km2':>10}  nuts3")
    print("-" * 44)
    for aid, km2, n in rows:
        print(f"{aid:22} {km2:10,.0f}  {n}")
    total = sum(r[1] for r in rows)
    print("-" * 44)
    print(f"{'TOTAL':22} {total:10,.0f}")
    print(f"{'published (2021)':22} {131957:10,.0f}")
    print(f"{'delta':22} {(total - 131957) / 131957 * 100:9.2f}%")
    print()
    print(f"wrote {ATOMS_GEOJSON} ({ATOMS_GEOJSON.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
