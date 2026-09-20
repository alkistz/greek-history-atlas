# Greek History Atlas

An interactive atlas of Greek history from 1821 to the present. The map redraws as
control of territory changes, and events are tied to the dates and places they happened.

This is **v0**: one working vertical slice, built to answer the only genuinely uncertain
question in the project, which is whether the atom model produces a map that looks right
and redraws convincingly.

## The corpus

127 events from the outbreak of the revolution to the Tempi disaster, 78 figures, 76
places, 32 instruments and 22 cited works. Every event and figure is written in both
English and Greek. `significance` ranks events 2 to 5 on what they changed: fifteen events
across two centuries are rated 5, meaning they changed the shape or the nature of the
state, and the scale is meant to stay that steep.

## The three ideas the project rests on

**Atoms.** An atom is an area whose sovereignty history is identical throughout the whole
period. Roughly nineteen of them cover Greece. Everything geographic is expressed as a set
of atoms rather than as drawn borders, so a border is never stored, only derived.

**Two-layer control.** A `sovereign` row and an `occupied` row may cover the same atom at
the same time. This is why 1941 to 1944 is drawn as hatching over the Greek fill rather
than as a change of colour: the Greek state remained sovereign while others occupied. A
year-slider over Wikipedia borders cannot express that, and it is the reason this exists.

**Regimes.** `control.yaml` says who held the ground; `regimes.yaml` says what the Greek
state itself was. The map needs the first and the corpus needs the second: the last date
on which control changes is 1960, twenty-one events fall after it, and a third of all
events happen in Athens, so territory stops telling them apart long before the corpus
ends. The regimes are an unbroken chain of half-open periods, contiguity enforced in
`validate.py`, which is what lets an event's regime be a lookup from its date with nothing
stored on any event -- the same bargain `regions.yaml` strikes with atoms.

## Running it

```sh
make setup     # uv sync, npm install
make fetch     # download the raw NUTS3 boundaries (once)
make atoms     # build data/atoms.geojson and data/context.geojson (output is committed)
make api       # backend on :8000
make web       # frontend on :5173
```

Then open http://localhost:5173.

`make export` writes the API to `frontend/static/api/` and `make build` produces the
deployable site in `frontend/build/`. See **Deploying** below.

## Layout

```
content/     the source of truth. YAML in git: atoms, polities, control, regimes, regions,
             instruments, places, sources as one file each; events/ and figures/ as one
             file per entry.
data/        raw boundary downloads (gitignored) and the built geometry (committed)
backend/     content pipeline and a read-only API. No database. `app/core` is shared
             plumbing; `app/modules/<name>` owns one domain each (models, crud, validate, router).
frontend/    SvelteKit, client-rendered. d3-geo, plain SVG. `static/api/` is the
             exported API (generated, committed); `build/` is the deployable site.
```

`content/` sits at the root rather than inside `backend/` because it belongs to neither
half. It feeds the frontend build directly through the static export.

There is no database. The corpus is a few hundred kilobytes, and the invariants a
PostGIS `EXCLUDE` constraint would have enforced are enforced in `backend/app/core/content.py` and each module's `validate.py`
at load time instead. **The app refuses to start on bad content.** If a database is ever
added it belongs downstream of the export, never between the content and the frontend.

## Known simplifications in v0

Atoms dissolve whole NUTS3 units, plus island groups cut off a mainland unit by bounding
box (Kythira, the Sporades, Imbros and Tenedos). Land frontiers that cut through a unit are
not modelled, so the following are wrong on purpose. None of them changes the model.

| what | why it is wrong |
|---|---|
| `sterea` uses modern boundaries | the 1832 Arta-Volos frontier cut across Fthiotida and Evrytania. Domokos and the northern Agrafa sit inside this atom but were Ottoman until 1881. This is the largest single error and puts the 1833 figure roughly 3% over the published one |
| `thessaly` includes Elassona | Elassona stayed Ottoman until 1912 |
| `arta-preveza` is one atom | Arta became Greek in 1881, Preveza in 1913. v0 treats both as 1881 |
| `samos-ikaria` is one atom | Ikaria declared itself a free state in July 1912 |
| `smyrna` is the whole İzmir province | the Sèvres zone was smaller |
| `cyprus` is whole | the 1974 partition needs a hand-drawn line |
| the revolution is static | Ibrahim's reconquest of most of the Peloponnese in 1825-27 is not modelled, so the insurgent extent does not move across the decade |
| occupation zones are atom-grained | the German zone actually included an Evros strip, a Thessaloniki-Chalkidiki strip, and only part of Crete |
| neighbours are modern | the land backdrop is drawn at present-day extent, uncoloured, with no borders |

Computed areas against published figures, as a check on the geometry rather than on the history:

| date | computed | published | delta |
|---|---|---|---|
| present day | 131,790 | 131,957 | -0.13% |
| 1914-01-01 | 120,479 | 120,308 | +0.14% |
| 1833-01-01 | 48,780 | 47,516 | +2.7% |

The first two show the NUTS3 approximation is sound. The third is the Fthiotida and
Evrytania problem described above, and it is the one worth fixing first.

## Deliberately not here yet

Sub-NUTS3 land cuts. A Cyprus split for 1974. Claims (numbers with citations) and
interpretations. TopoJSON and merged borders. Server-side rendering and prerendering. CI.

## Deploying

The deployed site has no server. Every route is a pure read off a corpus that changes only
when someone edits `content/`, so `make export` runs the real app through `TestClient` and
writes each response body verbatim to `frontend/static/api/`: 248 files, about 2.2 MB. The
whole build is 2.9 MB. `events.json` is 255 KB of that, because the ledger carries every
event's summary in both languages; if it starts to hurt, splitting the ledger from the
summaries is the first thing to try.

This removes the hosted process, not the backend. The same models, the same `validate.py`
invariants and the same serialiser still stand between the YAML and the browser; they run
once per deploy instead of once per boot. Bad content now fails the build rather than a
server nobody is watching.

One set of URLs works in both places. The frontend asks for `/api/events.json`; in
production that is a file, and in dev the Vite proxy strips the suffix and forwards to
FastAPI on :8000. `make api` is unchanged.

**Cloudflare Workers.** Pages still runs, but Cloudflare now directs new projects to
Workers with static assets, and a static site is the simplest case of it: no Worker script,
just the built directory. [`frontend/wrangler.jsonc`](frontend/wrangler.jsonc) is the whole
configuration.

```sh
npx wrangler login    # once
make deploy           # export, build, upload
```

For deploys on push instead, connect the repo under the Worker's Settings -> Builds:

| setting | value |
|---|---|
| root directory | `frontend` |
| build command | `npm run build` |
| deploy command | `npx wrangler deploy` |

The Worker's name in the dashboard must match `name` in `wrangler.jsonc`, or the build
fails.

`not_found_handling: "single-page-application"` serves the app shell for any path that is
not a real file, which is what makes `/events/<id>` work on a cold load. It also means a
missing id comes back as HTML with a 200 rather than a 404, so `src/lib/api.ts` checks the
content type before parsing and raises a proper not-found page. That is a property of
static hosting generally, not of Workers.

Nothing here is a one-way door. If readers ever need to write to this thing, the FastAPI
app deploys as it stands and the frontend points back at it.

## Data and licence

Boundaries from [Eurostat Nuts2json](https://github.com/eurostat/Nuts2json) v2, 2021
edition, EPSG:4326, 03M resolution (EUPL 1.2). Administrative boundaries
(c) EuroGeographics. Historical content in `content/` is original prose in English and
Greek, and every event and figure carries at least one citation into `sources.yaml`.
