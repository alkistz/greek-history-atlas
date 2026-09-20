"""Build data/atoms.geojson and data/context.geojson from content/atoms.yaml and
the raw NUTS3 boundaries.

Run once; both outputs are committed so nothing downstream needs the network.

Atoms are dissolved from whole NUTS3 units (`nuts3`) and, where a historical
frontier cuts an island group off a mainland unit, from polygon parts selected
by bounding box (`parts`). Sub-NUTS3 land cuts (Elassona, Domokos, Preveza) are
not supported here and remain known simplifications.

Context is the neutral land backdrop: every unit of the neighbouring countries
dissolved into one polygon and clipped to the widest map frame. It includes the
Greek units too, so an atom with no control row on a date simply vanishes into
the land rather than showing as a hole.
"""

import json
import sys
from collections import defaultdict
from typing import Any

import yaml
from pyproj import Geod
from shapely import make_valid
from shapely.geometry import MultiPolygon, Polygon, mapping, shape
from shapely.geometry.polygon import orient
from shapely.ops import clip_by_rect, unary_union

from app.core.paths import ATOMS_GEOJSON, ATOMS_YAML, CONTEXT_GEOJSON, NUTS3_RAW

GEOD = Geod(ellps="WGS84")
PRECISION = 6

# Everything drawn as neutral land. EL is included on purpose (see module docstring).
CONTEXT_COUNTRIES = ("EL", "AL", "MK", "BG", "TR", "IT", "RS", "ME", "CY")

# Union of the frontend's frames plus a one-degree margin, so no clipped edge is
# ever visible inside a frame. Kosovo is not in NUTS; its tip shows as sea.
CLIP_BBOX = (17.4, 33.2, 36.2, 43.4)

PUBLISHED_KM2 = 131_957  # Greece, 2021


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
        return MultiPolygon([orient(p, sign=1.0) for p in geom.geoms])
    return geom


def area_km2(geom) -> float:
    area, _ = GEOD.geometry_area_perimeter(geom)
    return abs(area) / 1e6


def polygons(geom) -> list[Polygon]:
    if geom.geom_type == "Polygon":
        return [geom]
    return list(geom.geoms)


def within(bounds, bbox) -> bool:
    w, s, e, n = bbox
    return bounds[0] >= w and bounds[1] >= s and bounds[2] <= e and bounds[3] <= n


def load_nuts() -> dict[str, list[Polygon]]:
    """Every NUTS3 unit as a list of polygon parts, keyed by code."""
    raw = json.loads(NUTS3_RAW.read_text())
    return {f["properties"]["id"]: polygons(shape(f["geometry"])) for f in raw["features"]}


def build_atoms(atoms: list[dict], nuts: dict[str, list[Polygon]]):
    """Assign polygon parts to atoms. Returns (features, rows, errors)."""
    remaining = {code: list(parts) for code, parts in nuts.items()}
    claimed: dict[str, str] = {}  # code -> atom, for whole units
    geoms: dict[str, list[Polygon]] = defaultdict(list)
    errors: list[str] = []

    # Parts first, so whole-unit atoms get what is left of a shared unit.
    for a in atoms:
        for part in a.get("parts", []):
            code, bbox = part["nuts3"], tuple(part["bbox"])
            if code not in remaining:
                errors.append(f"atom {a['id']!r}: unknown NUTS3 code {code}")
                continue
            picked = [p for p in remaining[code] if within(p.bounds, bbox)]
            if not picked:
                errors.append(f"atom {a['id']!r}: no parts of {code} inside bbox {bbox}")
                continue
            remaining[code] = [p for p in remaining[code] if p not in picked]
            geoms[a["id"]].extend(picked)
            print(f"  {a['id']}: {len(picked)} part(s) of {code} inside {bbox}")

    for a in atoms:
        for code in a.get("nuts3", []):
            if code not in remaining:
                errors.append(f"atom {a['id']!r}: unknown NUTS3 code {code}")
                continue
            if code in claimed:
                errors.append(f"NUTS3 {code} claimed by both {claimed[code]!r} and {a['id']!r}")
                continue
            claimed[code] = a["id"]
            geoms[a["id"]].extend(remaining.pop(code))

    unassigned = sorted(c for c in remaining if c.startswith("EL") and c not in claimed)
    if unassigned:
        errors.append(f"Greek NUTS3 units assigned to no atom: {unassigned}")

    features, rows = [], []
    for a in atoms:
        if a["id"] not in geoms:
            errors.append(f"atom {a['id']!r} has no geometry")
            continue
        geom = unary_union(geoms[a["id"]])
        if not geom.is_valid:
            print(f"  make_valid applied to {a['id']}")
            geom = make_valid(geom)
        geom = oriented(geom)
        km2 = area_km2(geom)
        external = bool(a.get("external", False))
        rows.append((a["id"], km2, external))
        features.append(
            {
                "type": "Feature",
                "id": a["id"],
                "properties": {
                    "id": a["id"],
                    "name": a["name"],
                    "nuts3": a.get("nuts3", []),
                    "external": external,
                    "area_km2": round(km2, 1),
                },
                "geometry": round_coords(mapping(geom)),
            }
        )
    features.sort(key=lambda f: f["id"])
    return features, rows, errors


