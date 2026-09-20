<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import Citation from '$lib/Citation.svelte';
	import FilterBar from '$lib/FilterBar.svelte';
	import { both, t } from '$lib/lang.svelte';
	import { Term, ui } from '$lib/ui';
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
		return present.map((k) => ({ id: k, label: Term('kind.source', k) }));
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
					.flatMap((c) => both(c.title))
					.join(' ')
			);
		})
	);

	const uncited = $derived(data.sources.filter((s) => countOf(s) === 0).length);
</script>

<svelte:head>
	<title>{ui('page.title', { page: ui('page.sources'), site: ui('site.name') })}</title>
	<meta name="description" content={ui('sources.description')} />
</svelte:head>

<h1>{ui('page.sources')}</h1>
<p class="lead">
	{ui('sources.lead')}
	{#if uncited}
		{ui('sources.uncited', { n: uncited, total: data.sources.length })}
	{/if}
</p>

<FilterBar
	bind:query
	placeholder={ui('sources.placeholder')}
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
				label={ui('facet.kind')}
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
					{#each [{ key: 'events', label: ui('page.events'), rows: s.cited_by.events, base: '/events' }, { key: 'figures', label: ui('page.figures'), rows: s.cited_by.figures, base: '/figures' }, { key: 'instruments', label: ui('page.instruments'), rows: s.cited_by.instruments, base: '/instruments' }] as group (group.key)}
						{#if group.rows.length}
							<p class="group">
								<span class="glabel">{group.label}</span>
								{#each group.rows as r, i (r.id)}{i ? ', ' : ''}<a href="{group.base}/{r.id}"
										>{t(r.title)}</a
									>{/each}
							</p>
						{/if}
					{/each}
				</div>
			{:else}
				<p class="none">{ui('sources.none')}</p>
			{/if}
		</li>
	{:else}
		<li class="empty">{ui('sources.empty')}</li>
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
