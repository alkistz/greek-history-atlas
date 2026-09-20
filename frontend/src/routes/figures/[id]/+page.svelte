<script lang="ts">
	import Citation from '$lib/Citation.svelte';
	import { t } from '$lib/lang.svelte';
	import { term, ui } from '$lib/ui';
	import ReviewNote from '$lib/ReviewNote.svelte';
	import { prettyDate, prettyMonth, year } from '$lib/time';
	import type { FigureDetail } from '$lib/types';

	let { data } = $props();
	const figure = $derived(data.figure);

	// `month` and `circa` are real precisions in this corpus -- two figures are
	// dated to a month and three to a circa year -- so saying "day or year" would
	// print a false precision for five people.
	function when(ev: NonNullable<FigureDetail['born']>): string {
		if (ev.precision === 'day') return prettyDate(ev.date);
		if (ev.precision === 'month') return prettyMonth(ev.date);
		return ev.precision === 'circa' ? ui('date.circa', { year: year(ev.date) }) : year(ev.date);
	}
	function life(ev: FigureDetail['born']): string {
		if (!ev) return '';
		return ev.place ? `${when(ev)}, ${t(ev.place.name)}` : when(ev);
	}
</script>

<svelte:head>
	<title>{ui('page.title', { page: t(figure.name), site: ui('site.name') })}</title>
</svelte:head>

<article class="figure">
	<p class="kicker">{figure.roles.map((r) => term('role.figure', r)).join(' · ')}</p>
	<h1>{t(figure.name)}</h1>
	{#if figure.also_known_as.length}
		<p class="aka">{figure.also_known_as.map(t).join('; ')}</p>
	{/if}
	<dl class="life">
		{#if figure.born}
			<dt>{ui('figure.born')}</dt>
			<dd>
				{life(figure.born)}
				{#if figure.born.as_written}
					<span class="old">{ui('date.oldstyle', { date: figure.born.as_written.date })}</span>
				{/if}
			</dd>
		{/if}
		{#if figure.died}
			<dt>{ui('figure.died')}</dt>
			<dd>
				{life(figure.died)}
				{#if figure.died.as_written}
					<span class="old">{ui('date.oldstyle', { date: figure.died.as_written.date })}</span>
				{/if}
			</dd>
		{/if}
	</dl>

	<p class="summary">{t(figure.summary)}</p>
	{#if figure.body_html}
		<div class="prose">{@html t(figure.body_html)}</div>
	{/if}

	{#if figure.events.length}
		<h2>{ui('page.events')}</h2>
		<ol class="plain">
			{#each figure.events as e (e.id)}
				<li>
					<span class="mono">{year(e.period[0])}</span>
					<a href="/events/{e.id}">{t(e.title)}</a>
					<span class="muted">{term('role.event', e.role)}</span>
				</li>
			{/each}
		</ol>
	{/if}

	{#if figure.sources.length}
		<h2>{ui('page.sources')}</h2>
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
