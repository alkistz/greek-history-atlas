<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import FilterBar from '$lib/FilterBar.svelte';
	import IndexPage from '$lib/IndexPage.svelte';
	import Strip from '$lib/Strip.svelte';
	import { both, t } from '$lib/lang.svelte';
	import { daysBetween, toDay } from '$lib/time';
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

	const origin = $derived(data.meta.range.from);
	const maxDay = $derived(daysBetween(origin, data.meta.range.to));
	const years = (span: [string, string]) =>
		`${span[0].slice(0, 4)}–${span[1].slice(0, 4)}`;
</script>

<svelte:head>
	<title>{ui('page.title', { page: ui('page.threads'), site: ui('site.name') })}</title>
	<meta name="description" content={ui('threads.description')} />
</svelte:head>

<IndexPage title={ui('page.threads')} lead={ui('threads.lead')}>
	{#snippet filters()}
		<FilterBar
			bind:query
			placeholder={ui('threads.placeholder')}
			shown={shown.length}
			total={data.threads.length}
			noun="threads"
			{active}
			onclear={() => (query = '')}
		/>
	{/snippet}

	<ol class="threads">
		{#each shown as thread (thread.id)}
			<li class="card">
				<p class="top">
					<span class="when">{years(thread.span)}</span>
					<span class="count">{ui('threads.count', { n: thread.count })}</span>
				</p>
				<a class="title" href="/threads/{thread.id}">{t(thread.name)}</a>
				<p class="summary">{t(thread.summary)}</p>
				<!-- Where on the two centuries the arc lies, as a bar. -->
				<Strip
					{origin}
					{maxDay}
					span={[toDay(thread.span[0], origin), toDay(thread.span[1], origin)]}
					label={`${t(thread.name)}, ${years(thread.span)}`}
				/>
				<p class="meta">
					<a href="/events?threads={thread.id}">{ui('threads.filter')}</a>
				</p>
			</li>
		{:else}
			<p class="empty">{ui('threads.empty')}</p>
		{/each}
	</ol>
</IndexPage>

<style>
	.threads {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 360px), 1fr));
		gap: 10px;
	}
	.card {
		display: flex;
		flex-direction: column;
		gap: 2px;
		padding: 12px 14px;
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
		transition: border-color 120ms ease;
	}
	.card:hover {
		border-color: var(--ink-soft);
	}
	.card p {
		margin: 0;
	}
	.top {
		display: flex;
		align-items: baseline;
		gap: 10px;
		font-size: 0.78rem;
		color: var(--ink-soft);
	}
	.when {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
	}
	.count {
		text-transform: uppercase;
		letter-spacing: 0.06em;
		font-size: 0.72rem;
	}
	.title {
		font-family: var(--serif);
		font-size: 1.15rem;
		font-weight: 600;
		text-decoration: none;
		color: var(--ink);
	}
	.title:hover {
		color: var(--accent);
	}
	.summary {
		margin-top: 4px !important;
		margin-bottom: 8px !important;
		color: var(--ink-soft);
		font-size: 0.9rem;
	}
	.meta {
		margin-top: 6px !important;
		font-size: 0.82rem;
	}
	.empty {
		color: var(--ink-soft);
	}
	@media (prefers-reduced-motion: reduce) {
		.card {
			transition: none;
		}
	}
</style>
