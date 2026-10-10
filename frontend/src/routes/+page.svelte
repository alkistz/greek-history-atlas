<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import Atlas, { type MapPin } from '$lib/Atlas.svelte';
	import EventLedger from '$lib/EventLedger.svelte';
	import FrameSwitch from '$lib/FrameSwitch.svelte';
	import Legend from '$lib/Legend.svelte';
	import MapCaption from '$lib/MapCaption.svelte';
	import RegionFilter from '$lib/RegionFilter.svelte';
	import { t } from '$lib/lang.svelte';
	import { ui } from '$lib/ui';
	import { frameRect, visibleIn, type Rect } from '$lib/projection';
	import { regimeOn } from '$lib/regimes';
	import type { TrendPoint } from '$lib/TerritoryTrend.svelte';
	import Timeline, { type TimelineBand, type TimelineEvent } from '$lib/Timeline.svelte';
	import { instrumentsOn, legendEntries, resolveOn } from '$lib/resolve';
	import { daysBetween, toDay, toISO, within, year } from '$lib/time';
	import type { AtlasEvent } from '$lib/types';
	import { parseView, writeView } from '$lib/viewstate';

	let { data } = $props();

	const DEFAULT_DATE = '1913-08-10';

	const origin = $derived(data.meta.range.from);
	const maxDay = $derived(daysBetween(origin, data.meta.range.to));
	const epochDays = $derived(data.meta.epochs.map((d) => toDay(d, origin)));
	const areaOf = $derived(new Map(data.atoms.features.map((f) => [f.properties.id, f.properties])));
	const instrumentName = $derived(new Map(data.meta.instruments.map((i) => [i.id, t(i.name)])));
	const placeOf = $derived(new Map(data.places.map((p) => [p.id, p])));

	// The query string is the entry point; from here the local state leads and is
	// mirrored back, so dragging the timeline stays cheap.
	const initial = untrack(() => parseView(page.url, DEFAULT_DATE));
	let day = $state(untrack(() => toDay(initial.on ?? DEFAULT_DATE, data.meta.range.from)));
	let showOccupation = $state(initial.occupation);
	let selectedId = $state<string | null>(initial.event);
	let frame = $state(initial.frame);
	let regions = $state<string[]>(initial.regions);

	const date = $derived(toISO(day, origin));
	$effect(() => {
		writeView({ on: date, frame, event: selectedId, occupation: showOccupation, regions });
	});

	const layered = $derived(resolveOn(data.control, date));
	// What the camera is showing, so the legend lists what is on screen and not
	// what the frame nominally contains.
	let view = $state<Rect | null>(null);
	const legend = $derived(
		legendEntries(
			layered,
			data.meta.polities,
			visibleIn(data.atoms.features, view ?? frameRect(frame))
		)
	);
	const instruments = $derived(
		instrumentsOn(data.control, date).map((id) => ({ id, name: instrumentName.get(id) ?? id }))
	);
	// Undefined only before the chain begins, in the weeks of 1821 before there was
	// a Greek state to have a form.
	const regime = $derived(regimeOn(data.meta.regimes, date) ?? null);
	const bands = $derived.by((): TimelineBand[] =>
		data.meta.regimes.map((r) => ({
			id: r.id,
			from: toDay(r.from, origin),
			to: r.to ? toDay(r.to, origin) : maxDay,
			label: `${t(r.name)} · ${year(r.from)}–${r.to ? year(r.to) : ''}`
		}))
	);

	// A region is a set of atoms, so the filter is a set membership test and nothing
	// is stored per event. Empty selection means the whole map.
	const regionOf = $derived(
		new Map(data.meta.regions.flatMap((r) => r.atoms.map((a) => [a, r.id] as const)))
	);
	const scope = $derived.by(() => {
		if (!regions.length) return null;
		const byId = new Map(data.meta.regions.map((r) => [r.id, r]));
		return new Set(regions.flatMap((id) => byId.get(id)?.atoms ?? []));
	});
	const inScope = (atom: string | null) => scope === null || (atom !== null && scope.has(atom));
	const dimmed = $derived.by(() => {
		const out = new Set<string>();
		if (scope === null) return out;
		for (const f of data.atoms.features) {
			if (!scope.has(f.properties.id)) out.add(f.properties.id);
		}
		return out;
	});
	const shownEvents = $derived(
		scope === null ? data.events : data.events.filter((e) => inScope(e.atom))
	);

	const selected = $derived(data.events.find((e) => e.id === selectedId) ?? null);
	// The highlight follows the selected event only while the date is inside it.
	const highlight = $derived(
		selected && within(date, selected.period[0], selected.period[1]) ? selected.atom : null
	);

	const marks = $derived.by((): TimelineEvent[] =>
		data.events.map((e) => ({
			id: e.id,
			day: toDay(e.period[0], origin),
			title: `${year(e.period[0])} — ${t(e.title)}`,
			significance: e.significance,
			muted: !inScope(e.atom)
		}))
	);

	// Events of the surrounding years, as dots where they happened: the map is a
	// place to browse from, not only a picture of a date. Only the selected one
	// is named; the rest speak on hover.
	const NEAR_DAYS = 365 * 6;
	const pins = $derived.by((): MapPin[] => {
		const out: MapPin[] = [];
		for (const e of data.events) {
			if (!e.place) continue;
			const d = toDay(e.period[0], origin);
			const isSelected = e.id === selectedId;
			if (!isSelected && Math.abs(d - day) > NEAR_DAYS) continue;
			const p = placeOf.get(e.place);
			if (!p) continue;
			out.push({
				id: e.id,
				lon: p.lon,
				lat: p.lat,
				label: `${year(e.period[0])} — ${t(e.title)}`,
				selected: isSelected,
				muted: !inScope(e.atom),
				labelled: isSelected
			});
		}
		// The selected one last, so it is drawn on top.
		return out.sort((a, b) => Number(a.selected ?? false) - Number(b.selected ?? false));
	});

	function greekAreaIn(sovereign: Map<string, string>): number {
		let km2 = 0;
		for (const [atom, polity] of sovereign) {
			const props = areaOf.get(atom);
			if (props && !props.external && polity.startsWith('gr-')) km2 += props.area_km2;
		}
		return km2;
	}
	const greekArea = $derived(greekAreaIn(layered.sovereign));

	// Sampled at the epochs only, because that is the complete set of dates on
	// which the figure can change.
	const trend = $derived.by((): TrendPoint[] =>
		data.meta.epochs.map((iso) => ({
			day: toDay(iso, origin),
			km2: greekAreaIn(resolveOn(data.control, iso).sovereign)
		}))
	);

	function select(e: AtlasEvent) {
		selectedId = e.id;
		day = toDay(e.period[0], origin);
		frame = e.frame;
	}
	function selectById(id: string) {
		const e = data.events.find((x) => x.id === id);
		if (e) select(e);
	}

	/** A click on the map filters by that territory's region. */
	function pick(atom: string) {
		const id = regionOf.get(atom);
		if (!id) return;
		toggleRegion(id);
	}
	/**
	 * Selecting a region carries the map to it, where the region says where it is.
	 *
	 * Cyprus and Asia Minor are outside the default frame entirely, so filtering by
	 * them used to narrow the ledger while leaving the reader looking at a map with
	 * nothing selected on it. `Region.frame` is a viewport hint for exactly this;
	 * it does not define the region, so it is only ever followed on the way in.
	 */
	function toggleRegion(id: string) {
		const off = regions.includes(id);
		regions = off ? regions.filter((r) => r !== id) : [...regions, id];
		if (off) return;
		const hint = data.meta.regions.find((r) => r.id === id)?.frame;
		if (hint) frame = hint;
	}

	// Two columns or one. On a desktop the legend on the map is open and the frame
	// chips sit on the map; on a phone the map is small, so the legend folds to its
	// heading and the chips move under the timeline.
	const mq = matchMedia('(min-width: 900px)');
	let wide = $state(mq.matches);
	$effect(() => {
		const on = () => (wide = mq.matches);
		mq.addEventListener('change', on);
		return () => mq.removeEventListener('change', on);
	});
	let legendOpen = $state(mq.matches);
