<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import FilterBar from '$lib/FilterBar.svelte';
	import { both, t } from '$lib/lang.svelte';
	import { ui } from '$lib/ui';
	import { matches, params, replaceParams } from '$lib/urlstate';

	let { data } = $props();

	let query = $state(untrack(() => page.url.searchParams.get('q') ?? ''));
	$effect(() => replaceParams(params({ q: query })));

	const active = $derived(query.trim().length > 0);
	const shown = $derived(
		data.threads.filter((thread) =>
			// The span too, so "1922" finds the three arcs that run through it.
			matches(query, ...both(thread.name), ...both(thread.summary), thread.span[0], thread.span[1])
		)
	);

	const years = (span: [string, string]) =>
		`${span[0].slice(0, 4)}–${span[1].slice(0, 4)}`;
</script>

<svelte:head>
	<title>{ui('page.title', { page: ui('page.threads'), site: ui('site.name') })}</title>
	<meta name="description" content={ui('threads.description')} />
</svelte:head>

<h1>{ui('page.threads')}</h1>
<p class="lead">{ui('threads.lead')}</p>

<FilterBar
	bind:query
	placeholder={ui('threads.placeholder')}
	shown={shown.length}
	total={data.threads.length}
	noun="threads"
	{active}
	onclear={() => (query = '')}
/>

<ol class="threads">
	{#each shown as thread (thread.id)}
		<li>
			<span class="when">{years(thread.span)}</span>
			<div>
				<a class="title" href="/threads/{thread.id}">{t(thread.name)}</a>
				<span class="count">{ui('threads.count', { n: thread.count })}</span>
				<p>{t(thread.summary)}</p>
				<p class="meta">
					<a href="/events?threads={thread.id}">{ui('threads.filter')}</a>
				</p>
			</div>
		</li>
	{:else}
		<p class="empty">{ui('threads.empty')}</p>
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
