<script lang="ts">
	import { t } from '$lib/lang.svelte';
	import { ui } from '$lib/ui';
	import Significance from '$lib/Significance.svelte';
	import { atlasHref } from '$lib/viewstate';

	let { data } = $props();
	const thread = $derived(data.thread);
	const years = $derived(
		`${thread.span[0].slice(0, 4)}–${thread.span[1].slice(0, 4)}`
	);
</script>

<svelte:head>
	<title>{ui('page.title', { page: t(thread.name), site: ui('site.name') })}</title>
	<meta name="description" content={t(thread.summary)} />
</svelte:head>

<article>
	<p class="crumb"><a href="/threads">{ui('page.threads')}</a> <span class="muted">{years}</span></p>
	<h1>{t(thread.name)}</h1>
	<p class="summary">{t(thread.summary)}</p>
	<p class="crumb">
		<a href="/events?threads={thread.id}">{ui('thread.see', { n: thread.events.length })}</a>
	</p>

	<ol class="arc">
		{#each thread.events as e, i (e.id)}
			<li>
				<span class="when">{e.period[0].slice(0, 4)}</span>
				<div>
					<a class="title" href="/events/{e.id}">{t(e.title)}</a>
					<p class="meta">
						<span class="muted">{ui('thread.step', { i: i + 1, n: thread.events.length })}</span>
						<Significance significance={e.significance} compact />
						<a href={atlasHref({ on: e.period[0], event: e.id })}>{ui('events.openatlas')}</a>
					</p>
				</div>
			</li>
		{/each}
	</ol>
</article>

<style>
	article {
		max-width: 68ch;
	}
	.crumb {
		font-size: 0.85rem;
		margin: 0 0 6px;
	}
	.muted {
		color: var(--ink-soft);
	}
	h1 {
		font-size: 1.9rem;
		margin: 0 0 6px;
	}
	.summary {
		color: var(--ink-soft);
		margin: 0 0 24px;
	}
	.arc {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	.arc li {
		display: flex;
		gap: 14px;
		padding: 10px 0;
		border-top: 1px solid var(--rule);
	}
	.when {
		flex: 0 0 5ch;
		color: var(--ink-soft);
		font-variant-numeric: tabular-nums;
		font-size: 0.85rem;
		padding-top: 2px;
	}
	.title {
		font-weight: 600;
	}
	.meta {
		display: flex;
		align-items: center;
		gap: 14px;
		flex-wrap: wrap;
		margin: 3px 0 0;
		font-size: 0.85rem;
	}
</style>
