<script lang="ts">
	import { prettyDate, year } from '$lib/time';
	import { atlasHref } from '$lib/viewstate';

	let { data } = $props();

	const polityName = $derived(new Map(data.meta.polities.map((p) => [p.id, p.name.en])));
	const sorted = $derived([...data.instruments].sort((a, b) => a.signed.localeCompare(b.signed)));
</script>

<svelte:head>
	<title>Instruments — Greek History Atlas</title>
	<meta
		name="description"
		content="The treaties, protocols and conventions that moved the frontier."
	/>
</svelte:head>

<h1>Instruments</h1>
<p class="lead">
	The treaties, protocols and conventions that moved the frontier. Each one links to the map on the
	day it took effect.
</p>

<ol class="instruments">
	{#each sorted as i (i.id)}
		<li>
			<span class="when">{year(i.signed)}</span>
			<div>
				<a class="title" href="/instruments/{i.id}">{i.name.en}</a>
				<span class="kind">{i.kind}</span>
				<p class="parties">{i.parties.map((p) => polityName.get(p) ?? p).join(' · ')}</p>
				{#if i.summary}<p>{i.summary.en}</p>{/if}
				<p class="meta">
					<span>Signed {prettyDate(i.signed)}</span>
					<a href={atlasHref({ on: i.signed })}>Open on the atlas</a>
				</p>
			</div>
		</li>
	{/each}
</ol>

<style>
	h1 {
		font-size: 1.9rem;
		margin: 0 0 4px;
	}
	.lead {
		color: var(--ink-soft);
		margin: 0 0 20px;
		max-width: 64ch;
	}
	.instruments {
		list-style: none;
		padding: 0;
		margin: 0;
		max-width: 76ch;
		border-top: 1px solid var(--rule);
	}
	.instruments li {
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
	.kind {
		margin-left: 8px;
		color: var(--ink-soft);
		font-size: 0.82rem;
	}
	.parties {
		margin: 2px 0 0;
		color: var(--ink-soft);
		font-size: 0.85rem;
	}
	.instruments p {
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
</style>
