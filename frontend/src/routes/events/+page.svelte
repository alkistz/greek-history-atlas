<script lang="ts">
	import { prettyPeriod, year } from '$lib/time';
	import { atlasHref } from '$lib/viewstate';

	let { data } = $props();

	const decades = $derived.by(() => {
		const out: { decade: string; events: typeof data.events }[] = [];
		for (const e of data.events) {
			const decade = `${e.period[0].slice(0, 3)}0s`;
			const last = out.at(-1);
			if (last?.decade === decade) last.events.push(e);
			else out.push({ decade, events: [e] });
		}
		return out;
	});
</script>

<svelte:head>
	<title>Events — Greek History Atlas</title>
	<meta name="description" content="Every event in the atlas, in order." />
</svelte:head>

<h1>Events</h1>
<p class="lead">
	{data.events.length} events, in order. Each one opens the map on the day it happened.
</p>

{#each decades as g (g.decade)}
	<section>
		<h2>{g.decade}</h2>
		<ol class="events">
			{#each g.events as e (e.id)}
				<li>
					<span class="when">{year(e.period[0])}</span>
					<div>
						<a class="title" href="/events/{e.id}">{e.title.en}</a>
						<p>{e.summary.en}</p>
						<p class="meta">
							<span>{prettyPeriod(e.period, e.precision)}</span>
							<a href={atlasHref({ on: e.period[0], frame: e.frame, event: e.id })}>
								Open on the atlas
							</a>
						</p>
					</div>
				</li>
			{/each}
		</ol>
	</section>
{/each}

<style>
	h1 {
		font-size: 1.9rem;
		margin: 0 0 4px;
	}
	.lead {
		color: var(--ink-soft);
		margin: 0 0 24px;
		max-width: 60ch;
	}
	section {
		max-width: 76ch;
	}
	h2 {
		font-family: var(--mono);
		font-size: 0.78rem;
		letter-spacing: 0.1em;
		color: var(--ink-soft);
		margin: 26px 0 0;
		padding-bottom: 4px;
		border-bottom: 1px solid var(--rule);
	}
	.events {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	.events li {
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
	.events p {
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
