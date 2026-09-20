<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import FilterBar from '$lib/FilterBar.svelte';
	import { alt, both, byText, num, t } from '$lib/lang.svelte';
	import { term, Term, ui } from '$lib/ui';
	import { year } from '$lib/time';
	import { list, matches, params, replaceParams } from '$lib/urlstate';

	let { data } = $props();

	let query = $state(untrack(() => page.url.searchParams.get('q') ?? ''));
	let kinds = $state<string[]>(untrack(() => list(page.url, 'kinds')));

	$effect(() => replaceParams(params({ q: query, kinds })));

	const regionOf = $derived(
		new Map(data.meta.regions.flatMap((r) => r.atoms.map((a) => [a, t(r.name)] as const)))
	);
	const atomName = $derived(new Map(data.meta.atoms.map((a) => [a.id, t(a.name)])));

	// Links are authored on the event and on the figure; these are the inverses.
	const eventsAt = $derived.by(() => {
		const out = new Map<string, { id: string; title: string; when: string }[]>();
		for (const e of data.events) {
			if (!e.place) continue;
			const list = out.get(e.place) ?? [];
			list.push({ id: e.id, title: t(e.title), when: year(e.period[0]) });
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
				add(f.born.place, { id: f.id, name: t(f.name), what: 'born', when: year(f.born.date) });
			}
			if (f.died) {
				add(f.died.place, { id: f.id, name: t(f.name), what: 'died', when: year(f.died.date) });
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
			.map((k) => ({ id: k, label: Term('kind.place', k) }))
	);

	const active = $derived(query.trim().length > 0 || kinds.length > 0);
	// Alphabetical in the language being read: the English collator would leave
	// every Greek name in whatever order the file happens to list it.
	const sorted = $derived([...data.places].sort((a, b) => byText(current(a).name, current(b).name)));
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
				...p.names.flatMap((n) => both(n.name))
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
	<title>{ui('page.title', { page: ui('page.places'), site: ui('site.name') })}</title>
	<meta name="description" content={ui('places.description')} />
</svelte:head>

<h1>{ui('page.places')}</h1>
<p class="lead">{ui('places.lead')}</p>

<FilterBar
	bind:query
	placeholder={ui('places.placeholder')}
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
			label={ui('facet.kind')}
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
				<span class="name">{t(now.name)}</span>
				{#if alt(now.name)}<span class="alt">{alt(now.name)}</span>{/if}
				<span class="kind">{term('kind.place', p.kind)}</span>
			</div>
			<p class="where">
				{#if p.atom}
					<span>{atomName.get(p.atom) ?? p.atom}</span>
					{#if regionOf.get(p.atom) && regionOf.get(p.atom) !== atomName.get(p.atom)}
						<span class="region">{regionOf.get(p.atom)}</span>
					{/if}
				{:else}
					<span class="region">{ui('places.outside')}</span>
				{/if}
				<span class="coords">{ui('places.coords', { lat: num(p.lat, 2), lon: num(p.lon, 2) })}</span
				>
			</p>

			{#if past.length}
				<p class="formerly">
					{ui('places.alsoknown')}
					{#each past as n, i (n.name.en)}{i ? '; ' : ' '}<span class="oldname"
							>{t(n.name)}</span
						>{#if alt(n.name)}<span class="alt"> {alt(n.name)}</span>{/if}{#if n.from || n.to}<span
							class="span"
						>
							{n.from ? year(n.from) : '…'}–{n.to ? year(n.to) : '…'}</span
						>{/if}{/each}
				</p>
			{/if}

			{#if here.length > FOLD_AT}
				<details class="fold">
					<summary>{ui('places.eventshere', { n: here.length })}</summary>
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
							<span class="what">{term('what', l.what)}</span>
						</li>
					{/each}
				</ul>
			{/if}
			{#if !here.length && !lives.length}
				<p class="none">{ui('places.nothing')}</p>
			{/if}
		</li>
	{:else}
		<li class="empty">{ui('places.empty')}</li>
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
	.alt {
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