def build_context(nuts: dict[str, list[Polygon]]) -> dict:
    parts = [
        clip_by_rect(p, *CLIP_BBOX)
        for code, ps in nuts.items()
        if code.startswith(CONTEXT_COUNTRIES)
        for p in ps
    ]
    land = unary_union([p for p in parts if not p.is_empty])
    land = make_valid(land)
    if land.geom_type == "GeometryCollection":
        land = unary_union([g for g in land.geoms if g.geom_type in ("Polygon", "MultiPolygon")])
    land = oriented(land)
    return {
        "type": "Feature",
        "id": "land",
        "properties": {"id": "land", "countries": list(CONTEXT_COUNTRIES), "clip": CLIP_BBOX},
        "geometry": round_coords(mapping(land)),
    }


def write(path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    print(f"wrote {path} ({path.stat().st_size:,} bytes)")


def report(rows: list[tuple[str, float, bool]]) -> None:
    print()
    print(f"{'atom':22} {'km2':>10}")
    print("-" * 34)
    for aid, km2, external in sorted(rows, key=lambda r: (r[2], -r[1])):
        print(f"{aid:22} {km2:10,.0f}{'  (external)' if external else ''}")
    total = sum(km2 for _, km2, external in rows if not external)
    print("-" * 34)
    print(f"{'GREECE (non-external)':22} {total:10,.0f}")
    print(f"{'published (2021)':22} {PUBLISHED_KM2:10,.0f}")
    print(f"{'delta':22} {(total - PUBLISHED_KM2) / PUBLISHED_KM2 * 100:9.2f}%")
    print()


def main() -> int:
    if not NUTS3_RAW.exists():
        print(f"missing {NUTS3_RAW}. Run `make fetch` first.", file=sys.stderr)
        return 1

    nuts = load_nuts()
    by_country = defaultdict(int)
    for code in nuts:
        by_country[code[:2]] += 1
    counts = ", ".join(f"{c} {by_country[c]}" for c in CONTEXT_COUNTRIES)
    print(f"loaded {len(nuts)} NUTS3 units; {counts}")

    atoms = yaml.safe_load(ATOMS_YAML.read_text())
    features, rows, errors = build_atoms(atoms, nuts)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    write(
        ATOMS_GEOJSON,
        {
            "type": "FeatureCollection",
            "features": features,
            "_meta": {
                "source": "Eurostat Nuts2json v2 / 2021 / 4326 / 03M",
                "licence": "Nuts2json EUPL 1.2; boundaries (c) EuroGeographics for the "
                "administrative boundaries",
                "note": "Whole NUTS3 units, plus island groups cut by bounding box. "
                "See README.md for known simplifications.",
            },
        },
    )
    write(CONTEXT_GEOJSON, {"type": "FeatureCollection", "features": [build_context(nuts)]})
    report(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
