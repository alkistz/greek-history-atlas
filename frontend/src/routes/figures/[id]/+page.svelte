<script lang="ts">
	import Atlas, { type MapPin } from '$lib/Atlas.svelte';
	import Citation from '$lib/Citation.svelte';
	import Strip, { type StripMark } from '$lib/Strip.svelte';
	import { t } from '$lib/lang.svelte';
	import { term, ui } from '$lib/ui';
	import { daysBetween, prettyDate, prettyMonth, toDay, year } from '$lib/time';
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

	// Where the life began and ended, as pins; the map is drawn on the day of the
	// figure's first event, or of their birth, so the colours are of their time.
	const pins = $derived.by((): MapPin[] => {
		const out: MapPin[] = [];
		const add = (ev: FigureDetail['born'], what: string) => {
			if (!ev?.place) return;
			out.push({
				id: `${what}-${ev.place.id}`,
				lon: ev.place.lon,
				lat: ev.place.lat,
				label: `${term('what', what)} · ${t(ev.place.name)}`
			});
		};
		add(figure.born, 'born');
		add(figure.died, 'died');
		return out;
	});
	const mapDate = $derived(
		figure.events[0]?.period[0] ?? figure.born?.date ?? data.meta.range.from
	);
	const inRange = $derived(mapDate >= data.meta.range.from && mapDate <= data.meta.range.to);

	const origin = $derived(data.meta.range.from);
	const maxDay = $derived(daysBetween(origin, data.meta.range.to));
	const span = $derived.by((): [number, number] | null => {
		if (!figure.born) return null;
		const from = toDay(figure.born.date, origin);
		const to = figure.died ? toDay(figure.died.date, origin) : maxDay;
		return [from, to];
	});
	const marks = $derived.by((): StripMark[] =>
		figure.events.map((e) => ({
			id: e.id,
			day: toDay(e.period[0], origin),
			title: `${year(e.period[0])} — ${t(e.title)}`,
			href: `/events/${e.id}`
		}))
	);
	const hasMap = $derived(pins.length > 0 || figure.events.length > 0);
</script>

<svelte:head>
	<title>{ui('page.title', { page: t(figure.name), site: ui('site.name') })}</title>
</svelte:head>

<article class="figure" class:withmap={hasMap}>
	{#if hasMap}
		<aside class="side">
			<figure class="map">
				<Atlas
					atoms={data.atoms.features}
					land={data.land}
					meta={data.meta}
					control={data.control}
					date={inRange ? mapDate : data.meta.range.from}
					{pins}
					showLabels={false}
					interactive={false}
				/>
			</figure>
			<div class="strip">
				<p class="label">{ui('figure.strip')}</p>
				<Strip {origin} {maxDay} {marks} {span} label={ui('figure.strip')} />
			</div>
		</aside>
	{/if}

	<div class="text">
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
	</div>
</article>

<style>
	.figure {
		max-width: 66ch;
	}
	.figure.withmap {
		max-width: none;
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr);
		gap: 32px;
		align-items: start;
	}
	.side {
		position: sticky;
		top: calc(var(--header-h, 0px) + 12px);
	}
	.map {
		margin: 0;
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
		padding: 8px;
	}
	.strip {
		margin-top: 10px;
		padding: 8px 12px 4px;
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
	}
	.label {
		margin: 0 0 4px;
		color: var(--ink-soft);
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
	}
	.text {
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
	@media (max-width: 900px) {
		.figure.withmap {
			grid-template-columns: 1fr;
		}
		.side {
			position: static;
		}
	}
</style>
