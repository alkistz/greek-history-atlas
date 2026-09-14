# after1821 — build plan

A bilingual (EL/EN) interactive atlas of Greek history from 1821 to the present.
Events are tied to a map that redraws itself as control of territory changes.

This file is the working specification. It lives at the repo root. Work top to bottom.
Each phase has acceptance criteria; do not move on until they pass.

Working name: `after1821`. Rename freely, it appears only in the package names and the site title.

---

## Ground rules

1. **Content lives in git, not in the database.** YAML files under `content/` are the source
   of truth. Postgres is a derived read model and an authoring workbench. If the database is
   dropped, `make ingest` rebuilds it from the repo.
2. **The database enforces historical consistency.** Two states cannot hold the same ground as
   sovereign at the same moment. That is a constraint, not a convention.
3. **Every number has a citation.** Death tolls, populations and areas are `claim` rows with a
   `source_id`, never prose in an event summary.
4. **The public site is static.** No database in the request path for v1.
5. **Simple first.** Hand-build what can be hand-built. The automated version comes later or never.

### Do not build in v1

No auth, no user accounts, no admin UI, no CMS, no comments, no search backend, no MapLibre,
no vector tiles, no Docker for the frontend, no GraphQL, no Celery, no Redis.
If a task below seems to need one of these, the task is wrong. Stop and flag it.

---

## Repo layout

```
after1821/
├── CLAUDE.md
├── TODO.md                      # this file
├── Makefile
├── docker-compose.yml           # postgis only
├── .pre-commit-config.yaml
├── content/                     # source of truth
│   ├── polities.yaml
│   ├── instruments.yaml
│   ├── atoms.yaml               # atom labels + NUTS3 composition rules
│   ├── control.yaml             # who held what, when
│   ├── sources.yaml
│   ├── places/*.yaml
│   └── events/*.yaml            # one file per event
├── apps/
│   ├── api/                     # FastAPI + SQLAlchemy + Alembic
│   │   ├── pyproject.toml
│   │   ├── alembic/
│   │   └── src/after1821/
│   │       ├── db/              # models, session
│   │       ├── schemas/         # Pydantic: ingest + API response
│   │       ├── ingest/          # YAML -> Postgres
│   │       ├── geo/             # atom building, TopoJSON export
│   │       ├── export/          # build-time static dump
│   │       └── api/             # routers
│   └── web/                     # SvelteKit 2 + Svelte 5
│       ├── package.json
│       ├── svelte.config.js
│       ├── src/
│       │   ├── lib/
│       │   │   ├── map/
│       │   │   ├── tokens.css
│       │   │   └── i18n/
│       │   └── routes/[[lang]]/
│       └── static/data/         # build-time output lands here
└── data/
    ├── raw/                     # downloaded boundary sources, gitignored
    └── derived/                 # atoms.geojson, committed
```

---

# PHASE 0 — Repo and tooling

- [ ] `git init`, MIT or CC-BY-SA licence (content and code licensed separately; content CC-BY-SA 4.0)
- [ ] Python toolchain with **uv**. `apps/api/pyproject.toml`, Python 3.12.
      Deps: `fastapi`, `uvicorn[standard]`, `sqlalchemy>=2.0`, `geoalchemy2`, `alembic`,
      `psycopg[binary]`, `pydantic>=2`, `pydantic-settings`, `pyyaml`, `shapely`, `typer`.
      Dev: `pytest`, `pytest-asyncio`, `ruff`, `mypy`, `httpx`.
- [ ] JS toolchain with **pnpm**, workspace at root (`pnpm-workspace.yaml` listing `apps/web`)
- [ ] `docker-compose.yml` with a single service: `postgis/postgis:16-3.4`, port 5432,
      volume for persistence, db `after1821`
- [ ] `Makefile` with: `db-up`, `db-down`, `migrate`, `ingest`, `export`, `api`, `web`,
      `test`, `lint`, `reset` (drop, migrate, ingest)
- [ ] `.pre-commit-config.yaml`: ruff format + ruff check + mypy on `apps/api`, prettier on `apps/web`
- [ ] `.env.example` with `DATABASE_URL=postgresql+psycopg://after1821:dev@localhost:5432/after1821`
- [ ] Write `CLAUDE.md` (content sketched at the bottom of this file)

