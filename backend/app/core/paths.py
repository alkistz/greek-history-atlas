"""Filesystem layout.

Resolved from this file rather than from the working directory, so the backend
behaves the same whether it is started from the repo root, from ``backend/``,
or by an editor that picks its own cwd.
"""

from pathlib import Path

# app/core/paths.py -> core -> app -> backend -> repo root
ROOT = Path(__file__).resolve().parents[3]

CONTENT = ROOT / "content"
DATA = ROOT / "data"
RAW = DATA / "raw"

# Where `scripts/export_static.py` writes the API as files the frontend build serves.
STATIC = ROOT / "frontend" / "static"
API_EXPORT = STATIC / "api"

# Reference tables: one file each.
ATOMS_YAML = CONTENT / "atoms.yaml"
POLITIES_YAML = CONTENT / "polities.yaml"
CONTROL_YAML = CONTENT / "control.yaml"
INSTRUMENTS_YAML = CONTENT / "instruments.yaml"
PLACES_YAML = CONTENT / "places.yaml"
SOURCES_YAML = CONTENT / "sources.yaml"

# Prose-carrying entries: one file per entry.
EVENTS_DIR = CONTENT / "events"
FIGURES_DIR = CONTENT / "figures"

NUTS3_RAW = RAW / "nutsrg_3.json"
ATOMS_GEOJSON = DATA / "atoms.geojson"
CONTEXT_GEOJSON = DATA / "context.geojson"
