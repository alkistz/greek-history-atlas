# after1821

An interactive atlas of Greek history from 1821 to the present. The map redraws as
control of territory changes, and events are tied to the dates and places they happened.

This is **v0**: one working vertical slice, built to answer the only genuinely uncertain
question in the project, which is whether the atom model produces a map that looks right
and redraws convincingly.

## The two ideas the project rests on

**Atoms.** An atom is an area whose sovereignty history is identical throughout the whole
period. Roughly nineteen of them cover Greece. Everything geographic is expressed as a set
of atoms rather than as drawn borders, so a border is never stored, only derived.

**Two-layer control.** A `sovereign` row and an `occupied` row may cover the same atom at
the same time. This is why 1941 to 1944 is drawn as hatching over the Greek fill rather
than as a change of colour: the Greek state remained sovereign while others occupied. A
year-slider over Wikipedia borders cannot express that, and it is the reason this exists.

## Running it

```sh
make setup     # uv sync, npm install
make fetch     # download the raw NUTS3 boundaries (once)
make atoms     # build data/atoms.geojson (once, output is committed)
make api       # backend on :8000
make web       # frontend on :5173
```

Then open http://localhost:5173.

## Layout

```
content/     the source of truth: atoms, polities, control, events. YAML in git.
data/        raw boundary downloads (gitignored) and the built atom geometry (committed)
backend/     content pipeline and a read-only API. No database. `app/core` is shared
             plumbing; `app/modules/<name>` owns one domain each (models, crud, validate, router).
frontend/    SvelteKit, dev mode. d3-geo, plain SVG.
```

`content/` sits at the root rather than inside `backend/` because it belongs to neither
half. When a static export path arrives, content will feed the frontend build directly.

There is no database. The corpus is a few hundred kilobytes, and the invariants a
PostGIS `EXCLUDE` constraint would have enforced are enforced in `backend/app/core/content.py` and each module's `validate.py`
at load time instead. **The app refuses to start on bad content.** If a database is ever
added it belongs downstream of the export, never between the content and the frontend.

## Known simplifications in v0

v0 dissolves whole NUTS3 units. Several historical frontiers cut across modern ones, so the
following are wrong on purpose. Each is fixed later by a sub-NUTS3 cut or an extra atom,
and none of them changes the model.

| what | why it is wrong |
|---|---|
| `attica` includes Kythira | Kythira was Ionian, so British until 1864, not Greek in 1832 |
| `sterea` uses modern boundaries | the 1832 Arta-Volos frontier cut across Fthiotida and Evrytania. Domokos and the northern Agrafa sit inside this atom but were Ottoman until 1881. This is the largest single error and puts the 1833 figure roughly 3% over the published one |
| `thessaly` includes Elassona | Elassona stayed Ottoman until 1912 |
| `arta-preveza` is one atom | Arta became Greek in 1881, Preveza in 1913. v0 treats both as 1881 |
| `samos-ikaria` is one atom | Ikaria declared itself a free state in July 1912 |
| the revolution is static | Ibrahim's reconquest of most of the Peloponnese in 1825-27 is not modelled, so the insurgent extent does not move across the decade |
| occupation zones are atom-grained | the German zone actually included an Evros strip, a Thessaloniki-Chalkidiki strip, and only part of Crete |
| no neighbours | surrounding countries are not drawn at all |

Computed areas against published figures, as a check on the geometry rather than on the history:

| date | computed | published | delta |
|---|---|---|---|
| present day | 131,790 | 131,957 | -0.13% |
| 1914-01-01 | 120,479 | 120,308 | +0.14% |
| 1833-01-01 | 48,806 | 47,516 | +2.7% |

The first two show the NUTS3 approximation is sound. The third is the Fthiotida and
Evrytania problem described above, and it is the one worth fixing first.

## Deliberately not here yet

Sub-NUTS3 cuts. Hand-drawn atoms outside the modern state (the Smyrna zone, Eastern Thrace,
Imbros and Tenedos, Northern Epirus, a Cyprus split for 1974). Sources, claims and
interpretations. The Greek text. TopoJSON and merged borders. Server-side rendering,
prerendering, routing and per-event pages. CI.

## Data and licence

Boundaries from [Eurostat Nuts2json](https://github.com/eurostat/Nuts2json) v2, 2021
edition, EPSG:4326, 03M resolution (EUPL 1.2). Administrative boundaries
(c) EuroGeographics. Historical content in `content/` is original prose; event summaries
carry no citations yet, which is a gap to close rather than a position.