**Acceptance:** `make db-up && make migrate` succeeds on a clean clone. `make lint` passes.

---

# PHASE 1 — Database schema

All migrations via Alembic. One migration per logical group so they are reviewable.

- [ ] `alembic init`, configure to read `DATABASE_URL`, set `compare_type=True`
- [ ] Migration 001: enable extensions `postgis`, `btree_gist` (btree_gist is required for the
      EXCLUDE constraint to mix `=` on scalars with `&&` on a range)
- [ ] Migration 002: `polity`, `instrument`

```sql
CREATE TABLE polity (
  id        text PRIMARY KEY,           -- 'gr-kingdom', 'ottoman', 'gr-republic-3'
  name      jsonb NOT NULL,             -- {"en": "...", "el": "..."}
  period    daterange NOT NULL,
  succeeds  text REFERENCES polity(id),
  kind      text NOT NULL CHECK (kind IN
              ('state','empire','protectorate','occupation','autonomous','de_facto')),
  CONSTRAINT polity_name_has_en CHECK (name ? 'en')
);

CREATE TABLE instrument (
  id      text PRIMARY KEY,             -- 'treaty-lausanne-1923', 'london-protocol-1830'
  title   jsonb NOT NULL,
  kind    text NOT NULL CHECK (kind IN ('treaty','protocol','law','convention','armistice','decree')),
  signed  date,
  in_force_from date,
  source_id text REFERENCES source(id)  -- add FK in a later migration if ordering bites
);
```

- [ ] Migration 003: `atom`

```sql
CREATE TABLE atom (
  id       text PRIMARY KEY,            -- 'thrace-west', 'dodecanese', 'elassona'
  name     jsonb NOT NULL,
  geom     geometry(MultiPolygon, 4326) NOT NULL,
  area_km2 numeric GENERATED ALWAYS AS (ST_Area(geom::geography)/1e6) STORED,
  note     text
);
CREATE INDEX atom_geom_gix ON atom USING gist (geom);
```

- [ ] Migration 004: `control`, the load-bearing table

```sql
CREATE TYPE control_kind AS ENUM
  ('sovereign','occupied','administered','mandated','autonomous','disputed','claimed');

CREATE TABLE control (
  id            bigserial PRIMARY KEY,
  atom_id       text NOT NULL REFERENCES atom(id) ON DELETE CASCADE,
  polity_id     text NOT NULL REFERENCES polity(id),
  kind          control_kind NOT NULL,
  period        daterange NOT NULL,
  instrument_id text REFERENCES instrument(id),
  note          text,
  CONSTRAINT control_no_overlap
    EXCLUDE USING gist (atom_id WITH =, kind WITH =, period WITH &&)
);
CREATE INDEX control_period_gix ON control USING gist (period);
CREATE INDEX control_lookup ON control (polity_id, kind);
```

Note the constraint is scoped by `kind`, deliberately. A `sovereign` row and an `occupied`
row over the same atom at the same time is exactly what 1941 to 1944 needs.

- [ ] Migration 005: `source`, `place`, `place_name`

```sql
CREATE TABLE source (
  id        text PRIMARY KEY,           -- 'clogg-2021', 'gsa-arch-1821-045'
  kind      text NOT NULL CHECK (kind IN ('book','chapter','article','archive','dataset','web','statistical')),
  author    text, title text NOT NULL, year int, publisher text,
  url text, archive_ref text, lang text, licence text
);

CREATE TABLE place (
  id   text PRIMARY KEY,                -- 'smyrna', 'messolonghi'
  geom geometry(Point,4326) NOT NULL,
  kind text CHECK (kind IN ('city','town','village','battlefield','island','region','building','sea'))
);
CREATE INDEX place_geom_gix ON place USING gist (geom);

CREATE TABLE place_name (
  id       bigserial PRIMARY KEY,
  place_id text NOT NULL REFERENCES place(id) ON DELETE CASCADE,
  name     text NOT NULL,
  lang     text NOT NULL,               -- 'el','en','tr','it'
  period   daterange NOT NULL,
  official boolean NOT NULL DEFAULT true
);
```

