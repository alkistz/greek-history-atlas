<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import FilterBar from '$lib/FilterBar.svelte';
	import { year } from '$lib/time';
	import { list, matches, params, replaceParams } from '$lib/urlstate';

	let { data } = $props();

	let query = $state(untrack(() => page.url.searchParams.get('q') ?? ''));
	let kinds = $state<string[]>(untrack(() => list(page.url, 'kinds')));

	$effect(() => replaceParams(params({ q: query, kinds })));

	const regionOf = $derived(
		new Map(data.meta.regions.flatMap((r) => r.atoms.map((a) => [a, r.name.en] as const)))
	);
	const atomName = $derived(new Map(data.meta.atoms.map((a) => [a.id, a.name.en])));

	// Links are authored on the event and on the figure; these are the inverses.
	const eventsAt = $derived.by(() => {
		const out = new Map<string, { id: string; title: string; when: string }[]>();
		for (const e of data.events) {
			if (!e.place) continue;
			const list = out.get(e.place) ?? [];
			list.push({ id: e.id, title: e.title.en, when: year(e.period[0]) });
			out.set(e.place, list);
		}
		return out;
	});
	const livesAt = $derived.by(() => {
		const out = new Map<string, { id: string; name: string; what: string; when: string }[]>();
		const add = (place: string | null, row: { id: string; name: string; what: string; when: string }) => {
			if (!place) return;
			const list = out.get(place) ?? [];
			list.push(row);
			out.set(place, list);
		};
		for (const f of data.figures) {
			if (f.born) {
				add(f.born.place, { id: f.id, name: f.name.en, what: 'born', when: year(f.born.date) });
			}
			if (f.died) {
				add(f.died.place, { id: f.id, name: f.name.en, what: 'died', when: year(f.died.date) });
			}
		}
		return out;
	});

	/** The name in force today, which is the one to lead with. */
	const current = (p: (typeof data.places)[number]) =>
		p.names.find((n) => n.to === null) ?? p.names[p.names.length - 1];

	const kindItems = $derived(
		[...new Set(data.places.map((p) => p.kind))]
			.sort()
			.map((k) => ({ id: k, label: k[0].toUpperCase() + k.slice(1) }))
	);

	const active = $derived(query.trim().length > 0 || kinds.length > 0);
	const sorted = $derived(
		[...data.places].sort((a, b) => current(a).name.en.localeCompare(current(b).name.en))
	);
	const shown = $derived(
		sorted.filter((p) => {
			if (kinds.length && !kinds.includes(p.kind)) return false;
			return matches(
				query,
				p.kind,
				p.atom ? atomName.get(p.atom) : null,
				p.atom ? regionOf.get(p.atom) : null,
				// Every name the place has ever carried, in both languages: Smyrna
				// should find İzmir and Σμύρνη should find both.
				...p.names.flatMap((n) => [n.name.en, n.name.el])
			);
		})
	);

	const toggle = (c: string[], id: string) =>
		c.includes(id) ? c.filter((x) => x !== id) : [...c, id];

	// A third of the corpus happens in Athens, so one place can be forty rows long
	// and bury the twenty places under it. Past this, the list folds.
	const FOLD_AT = 8;
</script>

<svelte:head>
	<title>Places — Greek History Atlas</title>
	<meta name="description" content="Every place the atlas names, and what happened there." />
</svelte:head>

<h1>Places</h1>
<p class="lead">
	Every point the atlas names. Names change and the point does not, so a place carries all
	the names it has held and the dates each was in force — searching any of them finds it.
</p>

<FilterBar
	bind:query
	placeholder="Search places, old names, regions…"
	shown={shown.length}
	total={data.places.length}
	noun="places"
	{active}
	onclear={() => {
		query = '';
		kinds = [];
	}}
