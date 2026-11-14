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
	import { greekArea, instrumentsOn, legendEntries, resolveOn } from '$lib/resolve';
	import { daysBetween, toDay, toISO, within, year } from '$lib/time';
	import type { AtlasEvent } from '$lib/types';
	import { parseView, writeView } from '$lib/viewstate';
	import { useChrome } from '$lib/chrome.svelte';

	let { data } = $props();

	// With no date in the URL the atlas opens where the corpus does, on its first
	// event, and the reader moves forward from there.
	const DEFAULT_DATE = untrack(() =>
		data.events.reduce((first, e) => (e.period[0] < first ? e.period[0] : first), data.meta.range.to)
	);

	const origin = $derived(data.meta.range.from);
	const maxDay = $derived(daysBetween(origin, data.meta.range.to));
	const epochDays = $derived(data.meta.epochs.map((d) => toDay(d, origin)));
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

	const greekKm2 = $derived(greekArea(layered.sovereign, data.atoms.features));

	// Sampled at the epochs only, because that is the complete set of dates on
	// which the figure can change.
	const trend = $derived.by((): TrendPoint[] =>
		data.meta.epochs.map((iso) => ({
			day: toDay(iso, origin),
			km2: greekArea(resolveOn(data.control, iso).sovereign, data.atoms.features)
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

	// The whole window or a tall page. On a desktop the map lies under everything
	// and the header, the events and the date float over it as panels, with the
	// legend open and the frame chips on the map; on a phone the map is small, so
	// the legend folds to its heading and the chips move under the timeline.
	const mq = matchMedia('(min-width: 1100px)');
	let wide = $state(mq.matches);
	$effect(() => {
		const on = () => (wide = mq.matches);
		mq.addEventListener('change', on);
		return () => mq.removeEventListener('change', on);
	});
	let legendOpen = $state(mq.matches);

	// What the panels cover, so the camera frames a region in the clear part of
	// the window and never behind the list. These mirror the wide rules below.
	const EDGE = 12;
	const SEP = 8;
	const SIDE = 400;
	const chrome = useChrome();
	let deckH = $state(0);
	let framesH = $state(0);
	const insets = $derived(
		wide
			? {
					top: EDGE + chrome.header + SEP + chrome.notice + SEP + framesH + SEP,
					right: EDGE + SIDE + SEP,
					bottom: EDGE + deckH + SEP,
					left: EDGE
				}
			: undefined
	);
</script>

<svelte:head>
	<title>{ui('page.title', { page: ui('page.atlas'), site: ui('site.name') })}</title>
</svelte:head>

<main class="atlas" style:--side="{SIDE}px" style:--deck-h="{deckH}px">
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
				{insets}
				fill
			/>

			{#if wide}
				<div class="frames" bind:offsetHeight={framesH}>
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

		<div class="deck" bind:offsetHeight={deckH}>
			<MapCaption {date} areaKm2={greekKm2} {instruments} {trend} {day} {maxDay} {regime} compact />
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
	/* Narrow first: a tall page, the map at the top and the list beneath. The
	   wide arrangement, with everything floating over a full-window map, is in
	   the media block at the end. */
	main {
		display: block;
	}
	.stage {
		display: flex;
		flex-direction: column;
		min-height: 0;
	}
	.mapframe {
		position: relative;
		overflow: hidden;
		background: var(--sea);
	}
	/* Panels on the map are cartouches: opaque, square, ruled in ink. */
	.frames {
		position: absolute;
		padding: 4px 6px;
		background: var(--panel);
		border: 1px solid var(--ink);
		font-size: 0.85rem;
	}
	/* Bottom right: in the default frame that corner is open sea, where the
	   bottom left is the Ionian and the Peloponnese. */
	.legend {
		position: absolute;
		right: 8px;
		bottom: 8px;
		max-width: min(300px, calc(100% - 16px));
		background: var(--panel);
		border: 1px solid var(--ink);
		font-size: 0.85rem;
	}
	.legend summary {
		cursor: pointer;
		padding: 5px 10px;
		color: var(--ink-soft);
		font-family: var(--serif);
		font-variant-caps: all-small-caps;
		font-size: 0.95rem;
		letter-spacing: 0.1em;
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
		font-size: 1.25rem;
		font-weight: 500;
		font-variant-caps: small-caps;
		letter-spacing: 0.04em;
		margin: 0 0 8px;
	}

	@media (min-width: 1100px) {
		main {
			position: relative;
			flex: 1;
			min-height: 0;
		}
		.stage {
			position: absolute;
			inset: 0;
		}
		.mapframe {
			position: absolute;
			inset: 0;
		}
		.frames {
			top: calc(12px + var(--header-h) + 8px + var(--notice-h) + 8px);
			left: 12px;
		}
		.legend {
			right: calc(var(--side) + 20px);
			bottom: calc(var(--deck-h) + 20px);
		}
		.deck {
			position: absolute;
			z-index: 4;
			left: 12px;
			right: calc(var(--side) + 20px);
			bottom: 12px;
			padding: 4px 16px 10px;
			background: var(--panel);
			border: 1px solid var(--ink);
		}
		aside {
			position: absolute;
			z-index: 4;
			top: calc(12px + var(--header-h) + 8px);
			right: 12px;
			bottom: 12px;
			width: var(--side);
			box-sizing: border-box;
			padding: 12px 14px 0;
			background: var(--panel);
			border: 1px solid var(--ink);
			--ledger-bg: var(--panel);
		}
	}
	@media (max-width: 1099px) {
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