- [ ] Migration 006: `event`, `theme`, `event_theme`, `event_source`, `event_link`

```sql
CREATE TABLE event (
  id            text PRIMARY KEY,       -- 'exodus-messolonghi'
  title         jsonb NOT NULL,
  summary       jsonb NOT NULL,
  period        daterange NOT NULL,     -- a single day is [d, d+1)
  precision     text NOT NULL CHECK (precision IN ('day','month','season','year','span','circa')),
  as_written    jsonb,                  -- {"date":"1826-04-10","calendar":"julian","display":{"el":"...","en":"..."}}
  place_id      text REFERENCES place(id),
  polity_id     text REFERENCES polity(id),
  instrument_id text REFERENCES instrument(id),
  significance  smallint NOT NULL CHECK (significance BETWEEN 1 AND 5),
  CONSTRAINT event_title_has_en CHECK (title ? 'en' AND title ? 'el'),
  CONSTRAINT event_summary_has_both CHECK (summary ? 'en' AND summary ? 'el')
);
CREATE INDEX event_period_gix ON event USING gist (period);

CREATE TABLE theme (id text PRIMARY KEY, name jsonb NOT NULL, colour text NOT NULL);
CREATE TABLE event_theme (event_id text REFERENCES event(id) ON DELETE CASCADE,
                          theme_id text REFERENCES theme(id), PRIMARY KEY (event_id, theme_id));
CREATE TABLE event_source (event_id text REFERENCES event(id) ON DELETE CASCADE,
                           source_id text REFERENCES source(id), locator text,
                           PRIMARY KEY (event_id, source_id));

CREATE TYPE link_kind AS ENUM
  ('causes','enables','precedes','culminates_in','reverses','responds_to','commemorates');
CREATE TABLE event_link (
  src text REFERENCES event(id) ON DELETE CASCADE,
  dst text REFERENCES event(id) ON DELETE CASCADE,
  kind link_kind NOT NULL,
  note jsonb,
  PRIMARY KEY (src, dst, kind),
  CONSTRAINT no_self_link CHECK (src <> dst)
);
```

- [ ] Migration 007: `claim`, `interpretation`

```sql
CREATE TABLE claim (
  id        bigserial PRIMARY KEY,
  event_id  text REFERENCES event(id) ON DELETE CASCADE,
  atom_id   text REFERENCES atom(id),        -- for area/population claims not tied to an event
  measure   text NOT NULL,                   -- 'deaths','displaced','turnout_pct','population','area_km2','refugees'
  low numeric, high numeric, point numeric,
  unit      text,
  as_of     date,
  source_id text NOT NULL REFERENCES source(id),
  note      jsonb,
  CONSTRAINT claim_has_a_value CHECK (low IS NOT NULL OR point IS NOT NULL),
  CONSTRAINT claim_range_ordered CHECK (low IS NULL OR high IS NULL OR low <= high),
  CONSTRAINT claim_has_a_subject CHECK (event_id IS NOT NULL OR atom_id IS NOT NULL)
);

CREATE TABLE interpretation (
  id        text PRIMARY KEY,
  event_id  text NOT NULL REFERENCES event(id) ON DELETE CASCADE,
  school    text NOT NULL,                   -- 'orthodox','revisionist','post-revisionist','nationalist','marxist'
  summary   jsonb NOT NULL,
  source_id text NOT NULL REFERENCES source(id)
);
```

**Acceptance:**
- `make migrate` runs clean on an empty database and `alembic downgrade base` reverses it.
- A test inserts two overlapping `sovereign` control rows for one atom and asserts an
  `IntegrityError`. A test inserts a `sovereign` and an `occupied` row over the same atom and
  period and asserts both succeed.

---

# PHASE 2 — Atoms (the geometry)

An **atom** is any area whose sovereignty history is identical across the whole period.
Build these by hand. Do not attempt an automated boundary-arrangement overlay; it is a
research project and this list is short enough to audit by eye.

- [ ] Download Eurostat Nuts2json NUTS3 at 10M resolution, 4326, 2021 edition, into `data/raw/`.
      URL pattern: `https://raw.githubusercontent.com/eurostat/Nuts2json/master/pub/v2/2021/4326/10M/nutsrg_3.json`
