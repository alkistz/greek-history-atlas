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

ATOMS_YAML = CONTENT / "atoms.yaml"
POLITIES_YAML = CONTENT / "polities.yaml"
CONTROL_YAML = CONTENT / "control.yaml"
EVENTS_YAML = CONTENT / "events.yaml"

NUTS3_RAW = RAW / "nutsrg_3.json"
ATOMS_GEOJSON = DATA / "atoms.geojson"