</script>

<svelte:head>
	<title>{ui('site.name')}</title>
</svelte:head>

<main class="atlas">
	<section class="stage">
		<div class="mapframe">
			<Atlas
				atoms={data.atoms.features}
				land={data.land}
				meta={data.meta}
				control={data.control}
				{date}
				{frame}
				{showOccupation}
				{highlight}
				{dimmed}
				{pins}
				onpick={pick}
				onpin={selectById}
				onview={(r) => (view = r)}
				fill
			/>

			{#if wide}
				<div class="frames">
					<FrameSwitch bind:frame />
				</div>
			{/if}

			<details class="legend" bind:open={legendOpen}>
				<summary>{ui('atlas.legend')}</summary>
				<div class="legend-body">
					<Legend entries={legend} />
					{#if layered.insurgent.size}
						<p class="note">{ui('atlas.note.insurgent')}</p>
					{/if}
					{#if layered.occupied.size}
						<p class="note">{ui('atlas.note.occupied')}</p>
					{/if}
					<label class="occ">
						<input type="checkbox" bind:checked={showOccupation} />
						{ui('atlas.occupation')}
					</label>
					<details class="about">
						<summary>{ui('atlas.about')}</summary>
						<p class="note">{ui('site.footer')}</p>
					</details>
				</div>
			</details>
		</div>

		<div class="deck">
			<MapCaption {date} areaKm2={greekArea} {instruments} {trend} {day} {maxDay} {regime} compact />
			<div class="scrub">
				<Timeline
					bind:day
					{maxDay}
					{epochDays}
					{origin}
					events={marks}
					{bands}
					{selectedId}
					onselectevent={selectById}
				/>
			</div>
			{#if !wide}
				<div class="frames-row">
					<FrameSwitch bind:frame />
				</div>
			{/if}
		</div>
	</section>

	<aside>
		<div class="aside-head">
			<h2>{ui('page.events')}</h2>
			<RegionFilter
				regions={data.meta.regions}
				selected={regions}
				ontoggle={toggleRegion}
				onclear={() => (regions = [])}
			/>
		</div>
		<EventLedger
			events={shownEvents}
			total={data.events.length}
			{date}
			{selectedId}
			onselect={select}
			fill
		/>
	</aside>
</main>

<style>
	main {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(300px, 400px);
		gap: 24px;
		align-items: stretch;
		flex: 1;
		min-height: 0;
	}
	.stage {
		display: flex;
		flex-direction: column;
		min-height: 0;
	}
	.mapframe {
		position: relative;
		flex: 1;
		min-height: 320px;
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg, 8px);
		overflow: hidden;
	}
	.frames {
		position: absolute;
		top: 8px;
		left: 8px;
		padding: 4px 6px;
		background: color-mix(in srgb, var(--panel) 85%, transparent);
		backdrop-filter: blur(6px);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg, 8px);
		font-size: 0.85rem;
	}
	/* Bottom right: in the default frame that corner is open sea, where the
	   bottom left is the Ionian and the Peloponnese. */
	.legend {
		position: absolute;
		right: 8px;
		bottom: 8px;
		max-width: min(300px, calc(100% - 16px));
		background: color-mix(in srgb, var(--panel) 88%, transparent);
		backdrop-filter: blur(6px);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg, 8px);
		font-size: 0.85rem;
	}
	.legend summary {
		cursor: pointer;
		padding: 5px 10px;
		color: var(--ink-soft);
		font-size: 0.74rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
		list-style: none;
	}
	.legend summary::-webkit-details-marker {
		display: none;
	}
	.legend summary::before {
		content: '▸';
		display: inline-block;
		margin-right: 6px;
		transition: transform 150ms ease;
	}
	.legend[open] summary::before {
		transform: rotate(90deg);
	}
	.legend-body {
		padding: 0 10px 8px;
		max-height: 40vh;
		overflow: auto;
	}
	.occ {
		display: inline-flex;
		gap: 6px;
		align-items: center;
		cursor: pointer;
		margin-top: 8px;
		font-size: 0.84rem;
		color: var(--ink-soft);
	}
	.note {
		margin: 8px 0 0;
		color: var(--ink-soft);
		font-size: 0.8rem;
		max-width: 60ch;
	}
	.about {
		margin-top: 8px;
		font-size: 0.74rem;
		color: var(--ink-soft);
	}
	.about summary {
		cursor: pointer;
	}
	.about .note {
		margin-top: 4px;
		font-size: 0.72rem;
	}
	.legend-body :global(.legend) {
		grid-template-columns: 1fr;
	}
	.deck {
		flex: none;
		padding-top: 2px;
	}
	.scrub {
		margin-top: 6px;
	}

	aside {
		display: flex;
		flex-direction: column;
		min-height: 0;
	}
	.aside-head {
		flex: none;
	}
	aside h2 {
		font-size: 1.15rem;
		margin: 0 0 8px;
	}

	@media (max-width: 900px) {
		main {
			display: block;
		}
		/* The map and its date control stay put while the list scrolls under them:
		   picking an event must never scroll the map out of sight. */
		.stage {
			position: sticky;
			top: 0;
			z-index: 3;
			background: var(--ground);
			padding-bottom: 8px;
		}
		.mapframe {
			height: 36vh;
			min-height: 220px;
			flex: none;
		}
		.frames-row {
			margin-top: 6px;
			font-size: 0.8rem;
		}
		/* No room for the sparkline here; the figure itself stays. */
		.deck :global(.trend) {
			display: none;
		}
		.legend {
			max-width: calc(100% - 16px);
		}
		.legend-body {
			max-height: 30vh;
		}
		aside {
			display: block;
			margin-top: 12px;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.legend summary::before {
			transition: none;
		}
	}
</style>