- [ ] Write `content/atoms.yaml`. Each atom is either a list of NUTS3 ids to dissolve, or a
      reference to a hand-drawn polygon in `data/derived/manual/*.geojson`.

Atom list for v1 (roughly 29). Build exactly these:

| atom id | composition | note |
|---|---|---|
| `peloponnese` | EL651, EL652, EL653, EL632, EL633 | 1832 core |
| `attica` | EL301–EL306, EL307 **minus Kythira** | 1832 core |
| `sterea-south` | EL641, EL643, EL644, EL645 | 1832 core |
| `evvoia` | EL642 | 1832 core |
| `aitoloakarnania` | EL631 | 1832 core |
| `cyclades` | EL422 | 1832 core |
| `sporades` | Skiathos, Skopelos, Alonnisos, Skyros — split out of EL613 | Greek 1832, **not** 1881 |
| `ionian` | EL621, EL622, EL623, EL624 | 1864 |
| `kythira` | split out of EL307 | Ionian, so 1864 **not** 1832 |
| `thessaly` | EL611, EL612 minus Elassona, EL613 minus Sporades | 1881 |
| `elassona` | split out of EL612 | Ottoman until 1912 |
| `arta` | eastern part of EL541 | 1881 |
| `preveza` | western part of EL541 | 1913 |
| `epirus-south` | EL542, EL543 | 1913 |
| `macedonia-west` | EL531, EL532, EL533 | 1913 |
| `macedonia-central` | EL521–EL527 | 1913 |
| `macedonia-east` | EL514, EL515 | 1913 |
| `thrace-west` | EL511, EL512, EL513 | 1920 |
| `crete` | EL431–EL434 | autonomous 1898, Greek 1913 |
| `lesvos-limnos` | EL411 | 1912 |
| `chios` | EL413 | 1912 |
| `samos` | split out of EL412 | autonomous principality 1834–1912 |
| `ikaria` | split out of EL412 | self-declared free state July 1912 |
| `dodecanese` | EL421 minus Kastellorizo | Ottoman → Italian 1912 → Greek 1947 |
| `kastellorizo` | split out of EL421 | French occupation 1915–21 |
| `thrace-east` | hand-drawn | Greek 1920–1922 only |
| `smyrna-zone` | hand-drawn | Greek administration 1919–1922 |
| `imbros-tenedos` | hand-drawn | Greek occupation 1912–1923 |
| `northern-epirus` | hand-drawn | Greek occupation 1914, 1916–17, 1940–41 |
| `cyprus` | from Nuts2json country layer | never Greek; needed for 1974 |

- [ ] Implement `after1821.geo.build_atoms`: reads `content/atoms.yaml`, dissolves NUTS3 features
      with `shapely.union_all`, loads hand-drawn GeoJSON, writes `data/derived/atoms.geojson`
- [ ] The sub-NUTS3 splits (Kythira, Sporades, Elassona, Arta/Preveza, Samos/Ikaria, Kastellorizo)
      need either LAU boundaries or a hand-drawn cut line. Prefer a hand-drawn cut line committed
      as GeoJSON with a comment naming the historical boundary it approximates.
- [ ] `make ingest` loads `atoms.geojson` into the `atom` table
- [ ] Commit `data/derived/atoms.geojson`. It is small and it is the thing everything else rests on.

**Acceptance:**
- `SELECT count(*) FROM atom` returns 29 or whatever the final list is.
- `SELECT ST_IsValid(geom) FROM atom` is true for every row. Run `ST_MakeValid` in the builder if not.
- The union of all present-day Greek atoms is within 1% of 131,957 km².
- No two atoms overlap: `SELECT a.id, b.id FROM atom a JOIN atom b ON a.id < b.id AND ST_Overlaps(a.geom, b.geom)` returns zero rows. Allow shared boundaries, forbid overlapping interiors.

---

# PHASE 3 — Control (who held what, when)

- [ ] Write `content/polities.yaml`: ottoman, gr-provisional (1821–1832), gr-kingdom (1832–1924),
      gr-republic-2 (1924–1935), gr-kingdom-2 (1935–1973), gr-junta (1967–1974),
      gr-republic-3 (1974–), britain, italy, bulgaria, germany, turkey, albania, cyprus-republic,
      crete-autonomous, samos-principality, ionian-state (United States of the Ionian Islands, 1815–1864)
