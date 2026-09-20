<script lang="ts">
	import { atlasHref } from '$lib/viewstate';

	let { data } = $props();
	const thread = $derived(data.thread);
	const years = $derived(
		`${thread.span[0].slice(0, 4)}–${thread.span[1].slice(0, 4)}`
	);
</script>

<svelte:head>
	<title>{thread.name.en} — Greek History Atlas</title>
	<meta name="description" content={thread.summary.en} />
</svelte:head>

<article>
	<p class="crumb"><a href="/threads">Threads</a> <span class="muted">{years}</span></p>
	<h1>{thread.name.en}</h1>
	<p class="summary">{thread.summary.en}</p>

	<ol class="arc">
		{#each thread.events as e, i (e.id)}
			<li>
				<span class="when">{e.period[0].slice(0, 4)}</span>
				<div>
					<a class="title" href="/events/{e.id}">{e.title.en}</a>
					<p class="meta">
						<span class="muted">{i + 1} of {thread.events.length}</span>
						<a href={atlasHref({ on: e.period[0], event: e.id })}>Open on the atlas</a>
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
		gap: 14px;
		margin: 3px 0 0;
		font-size: 0.85rem;
	}
</style>