>
	{#snippet facets()}
		<ChipGroup
			label="Kind"
			items={kindItems}
			selected={kinds}
			ontoggle={(id) => (kinds = toggle(kinds, id))}
			onclear={() => (kinds = [])}
		/>
	{/snippet}
</FilterBar>

<ol class="places">
	{#each shown as p (p.id)}
		{@const now = current(p)}
		{@const past = p.names.filter((n) => n !== now)}
		{@const here = eventsAt.get(p.id) ?? []}
		{@const lives = livesAt.get(p.id) ?? []}
		<li id={p.id}>
			<div class="head">
				<span class="name">{now.name.en}</span>
				{#if now.name.el}<span class="el">{now.name.el}</span>{/if}
				<span class="kind">{p.kind}</span>
			</div>
			<p class="where">
				{#if p.atom}
					<span>{atomName.get(p.atom) ?? p.atom}</span>
					{#if regionOf.get(p.atom) && regionOf.get(p.atom) !== atomName.get(p.atom)}
						<span class="region">{regionOf.get(p.atom)}</span>
					{/if}
				{:else}
					<span class="region">outside the mapped territory</span>
				{/if}
				<span class="coords">{p.lat.toFixed(2)}°N {p.lon.toFixed(2)}°E</span>
			</p>

			{#if past.length}
				<p class="formerly">
					Also known as
					{#each past as n, i (n.name.en)}{i ? '; ' : ' '}<span class="oldname"
							>{n.name.en}</span
						>{#if n.name.el}<span class="el"> {n.name.el}</span>{/if}{#if n.from || n.to}<span
							class="span"
						>
							{n.from ? year(n.from) : '…'}–{n.to ? year(n.to) : '…'}</span
						>{/if}{/each}
				</p>
			{/if}

			{#if here.length > FOLD_AT}
				<details class="fold">
					<summary>{here.length} events here</summary>
					<ul class="at">
						{#each here as e (e.id)}
							<li><span class="mono">{e.when}</span> <a href="/events/{e.id}">{e.title}</a></li>
						{/each}
					</ul>
				</details>
			{:else if here.length}
				<ul class="at">
					{#each here as e (e.id)}
						<li><span class="mono">{e.when}</span> <a href="/events/{e.id}">{e.title}</a></li>
					{/each}
				</ul>
			{/if}
			{#if lives.length}
				<ul class="at lives">
					{#each lives as l (l.id + l.what)}
						<li>
							<span class="mono">{l.when}</span>
							<a href="/figures/{l.id}">{l.name}</a>
							<span class="what">{l.what} here</span>
						</li>
					{/each}
				</ul>
			{/if}
			{#if !here.length && !lives.length}
				<p class="none">Named by the corpus, but nothing is anchored here yet.</p>
			{/if}
		</li>
	{:else}
		<li class="empty">No place matches that.</li>
	{/each}
</ol>

<style>
	h1 {
		font-size: 1.9rem;
		margin: 0 0 4px;
	}
	.lead {
		color: var(--ink-soft);
		margin: 0 0 18px;
		max-width: 66ch;
	}
	.places {
		list-style: none;
		padding: 0;
		margin: 0;
		max-width: 76ch;
		border-top: 1px solid var(--rule);
	}
	.places > li {
		padding: 12px 0;
		border-bottom: 1px solid var(--rule);
	}
	.head {
		display: flex;
		align-items: baseline;
		gap: 8px;
		flex-wrap: wrap;
	}
	.name {
		font-family: var(--serif);
		font-size: 1.1rem;
		font-weight: 600;
	}
	.el {
		color: var(--ink-soft);
		font-size: 0.9rem;
	}
	.kind {
		color: var(--ink-soft);
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	.where {
		margin: 2px 0 0;
		display: flex;
		gap: 12px;
		flex-wrap: wrap;
		font-size: 0.82rem;
		color: var(--ink-soft);
	}
	.region {
		text-transform: uppercase;
		letter-spacing: 0.06em;
		font-size: 0.74rem;
	}
	.coords {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.76rem;
		opacity: 0.8;
	}
	.formerly {
		margin: 5px 0 0;
		font-size: 0.85rem;
		color: var(--ink-soft);
	}
	.oldname {
		font-style: italic;
	}
	.span {
		font-family: var(--mono);
		font-size: 0.74rem;
	}
	.fold summary {
		cursor: pointer;
		margin-top: 6px;
		color: var(--ink-soft);
		font-size: 0.82rem;
	}
	.fold summary:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
		border-radius: var(--radius);
	}
	.at {
		list-style: none;
		padding: 0;
		margin: 6px 0 0;
		font-size: 0.88rem;
	}
	.at li {
		margin: 2px 0;
	}
	.at li > * + * {
		margin-left: 8px;
	}
	.mono {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.8rem;
		color: var(--ink-soft);
	}
	.what {
		color: var(--ink-soft);
		font-size: 0.8rem;
	}
	.none {
		margin: 5px 0 0;
		font-size: 0.85rem;
		color: var(--ink-soft);
		font-style: italic;
	}
	.empty {
		display: block;
		color: var(--ink-soft);
		padding: 14px 0;
	}
</style>
