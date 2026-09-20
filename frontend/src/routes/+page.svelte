<script lang="ts">
	import { untrack } from 'svelte';
	import Atlas from '$lib/Atlas.svelte';
	import EventLedger from '$lib/EventLedger.svelte';
	import Legend from '$lib/Legend.svelte';
	import MapCaption from '$lib/MapCaption.svelte';
	import { visibleIn, type FrameId } from '$lib/projection';
	import Scrubber from '$lib/Scrubber.svelte';
	import { instrumentsOn, legendEntries, resolveOn } from '$lib/resolve';
	import { daysBetween, toDay, toISO, within, year } from '$lib/time';
	import type { AtlasEvent } from '$lib/types';

	let { data } = $props();

	const origin = $derived(data.meta.range.from);
	const maxDay = $derived(daysBetween(origin, data.meta.range.to));
	const epochDays = $derived(data.meta.epochs.map((d) => toDay(d, origin)));
	const areaOf = $derived(new Map(data.atoms.features.map((f) => [f.properties.id, f.properties])));
	const instrumentName = $derived(new Map(data.meta.instruments.map((i) => [i.id, i.name.en])));

	let day = $state(untrack(() => toDay('1913-08-10', origin)));
	let showOccupation = $state(true);
	let selectedId = $state<string | null>(null);
	let frame = $state<FrameId>('greece');

	const date = $derived(toISO(day, origin));
	const layered = $derived(resolveOn(data.control, date));
	const legend = $derived(
		legendEntries(layered, data.meta.polities, visibleIn(data.atoms.features, frame))
	);
	const instruments = $derived(
		instrumentsOn(data.control, date).map((id) => ({ id, name: instrumentName.get(id) ?? id }))
	);

	const selected = $derived(data.events.find((e) => e.id === selectedId) ?? null);
	// The highlight follows the selected event only while the date is inside it.
	const highlight = $derived(
		selected && within(date, selected.period[0], selected.period[1]) ? selected.atom : null
	);

	const greekArea = $derived.by(() => {
		let km2 = 0;
		for (const [atom, polity] of layered.sovereign) {
			const props = areaOf.get(atom);
			if (props && !props.external && polity.startsWith('gr-')) km2 += props.area_km2;
		}
		return km2;
	});

	function select(e: AtlasEvent) {
		selectedId = e.id;
		day = toDay(e.period[0], origin);
		frame = e.frame;
	}
</script>

<p class="tagline">An atlas of Greek history. The map redraws as control of territory changes.</p>

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
			/>
		</div>

		<MapCaption {date} areaKm2={greekArea} {instruments} {frame} onreset={() => (frame = 'greece')} />

		<div class="scrub">
			<Scrubber bind:day {maxDay} {epochDays} year={year(date)} />
		</div>

		<div class="controls">
			<label>
				<input type="checkbox" bind:checked={showOccupation} />
				Show occupation
			</label>
		</div>

		<div class="legend">
			<Legend entries={legend} />
		</div>

		{#if layered.insurgent.size}
			<p class="note">Stippled areas are in armed revolt. There was no recognised frontier.</p>
		{/if}
		{#if layered.occupied.size}
			<p class="note">
				Hatching marks occupation layered over sovereignty, not replacing it. The Greek state
				remained sovereign throughout.
			</p>
		{/if}
	</section>

	<aside>
		<h2>Events</h2>
		<EventLedger events={data.events} {date} {selectedId} onselect={select} />
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
		grid-template-columns: minmax(0, 1.9fr) minmax(0, 1fr);
		gap: 28px;
		align-items: start;
	}
	.mapframe {
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 8px;
	}
	.scrub {
		margin-top: 14px;
	}
	.controls {
		margin-top: 8px;
		color: var(--ink-soft);
		font-size: 0.88rem;
	}
	.controls label {
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
