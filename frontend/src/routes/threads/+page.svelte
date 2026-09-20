<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import FilterBar from '$lib/FilterBar.svelte';
	import { matches, params, replaceParams } from '$lib/urlstate';

	let { data } = $props();

	let query = $state(untrack(() => page.url.searchParams.get('q') ?? ''));
	$effect(() => replaceParams(params({ q: query })));

	const active = $derived(query.trim().length > 0);
	const shown = $derived(
		data.threads.filter((t) =>
			// The span too, so "1922" finds the three arcs that run through it.
			matches(query, t.name.en, t.name.el, t.summary.en, t.summary.el, t.span[0], t.span[1])
		)
	);

	const years = (span: [string, string]) =>
		`${span[0].slice(0, 4)}–${span[1].slice(0, 4)}`;
</script>

<svelte:head>
	<title>Threads — Greek History Atlas</title>
	<meta name="description" content="The narrative arcs the events belong to." />
</svelte:head>

<h1>Threads</h1>
<p class="lead">
	The orders in which the events are worth reading. An event can sit on several arcs at
	once: 1922 belongs to the Great Idea, to the Asia Minor campaign and to the National
	Schism, and each tells it differently.
</p>

<FilterBar
	bind:query
	placeholder="Search threads and years…"
	shown={shown.length}
	total={data.threads.length}
	noun="threads"
	{active}
	onclear={() => (query = '')}
/>

<ol class="threads">
	{#each shown as t (t.id)}
		<li>
			<span class="when">{years(t.span)}</span>
			<div>
				<a class="title" href="/threads/{t.id}">{t.name.en}</a>
				<span class="count">{t.count} events</span>
				<p>{t.summary.en}</p>
				<p class="meta">
					<a href="/events?threads={t.id}">Filter the ledger by this arc</a>
				</p>
			</div>
		</li>
	{:else}
		<p class="empty">No thread matches that.</p>
	{/each}
</ol>

<style>
	h1 {
		font-size: 1.9rem;
		margin: 0 0 4px;
	}
	.lead {
		color: var(--ink-soft);
		max-width: 62ch;
		margin: 0 0 20px;
	}
	.threads {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	.threads li {
		display: flex;
		gap: 14px;
		padding: 11px 0;
		border-top: 1px solid var(--rule);
	}
	.when {
		flex: 0 0 8.5ch;
		color: var(--ink-soft);
		font-variant-numeric: tabular-nums;
		font-size: 0.85rem;
		padding-top: 2px;
	}
	.title {
		font-weight: 600;
	}
	.count {
		margin-left: 8px;
		color: var(--ink-soft);
		font-size: 0.74rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	.threads p {
		margin: 4px 0 0;
		color: var(--ink-soft);
		font-size: 0.92rem;
		max-width: 68ch;
	}
	.meta {
		font-size: 0.82rem;
	}
	.empty {
		color: var(--ink-soft);
	}
</style>