- [ ] Write `content/instruments.yaml`: london-protocol-1830, constantinople-convention-1832,
      london-treaty-1864, berlin-congress-1878, constantinople-convention-1881, london-treaty-1913,
      bucharest-treaty-1913, neuilly-1919, sevres-1920, lausanne-1923, paris-1947
- [ ] Write `content/control.yaml`. One entry per (atom, polity, kind, period).
      Expect roughly 90 to 120 rows. This is the most historically demanding file in the repo;
      cite an instrument on every sovereignty transfer.

Example shape:

```yaml
- atom: thrace-east
  polity: ottoman
  kind: sovereign
  period: ["1821-01-01", "1920-08-10"]
- atom: thrace-east
  polity: gr-kingdom
  kind: sovereign
  period: ["1920-08-10", "1923-07-24"]
  instrument: sevres-1920
  note: "Administration from 1920; reversed at Lausanne."
- atom: thrace-east
  polity: turkey
  kind: sovereign
  period: ["1923-07-24", null]     # null = open-ended, becomes 'infinity'
  instrument: lausanne-1923
```

- [ ] Implement `after1821.ingest.control` with a Pydantic model that parses `period` into a
      `daterange`, defaults the upper bound to `infinity`, and validates the referenced ids exist
- [ ] Implement `after1821.geo.snapshot(on: date, kind: control_kind) -> geometry` using
      `ST_Union` over the atoms under that control on that date

**Acceptance — this is the phase that proves the model works.** Write `tests/test_borders.py`
asserting the total sovereign Greek area on each date, tolerance 2%:

| date | expected km² |
|---|---|
| 1833-01-01 | 47,516 |
| 1865-01-01 | 50,176 |
| 1882-01-01 | 63,571 |
| 1914-01-01 | 120,308 |
| 1921-06-01 | > 150,000 (includes Eastern Thrace and the Smyrna zone) |
| 1924-01-01 | 128,900 |
| 1950-01-01 | 131,957 |

Also assert that on 1942-06-01 Greece is still `sovereign` over its atoms while Germany,
Italy and Bulgaria hold `occupied` rows over them, and that both queries return sensibly.

If these pass, the hard part of the project is done.

---

# PHASE 4 — Content model and the event corpus

- [ ] Pydantic ingest models in `apps/api/src/after1821/schemas/ingest.py` for every content type.
      Strict mode, no extra keys, custom validators for `period` and `precision` coherence
      (a `precision: day` event must have a one-day range).
- [ ] `content/events/<id>.yaml` schema:

```yaml
id: exodus-messolonghi
title:
  el: Η Έξοδος του Μεσολογγίου
  en: The Exodus of Messolonghi
summary:
  el: |
    ...
  en: |
    ...
period: ["1826-04-22", "1826-04-23"]     # proleptic Gregorian, always
precision: day
as_written:
  date: "1826-04-10"
  calendar: julian
  display:
    el: "10 Απριλίου 1826 (π.η.)"
    en: "10 April 1826 (o.s.)"
place: messolonghi
polity: gr-provisional
significance: 5
themes: [war]
sources:
  - id: st-clair-1972
    locator: "pp. 241-254"
claims:
  - measure: deaths
    low: 3000
    high: 6000
    source: st-clair-1972
    note:
      en: "Estimates vary widely; no reliable count of the garrison or the civilians."
links:
  - kind: culminates_in
    dst: fall-of-messolonghi
interpretations: []
```

- [ ] Write `content/sources.yaml` with at least: Clogg *A Concise History of Greece*,
      Gallant *Modern Greece*, Mazower *Salonica, City of Ghosts*, Kalyvas on the Civil War,
      Hirschon on the population exchange, ELSTAT census series, the Eurostat boundary dataset.
- [ ] Convert the 52 prototype events to YAML. The prototype HTML is the input; every number
      currently embedded in prose becomes a `claim` row with a source, or gets cut.
- [ ] `content/places/*.yaml` with `place_name` entries carrying periods, so Smyrna/İzmir and
      Constantinople/Istanbul resolve by date rather than by hardcoding.
