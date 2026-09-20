<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import Citation from '$lib/Citation.svelte';
	import FilterBar from '$lib/FilterBar.svelte';
	import { list, matches, params, replaceParams } from '$lib/urlstate';

	let { data } = $props();

	let query = $state(untrack(() => page.url.searchParams.get('q') ?? ''));
	let kinds = $state<string[]>(untrack(() => list(page.url, 'kinds')));

	$effect(() => replaceParams(params({ q: query, kinds })));

	const countOf = (s: (typeof data.sources)[number]) =>
		s.cited_by.events.length + s.cited_by.figures.length + s.cited_by.instruments.length;

	// Only offered once there is more than one kind to choose between; every work
	// in the corpus is currently a book, and a lone chip filters nothing.
	const kindItems = $derived.by(() => {
		const present = [...new Set(data.sources.map((s) => s.kind))].sort();
		if (present.length < 2) return [];
		return present.map((k) => ({ id: k, label: k[0].toUpperCase() + k.slice(1) }));
	});

	const active = $derived(query.trim().length > 0 || kinds.length > 0);
	const shown = $derived(
		data.sources.filter((s) => {
			if (kinds.length && !kinds.includes(s.kind)) return false;
			return matches(
				query,
				s.title,
				s.author,
				s.publisher,
				s.kind,
				s.year ? String(s.year) : null,
				s.isbn,
				s.doi,
				// The titles of what cites it, so a work can be found from its subject.
				[...s.cited_by.events, ...s.cited_by.figures, ...s.cited_by.instruments]
					.map((c) => c.title.en)
					.join(' ')
			);
		})
	);

	const uncited = $derived(data.sources.filter((s) => countOf(s) === 0).length);
</script>

<svelte:head>
	<title>Sources — Greek History Atlas</title>
	<meta name="description" content="Every work the atlas cites, and what cites it." />
</svelte:head>

<h1>Sources</h1>
<p class="lead">
	Every work the corpus cites, with the entries that cite it. Citations are authored on the
	entry, so this list is the inverse: the way to ask what one book is carrying.
	{#if uncited}
		{uncited} of {data.sources.length} are listed but not yet cited anywhere.
	{/if}
</p>

<FilterBar
	bind:query
	placeholder="Search authors, titles, publishers, what they support…"
	shown={shown.length}
	total={data.sources.length}
	noun="works"
	{active}
	onclear={() => {
		query = '';
		kinds = [];
	}}
>
	{#snippet facets()}
		{#if kindItems.length}
			<ChipGroup
				label="Kind"
				items={kindItems}
				selected={kinds}
				ontoggle={(id) => (kinds = kinds.includes(id) ? kinds.filter((k) => k !== id) : [...kinds, id])}
				onclear={() => (kinds = [])}
			/>
		{/if}
	{/snippet}
</FilterBar>

<ol class="sources">
	{#each shown as s (s.id)}
		<li id={s.id}>
			<p class="work"><Citation source={{ ...s, locator: null }} full /></p>
			{#if countOf(s)}
				<div class="cited">
					{#each [{ label: 'Events', rows: s.cited_by.events, base: '/events' }, { label: 'Figures', rows: s.cited_by.figures, base: '/figures' }, { label: 'Instruments', rows: s.cited_by.instruments, base: '/instruments' }] as group (group.label)}
						{#if group.rows.length}
							<p class="group">
								<span class="glabel">{group.label}</span>
								{#each group.rows as r, i (r.id)}{i ? ', ' : ''}<a href="{group.base}/{r.id}"
										>{r.title.en}</a
									>{/each}
							</p>
						{/if}
					{/each}
				</div>
			{:else}
				<p class="none">Listed, but nothing cites it yet.</p>
			{/if}
		</li>
	{:else}
		<li class="empty">No work matches that.</li>
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
	.sources {
		list-style: none;
		padding: 0;
		margin: 0;
		max-width: 76ch;
		border-top: 1px solid var(--rule);
	}
	.sources > li {
		padding: 12px 0;
		border-bottom: 1px solid var(--rule);
		/* So a jump from a citation link does not land under the sticky header. */
		scroll-margin-top: 16px;
	}
	.sources > li:target {
		background: var(--panel);
		box-shadow: inset 2px 0 0 var(--accent);
		padding-left: 10px;
	}
	.work {
		margin: 0;
	}
	.work :global(em) {
		color: var(--ink);
		font-size: 0.95rem;
	}
	.cited {
		margin-top: 4px;
	}
	.group {
		margin: 2px 0 0;
		font-size: 0.85rem;
		color: var(--ink-soft);
	}
	.glabel {
		display: inline-block;
		min-width: 9ch;
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	.none {
		margin: 4px 0 0;
		font-size: 0.85rem;
		font-style: italic;
		color: var(--ink-soft);
	}
	.empty {
		display: block;
		color: var(--ink-soft);
		padding: 14px 0;
	}
</style>
