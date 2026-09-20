<script lang="ts">
	import Citation from '$lib/Citation.svelte';
	import ReviewNote from '$lib/ReviewNote.svelte';
	import { prettyDate, year } from '$lib/time';
	import type { FigureDetail } from '$lib/types';

	let { data } = $props();
	const figure = $derived(data.figure);

	// `month` and `circa` are real precisions in this corpus -- two figures are
	// dated to a month and three to a circa year -- so saying "day or year" would
	// print a false precision for five people.
	function when(ev: NonNullable<FigureDetail['born']>): string {
		if (ev.precision === 'day') return prettyDate(ev.date);
		if (ev.precision === 'month') {
			return new Date(ev.date).toLocaleDateString('en-GB', {
				month: 'long',
				year: 'numeric',
				timeZone: 'UTC'
			});
		}
		return ev.precision === 'circa' ? `c. ${year(ev.date)}` : year(ev.date);
	}
	function life(ev: FigureDetail['born']): string {
		if (!ev) return '';
		return ev.place ? `${when(ev)}, ${ev.place.name.en}` : when(ev);
	}
</script>

<svelte:head>
	<title>{figure.name.en} — Greek History Atlas</title>
</svelte:head>

<article class="figure">
	<p class="kicker">{figure.roles.join(' · ')}</p>
	<h1>{figure.name.en}</h1>
	{#if figure.also_known_as.length}
		<p class="aka">{figure.also_known_as.map((n) => n.en).join('; ')}</p>
	{/if}
	<dl class="life">
		{#if figure.born}
			<dt>Born</dt>
			<dd>
				{life(figure.born)}
				{#if figure.born.as_written}
					<span class="old">Old Style {figure.born.as_written.date}</span>
				{/if}
			</dd>
		{/if}
		{#if figure.died}
			<dt>Died</dt>
			<dd>
				{life(figure.died)}
				{#if figure.died.as_written}
					<span class="old">Old Style {figure.died.as_written.date}</span>
				{/if}
			</dd>
		{/if}
	</dl>

	<p class="summary">{figure.summary.en}</p>
	{#if figure.body_html}
		<div class="prose">{@html figure.body_html.en}</div>
	{/if}

	{#if figure.events.length}
		<h2>Events</h2>
		<ol class="plain">
			{#each figure.events as e (e.id)}
				<li>
					<span class="mono">{year(e.period[0])}</span>
					<a href="/events/{e.id}">{e.title.en}</a>
					<span class="muted">{e.role}</span>
				</li>
			{/each}
		</ol>
	{/if}

	{#if figure.sources.length}
		<h2>Sources</h2>
		<ul class="plain sources">
			{#each figure.sources as s (s.id)}
				<li><a href="/sources#{s.id}"><Citation source={s} /></a></li>
			{/each}
		</ul>
	{/if}

	<ReviewNote review={figure.review} />
</article>

<style>
	.figure {
		max-width: 66ch;
	}
	.kicker {
		margin: 0;
		color: var(--ink-soft);
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	h1 {
		font-size: 1.9rem;
		margin: 4px 0 4px;
	}
	.aka {
		margin: 0 0 8px;
		color: var(--ink-soft);
		font-style: italic;
	}
	.life {
		display: grid;
		grid-template-columns: 6ch 1fr;
		gap: 2px 10px;
		margin: 10px 0 16px;
		font-size: 0.9rem;
	}
	.life dt {
		color: var(--ink-soft);
	}
	.life dd {
		margin: 0;
	}
	/* The Julian date the sources give, beside the Gregorian one stored. */
	.old {
		margin-left: 8px;
		font-family: var(--mono);
		font-size: 0.78rem;
		color: var(--ink-soft);
	}
	.summary {
		font-size: 1.05rem;
		color: var(--ink-soft);
	}
	.prose :global(p) {
		margin: 0 0 1em;
	}
	h2 {
		font-size: 1.05rem;
		margin: 22px 0 6px;
	}
	.plain {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	.plain li {
		margin: 3px 0;
	}
	.plain li > * + * {
		margin-left: 10px;
	}
	.mono {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.85rem;
		color: var(--ink-soft);
	}
	.muted {
		color: var(--ink-soft);
		font-size: 0.85rem;
	}
	.sources {
		font-size: 0.88rem;
		color: var(--ink-soft);
	}
	.sources a {
		text-decoration: none;
	}
	.sources a:hover {
		text-decoration: underline;
	}
</style>