- [ ] `make ingest` is idempotent: truncate and reload, wrapped in one transaction.

**Acceptance:**
- `make reset` from an empty database produces a fully populated one with zero warnings.
- Every event of `significance >= 4` has at least two distinct `event_source` rows.
- Every `claim` has a `source_id` (enforced by the schema, assert it in a test anyway).
- A test resolves the name of `place: smyrna` on 1922-09-01 to "Smyrna"/"Σμύρνη" and on
  2020-01-01 to "İzmir".

---

# PHASE 5 — API and the static export

- [ ] FastAPI app, `apps/api/src/after1821/api/`. Response models are Pydantic, separate from
      the ingest models. No ORM objects cross the boundary.
- [ ] `GET /api/atlas?on=1921-06-01&kinds=sovereign,occupied&simplify=2` → GeoJSON FeatureCollection
- [ ] `GET /api/events?from=&to=&themes=&min_significance=&lang=` → list, paginated
- [ ] `GET /api/events/{id}` → event with place, claims, sources, interpretations, links resolved
- [ ] `GET /api/epochs` → the sorted list of dates on which any control row starts or ends
- [ ] `after1821.export.dump`: a Typer command that writes the static payload for the frontend:
  - [ ] `atoms.topo.json` — one quantised TopoJSON of all atoms, via `topojson` (Python `topojson` package) or shell out to `geo2topo`/`toposimplify`. Quantise to 1e5, simplify lightly.
  - [ ] `control.json` — flat array `{atom, polity, kind, from, to}` with dates as ISO strings
  - [ ] `events.<lang>.json` — the timeline payload, one per language, only the fields the list needs
  - [ ] `events/<id>.<lang>.json` — full detail per event per language
  - [ ] `meta.json` — epochs, themes, polities, area and population series
- [ ] Output goes to `apps/web/static/data/`, gitignored, regenerated by `make export`

**Acceptance:**
- `make export` produces `atoms.topo.json` under 150 KB.
- A test loads the exported TopoJSON, merges the atoms Greece held on 1914-01-01 and asserts the
  resulting area matches the Postgres answer within 2%. This proves the client-side merge path
  agrees with the server-side one.

---

# PHASE 6 — CI

- [ ] GitHub Actions: spin up postgis service, `make migrate`, `make ingest`, `make test`, `make lint`
- [ ] Content validation job that fails the build on:
  - [ ] a `claim` without a source
  - [ ] an event at significance 4 or 5 with fewer than two sources
  - [ ] a control row without an instrument on a sovereignty change after 1830
  - [ ] any `title` or `summary` missing `el` or `en`
  - [ ] an `event_link` pointing at a nonexistent event
- [ ] Make this job the required check on `main`. Contested history needs review, and the
      review needs teeth.

---

# PHASE 7 — Frontend scaffold

- [ ] `pnpm create svelte@latest apps/web` — SvelteKit 2, TypeScript, no ESLint prompt spam
- [ ] `adapter-static`, `prerender = true` in the root layout
- [ ] Routing `src/routes/[[lang=lang]]/` with a param matcher accepting `el` and `en`.
      `/` redirects to `/en` or `/el` by `Accept-Language`. Both prerendered.
- [ ] `src/lib/tokens.css` — port the palette from the prototype:
      era ramp as six ordinal steps, madder accent, teal-biased neutrals, full light and dark
      token sets on `:root`, `@media (prefers-color-scheme: dark)` guarded by
      `:root:not([data-theme="light"])`, and `:root[data-theme="dark"]`
- [ ] Fonts: EB Garamond (display and body, has Greek), IBM Plex Sans (UI, has Greek),
      IBM Plex Mono (figures). Self-host via `@fontsource` rather than Google Fonts, and subset
      to latin + greek.
- [ ] Paraglide (inlang) for UI chrome only. Event text comes from the exported JSON.

**Acceptance:** `pnpm build` emits a static site; `/el` and `/en` both exist as HTML files
containing real text.

---

# PHASE 8 — The map component

- [ ] `src/lib/map/projection.ts` — `d3-geo`, `geoConicConformal` centred on Greece, fitted to
      a fixed bounding box covering lon 18.4 to 30.4 and lat 34.2 to 42.4, with an option to
      extend east for Cyprus and Asia Minor
