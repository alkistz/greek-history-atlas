<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import Atlas from '$lib/Atlas.svelte';
	import EventLedger from '$lib/EventLedger.svelte';
	import FrameSwitch from '$lib/FrameSwitch.svelte';
	import Legend from '$lib/Legend.svelte';
	import MapCaption from '$lib/MapCaption.svelte';
	import RegionFilter from '$lib/RegionFilter.svelte';
	import { t } from '$lib/lang.svelte';
	import { ui } from '$lib/ui';
	import { visibleIn } from '$lib/projection';
	import { regimeOn } from '$lib/regimes';
	import type { TrendPoint } from '$lib/TerritoryTrend.svelte';
	import Timeline, { type TimelineEvent } from '$lib/Timeline.svelte';
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
	const legend = $derived(
		legendEntries(layered, data.meta.polities, visibleIn(data.atoms.features, frame))
	);
	const instruments = $derived(
		instrumentsOn(data.control, date).map((id) => ({ id, name: instrumentName.get(id) ?? id }))
	);
	// Undefined only before the chain begins, in the weeks of 1821 before there was
	// a Greek state to have a form.
	const regime = $derived(regimeOn(data.meta.regimes, date) ?? null);

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
</script>

<p class="tagline">{ui('atlas.tagline')}</p>

<main>
	<section class="mapcol">
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
				onpick={pick}
			/>
		</div>

		<MapCaption {date} areaKm2={greekArea} {instruments} {trend} {day} {maxDay} {regime} />

		<div class="scrub">
			<Timeline
				bind:day
				{maxDay}
				{epochDays}
				{origin}
				events={marks}
				{selectedId}
				onselectevent={selectById}
			/>
		</div>

		<div class="controls">
			<FrameSwitch bind:frame />
			<label class="occ">
				<input type="checkbox" bind:checked={showOccupation} />
				{ui('atlas.occupation')}
			</label>
		</div>

		<div class="legend">
			<Legend entries={legend} />
		</div>

		{#if layered.insurgent.size}
			<p class="note">{ui('atlas.note.insurgent')}</p>
		{/if}
		{#if layered.occupied.size}
			<p class="note">{ui('atlas.note.occupied')}</p>
		{/if}
	</section>

	<aside>
		<h2>{ui('page.events')}</h2>
		<RegionFilter
			regions={data.meta.regions}
			selected={regions}
			ontoggle={toggleRegion}
			onclear={() => (regions = [])}
		/>
		<EventLedger
			events={shownEvents}
			total={data.events.length}
			{date}
			{selectedId}
			onselect={select}
		/>
	</aside>
</main>

<style>
	.tagline {
		margin: 0 0 20px;
		color: var(--ink-soft);
		max-width: 60ch;
	}
	main {
		display: grid;
		grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
		gap: 28px;
		align-items: start;
	}
	.mapframe {
		/* Never wider than the 760-unit reference drawing (the source geometry is
		   1:3M, so upscaling buys nothing), and on a short window narrower still,
		   by the frame's own aspect ratio, so the timeline stays on screen with
		   the map it drives. */
		max-width: min(760px, calc((100vh - 350px) * 1.118));
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 8px;
	}
	.scrub {
		margin-top: 10px;
	}
	.controls {
		margin-top: 10px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 16px;
		flex-wrap: wrap;
		color: var(--ink-soft);
		font-size: 0.88rem;
	}
	.occ {
		display: inline-flex;
		gap: 6px;
		align-items: center;
		cursor: pointer;
	}
	.legend {
		margin-top: 16px;
	}
	.note {
		margin: 10px 0 0;
		color: var(--ink-soft);
		font-size: 0.84rem;
		max-width: 68ch;
	}
	aside h2 {
		font-size: 1.15rem;
		margin: 0 0 8px;
	}
	@media (max-width: 900px) {
		main {
			grid-template-columns: 1fr;
		}
	}
</style>
