<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import FilterBar from '$lib/FilterBar.svelte';
	import { regimeLabel, regimeOn } from '$lib/regimes';
	import { prettyPeriod, year } from '$lib/time';
	import { list, matches, params, replaceParams } from '$lib/urlstate';
	import { atlasHref } from '$lib/viewstate';

	let { data } = $props();

	let query = $state(untrack(() => page.url.searchParams.get('q') ?? ''));
	let regions = $state<string[]>(untrack(() => list(page.url, 'regions')));
	let regimes = $state<string[]>(untrack(() => list(page.url, 'regimes')));

	$effect(() => replaceParams(params({ q: query, regions, regimes })));

	const regionOf = $derived(
		new Map(data.meta.regions.flatMap((r) => r.atoms.map((a) => [a, r.id] as const)))
	);
	const regionName = $derived(new Map(data.meta.regions.map((r) => [r.id, r.name.en])));
	const regionItems = $derived(data.meta.regions.map((r) => ({ id: r.id, label: r.name.en })));

	// Nothing is stored per event: an event's regime is a lookup from its start date,
	// the way its region is a lookup from its atom. The chips are already in order,
	// so the row doubles as a chronological spine for the century the map cannot show.
	const regimeItems = $derived(
		data.meta.regimes.map((r) => ({ id: r.id, label: regimeLabel(r) }))
	);

	const active = $derived(query.trim().length > 0 || regions.length > 0 || regimes.length > 0);
	const shown = $derived(
		data.events.filter((e) => {
			const region = e.atom ? regionOf.get(e.atom) : undefined;
			if (regions.length && (!region || !regions.includes(region))) return false;
			const regime = regimeOn(data.meta.regimes, e.period[0]);
			if (regimes.length && (!regime || !regimes.includes(regime.id))) return false;
			return matches(query, e.title.en, e.title.el, e.summary.en, e.period[0]);
		})
	);

	const decades = $derived.by(() => {
		const out: { decade: string; events: typeof shown }[] = [];
		for (const e of shown) {
			const decade = `${e.period[0].slice(0, 3)}0s`;
			const last = out.at(-1);
			if (last?.decade === decade) last.events.push(e);
			else out.push({ decade, events: [e] });
		}
		return out;
	});

	function toggleRegion(id: string) {
		regions = regions.includes(id) ? regions.filter((r) => r !== id) : [...regions, id];
	}
	function toggleRegime(id: string) {
		regimes = regimes.includes(id) ? regimes.filter((r) => r !== id) : [...regimes, id];
	}
	function clear() {
		query = '';
		regions = [];
		regimes = [];
	}
</script>

<svelte:head>
	<title>Events — Greek History Atlas</title>
	<meta name="description" content="Every event in the atlas, in order." />
</svelte:head>

<h1>Events</h1>
<p class="lead">In order. Each one opens the map on the day it happened.</p>

<FilterBar
	bind:query
	placeholder="Search events…"
	shown={shown.length}
	total={data.events.length}
	noun="events"
	{active}
	onclear={clear}
>
	{#snippet facets()}
		<ChipGroup
			label="Region"
			items={regionItems}
			selected={regions}
			ontoggle={toggleRegion}
		/>
		<ChipGroup
			label="Regime"
			items={regimeItems}
			selected={regimes}
			ontoggle={toggleRegime}
		/>
	{/snippet}
</FilterBar>

{#each decades as g (g.decade)}
	<section>
		<h2>{g.decade}</h2>
		<ol class="events">
			{#each g.events as e (e.id)}
				{@const regime = regimeOn(data.meta.regimes, e.period[0])}
				<li>
					<span class="when">{year(e.period[0])}</span>
					<div>
						<a class="title" href="/events/{e.id}">{e.title.en}</a>
						{#if e.atom && regionOf.get(e.atom)}
							<span class="region">{regionName.get(regionOf.get(e.atom)!)}</span>
						{/if}
						{#if regime}<span class="regime">{regime.name.en}</span>{/if}
						<p>{e.summary.en}</p>
						<p class="meta">
							<span>{prettyPeriod(e.period, e.precision)}</span>
							<a href={atlasHref({ on: e.period[0], frame: e.frame, event: e.id })}>
								Open on the atlas
							</a>
						</p>
					</div>
				</li>
			{/each}
		</ol>
	</section>
{:else}
	<p class="empty">No event matches that.</p>
{/each}

<style>
	h1 {
		font-size: 1.9rem;
		margin: 0 0 4px;
	}
	.lead {
		color: var(--ink-soft);
		margin: 0 0 18px;
		max-width: 60ch;
	}
	section {
		max-width: 76ch;
	}
	h2 {
		font-family: var(--mono);
		font-size: 0.78rem;
		letter-spacing: 0.1em;
		color: var(--ink-soft);
		margin: 26px 0 0;
		padding-bottom: 4px;
		border-bottom: 1px solid var(--rule);
	}
	.events {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	.events li {
		display: grid;
		grid-template-columns: 7ch 1fr;
		gap: 12px;
		padding: 12px 0;
		border-bottom: 1px solid var(--rule);
	}
	.when {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.85rem;
		color: var(--ink-soft);
		padding-top: 3px;
	}
	.title {
		font-family: var(--serif);
		font-size: 1.1rem;
		font-weight: 600;
		text-decoration: none;
		color: var(--ink);
	}
	.title:hover {
		color: var(--accent);
	}
	.region,
	.regime {
		margin-left: 8px;
		color: var(--ink-soft);
		font-size: 0.74rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	/* The regime is the softer of the two: it is context for the row, not its subject. */
	.regime {
		opacity: 0.72;
	}
	.events p {
		margin: 4px 0 0;
		color: var(--ink-soft);
		font-size: 0.92rem;
	}
	.meta {
		display: flex;
		gap: 14px;
		flex-wrap: wrap;
		font-size: 0.82rem;
	}
	.empty {
		color: var(--ink-soft);
		max-width: 60ch;
	}
</style>