- [ ] `src/lib/map/Atlas.svelte`:
  - props: `date`, `kinds`, `highlight`
  - loads `atoms.topo.json` once
  - `$derived` computes the held atom set for `date`, then `topojson.merge` per polity
  - renders `<path>` per polity per kind, plus a hairline for atom boundaries inside Greece
  - neighbours drawn flat and unlabelled, with a note that they are at present-day extent
  - **renders server-side during prerender** for the default date, so first paint has a map
- [ ] Occupation rendered as a hatch overlay on top of sovereignty, not as a replacement colour.
      This is the visual payoff of the two-layer control model; do not collapse it.
- [ ] Cyprus inset, bottom right, greyed, with its own projection
- [ ] Pins from event places, with the active one enlarged and labelled
- [ ] `prefers-reduced-motion` respected on all transitions

**Acceptance:** a Playwright test screenshots the atlas at 1832, 1913, 1921, 1942 and 1950
and the 1921 shot shows Eastern Thrace and the Smyrna zone, the 1942 shot shows the occupation
hatch. These are the states the prototype could not represent; they are the proof the rewrite
was worth it.

---

# PHASE 9 — Timeline, events, and routing

- [ ] `src/lib/Scrubber.svelte` — year range input, regime strip built from `polity` periods,
      event ticks, play control
- [ ] `src/lib/Ledger.svelte` — the scrolling event list, scroll-linked to the map date
- [ ] `/[lang]/` — the atlas plus ledger, the main view
- [ ] `/[lang]/[year]/[slug]` — one prerendered page per event per language, with the map frozen
      at that event's date, the full summary, claims rendered as ranges with citations,
      interpretations shown side by side where they exist, and links to related events
- [ ] `/[lang]/atlas/[date]` — a deep-linkable map state
- [ ] `/[lang]/sources` — the bibliography, generated from `sources.yaml`
- [ ] `/[lang]/about` — scope, method, and the caveats list (simplifications, contested figures,
      the calendar note)
- [ ] `sitemap.xml` and `robots.txt` generated at build
- [ ] Per-page `<title>`, meta description, canonical, and `hreflang` alternates between el and en
- [ ] Open Graph images: generate one per event at build time via `satori` or a Playwright pass,
      showing the map at that date with the title. This is what makes a link shared on social
      media look like a real publication.

**Acceptance:**
- Every event has a unique prerendered URL in both languages with `hreflang` pointing at its pair.
- Lighthouse on a mid-tier mobile profile: performance 95+, accessibility 100.
- The site works with JavaScript disabled for reading: text and the default map are in the HTML.

---

# PHASE 10 — Deploy

- [ ] Cloudflare Pages for `apps/web`, build command `pnpm build`, output `build/`
- [ ] The content build runs in CI: migrate, ingest, export, then build the site. Postgres exists
      only inside the CI job for v1. Do not provision a production database yet.
- [ ] Deploy the FastAPI app only when something actually needs it at runtime. Until then it is a
      local authoring tool and that is fine.
- [ ] Domain, and a CC-BY-SA notice in the footer linking to the sources page

---

# Definition of done for v1

A visitor can open the site in Greek or English, scrub from 1821 to today, watch the territory
assemble and see Eastern Thrace and the Smyrna zone appear and vanish, click any of the 52 events,
land on a page with its own URL that Google has indexed, see where the figures come from, and
follow a causal link to the next event. The whole thing is static files on a CDN, and adding an
event is a pull request containing one YAML file.

---

# CLAUDE.md (write this at the repo root)

Contents to include:

- One-paragraph description of the project and the four ground rules above
- The invariant: content is in `content/`, Postgres is derived, never hand-edit the database
- The commands: `make db-up`, `make migrate`, `make ingest`, `make export`, `make test`, `make reset`
- The "do not build" list from the top of this file
- Style: ruff format, line length 100, type hints everywhere, SQLAlchemy 2.0 declarative style,
  no `Any` in public signatures
- Svelte 5 runes only, no legacy stores, no `$:` reactive statements
- No em dashes in any prose written into the repo or the content files
- A note that historical claims must carry a citation and that contested figures are ranges,
  never a single number silently chosen