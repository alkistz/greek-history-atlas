<!--
	The front page: what the atlas is, how to read its map, and the ways in.

	The atlas itself is an instrument with a lot on it at once. This page exists
	so that a first visit starts with one sentence and a moving picture rather
	than with a timeline, a ledger and a legend; everything below the hero is a
	door into one of the other pages, chosen from the corpus rather than written
	here, so it grows with the content.
-->
<script lang="ts">
	import HeroMap from '$lib/HeroMap.svelte';
	import Swatch from '$lib/Swatch.svelte';
	import { t } from '$lib/lang.svelte';
	import { daysBetween, toDay, year } from '$lib/time';
	import { ui, type UiKey } from '$lib/ui';
	import { ATLAS_PATH, atlasHref } from '$lib/viewstate';

	let { data } = $props();

	const origin = $derived(data.meta.range.from);
	const maxDay = $derived(daysBetween(origin, data.meta.range.to));
	const pct = (iso: string) => (toDay(iso, origin) / maxDay) * 100;

	// The turning points are the events the corpus rates highest, so the list is
	// the corpus's own judgment and changes when a rating does.
	const TOP = 5;
	const turning = $derived(
		data.events
			.filter((e) => e.significance >= TOP)
			.sort((a, b) => a.period[0].localeCompare(b.period[0]))
	);

	const eventDate = $derived(new Map(data.events.map((e) => [e.id, e.period[0]])));
	const threads = $derived(
		[...data.threads].sort(
			(a, b) => a.span[0].localeCompare(b.span[0]) || a.span[1].localeCompare(b.span[1])
		)
	);
	const ticks = [1850, 1900, 1950, 2000];

	// The three ways a territory is drawn, with real polities so the swatches
	// carry the map's own colours.
	const colourOf = $derived(new Map(data.meta.polities.map((p) => [p.id, p.colour ?? 'transparent'])));

	const counts = $derived({ ...data.counts, instruments: data.meta.instruments.length });
	const doors: { href: string; key: 'events' | 'threads' | 'figures' | 'instruments' | 'places' | 'sources' }[] = [
		{ href: '/events', key: 'events' },
		{ href: '/threads', key: 'threads' },
		{ href: '/figures', key: 'figures' },
		{ href: '/instruments', key: 'instruments' },
		{ href: '/places', key: 'places' },
		{ href: '/sources', key: 'sources' }
	];
	const pageKey = (k: string) => `page.${k}` as UiKey;
	const descKey = (k: string) => `${k}.description` as UiKey;
</script>

<svelte:head>
	<title>{ui('site.name')}</title>
</svelte:head>

<main class="home">
	<section class="hero">
		<div class="pitch">
			<p class="eyebrow">{ui('home.eyebrow', { from: year(origin) })}</p>
			<h1>{ui('home.title')}</h1>
			<p class="lead">
				{ui('home.lead', {
					events: counts.events,
					figures: counts.figures,
					instruments: counts.instruments
				})}
			</p>
			<p class="ctas">
				<a class="cta primary" href={ATLAS_PATH}>{ui('home.cta.atlas')} →</a>
				<a class="cta" href="#threads">{ui('home.cta.threads')}</a>
			</p>
		</div>
		<HeroMap atoms={data.atoms.features} land={data.land} meta={data.meta} control={data.control} />
	</section>

	<section class="how" aria-labelledby="how-h">
		<h2 id="how-h" class="visually-hidden">{ui('home.how.title')}</h2>
		<ol>
			<li>
				<span class="step">1</span>
				<div>
					<h3>{ui('home.how.1.title')}</h3>
					<p>{ui('home.how.1.body')}</p>
					<ul class="swatches">
						<li><Swatch colour={colourOf.get('gr-kingdom') ?? ''} role="sovereign" polityId="gr-kingdom" />{ui('home.how.held')}</li>
						<li><Swatch colour={colourOf.get('germany') ?? ''} role="occupying" polityId="germany" />{ui('home.how.occupied')}</li>
						<li><Swatch colour={colourOf.get('gr-provisional') ?? ''} role="in revolt" polityId="gr-provisional" />{ui('home.how.revolt')}</li>
					</ul>
				</div>
			</li>
			<li>
				<span class="step">2</span>
				<div>
					<h3>{ui('home.how.2.title')}</h3>
					<p>{ui('home.how.2.body')}</p>
				</div>
			</li>
			<li>
				<span class="step">3</span>
				<div>
					<h3>{ui('home.how.3.title')}</h3>
					<p>{ui('home.how.3.body')}</p>
				</div>
			</li>
		</ol>
	</section>

	<section aria-labelledby="turning-h">
		<header class="section-head">
			<h2 id="turning-h">{ui('home.turning.title')}</h2>
			<p>{ui('home.turning.lead', { n: turning.length })}</p>
		</header>
		<ol class="turning">
			{#each turning as e (e.id)}
				<li>
					<a href={atlasHref({ on: e.period[0], frame: e.frame, event: e.id })}>
						<span class="when">{year(e.period[0])}</span>
						<span class="what">{t(e.title)}</span>
						<span class="why">{t(e.summary)}</span>
					</a>
				</li>
			{/each}
		</ol>
	</section>

	<section id="threads" aria-labelledby="threads-h">
		<header class="section-head">
			<h2 id="threads-h">{ui('home.threads.title')}</h2>
			<p>{ui('home.threads.lead', { n: threads.length })}</p>
		</header>
		<div class="arcs">
			<!-- One ruler for every arc, so where they overlap is the thing you see. -->
			<div class="arc axis" aria-hidden="true">
				<span></span>
				<div class="track">
					{#each ticks as y (y)}
						<span class="tick" style:left="{pct(`${y}-01-01`)}%">{y}</span>
					{/each}
				</div>
			</div>
			<ol>
				{#each threads as th (th.id)}
					<li>
						<a
							class="arc"
							href="/threads/{th.id}"
							title={`${t(th.name)}, ${year(th.span[0])}–${year(th.span[1])} · ${ui('threads.count', { n: th.count })}`}
						>
							<span class="name">{t(th.name)}</span>
							<span class="track">
								{#each ticks as y (y)}
									<span class="grid" style:left="{pct(`${y}-01-01`)}%"></span>
								{/each}
								<span
									class="bar"
									style:left="{pct(th.span[0])}%"
									style:width="max(6px, {pct(th.span[1]) - pct(th.span[0])}%)"
								></span>
								{#each th.events as id (id)}
									{@const d = eventDate.get(id)}
									{#if d}<span class="dot" style:left="{pct(d)}%"></span>{/if}
								{/each}
								<span class="years" style:left="{pct(th.span[1])}%"
									>{year(th.span[0])}–{year(th.span[1])}</span
								>
							</span>
						</a>
					</li>
				{/each}
			</ol>
		</div>
	</section>

	<section aria-labelledby="browse-h">
		<header class="section-head">
			<h2 id="browse-h">{ui('home.browse.title')}</h2>
		</header>
		<ul class="doors">
			{#each doors as d (d.key)}
				<li>
					<a href={d.href}>
						<span class="count">{counts[d.key]}</span>
						<span class="label">{ui(pageKey(d.key))}</span>
						<span class="desc">{ui(descKey(d.key))}</span>
					</a>
				</li>
			{/each}
		</ul>
	</section>
</main>

<style>
	.home {
		display: flex;
		flex-direction: column;
		gap: 56px;
	}
	section {
		scroll-margin-top: calc(var(--header-h, 0px) + 16px);
	}
	.visually-hidden {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip-path: inset(50%);
		white-space: nowrap;
	}

	/* ---- the hero ---- */
	.hero {
		display: grid;
		grid-template-columns: minmax(0, 5fr) minmax(0, 6fr);
		gap: 48px;
		align-items: center;
		padding-top: 12px;
	}
	.eyebrow {
		margin: 0 0 10px;
		font-family: var(--mono);
		font-size: 0.8rem;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--accent);
	}
	h1 {
		font-size: clamp(2.1rem, 1.4rem + 2.6vw, 3.4rem);
		line-height: 1.08;
		margin: 0 0 18px;
		letter-spacing: -0.02em;
	}
	.lead {
		font-size: 1.12rem;
		line-height: 1.6;
		color: var(--ink-soft);
		margin: 0 0 28px;
		max-width: 46ch;
	}
	.ctas {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		margin: 0;
	}
	.cta {
		display: inline-flex;
		align-items: center;
		padding: 10px 18px;
		border-radius: 999px;
		border: 1px solid var(--rule);
		background: var(--panel);
		color: var(--ink);
		text-decoration: none;
		font-weight: 600;
		transition:
			border-color 120ms ease,
			background 120ms ease;
	}
	.cta:hover {
		border-color: var(--ink-soft);
	}
	.cta.primary {
		background: var(--accent);
		border-color: var(--accent);
		color: var(--ground);
	}
	.cta.primary:hover {
		background: color-mix(in srgb, var(--accent) 86%, var(--ink));
	}
	.cta:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
	}

	/* ---- how to read the map ---- */
	.how ol {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 12px;
	}
	.how ol > li {
		display: flex;
		gap: 14px;
		padding: 16px 18px;
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
	}
	.step {
		flex: none;
		display: grid;
		place-items: center;
		width: 26px;
		height: 26px;
		border-radius: 50%;
		border: 1px solid var(--rule);
		font-family: var(--mono);
		font-size: 0.8rem;
		color: var(--ink-soft);
	}
	h3 {
		font-size: 1.05rem;
		margin: 1px 0 4px;
	}
	.how p {
		margin: 0;
		font-size: 0.92rem;
		color: var(--ink-soft);
	}
	.swatches {
		list-style: none;
		margin: 10px 0 0;
		padding: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 6px 14px;
		font-size: 0.82rem;
		color: var(--ink-soft);
	}
	.swatches li {
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}

	/* ---- section heads ---- */
	.section-head {
		margin-bottom: 16px;
	}
	h2 {
		font-size: 1.5rem;
		margin: 0 0 4px;
	}
	.section-head p {
		margin: 0;
		color: var(--ink-soft);
		max-width: 66ch;
	}

	/* ---- turning points ---- */
	.turning {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 250px), 1fr));
		gap: 10px;
	}
	.turning a {
		display: flex;
		flex-direction: column;
		gap: 4px;
		height: 100%;
		box-sizing: border-box;
		padding: 14px 16px;
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
		color: var(--ink);
		text-decoration: none;
		transition:
			border-color 120ms ease,
			transform 120ms ease;
	}
	.turning a:hover {
		border-color: var(--ink-soft);
		transform: translateY(-1px);
	}
	.turning a:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
	}
	.when {
		font-family: var(--mono);
		font-size: 0.85rem;
		color: var(--accent);
		font-variant-numeric: tabular-nums;
	}
	.what {
		font-family: var(--serif);
		font-size: 1.08rem;
		font-weight: 600;
		line-height: 1.3;
	}
	.why {
		font-size: 0.86rem;
		color: var(--ink-soft);
		display: -webkit-box;
		-webkit-line-clamp: 3;
		line-clamp: 3;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	/* ---- threads on one ruler ---- */
	.arcs {
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
		padding: 10px 14px 12px;
	}
	.arcs ol {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	.arc {
		display: grid;
		grid-template-columns: minmax(0, 15rem) minmax(0, 1fr);
		gap: 16px;
		align-items: center;
		padding: 5px 6px;
		margin: 0 -6px;
		border-radius: var(--radius);
		color: var(--ink);
		text-decoration: none;
	}
	a.arc:hover {
		background: var(--accent-soft);
	}
	a.arc:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: -2px;
	}
	.name {
		font-size: 0.92rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	a.arc:hover .name {
		color: var(--accent);
	}
	.track {
		position: relative;
		display: block;
		height: 18px;
	}
	/* The years sit at the end of the bar; the last arcs run to the present, so
	   they keep a right margin for the label to land in. */
	.arcs .track {
		margin-right: 76px;
	}
	.axis .track {
		height: 16px;
	}
	.tick {
		position: absolute;
		top: 0;
		transform: translateX(-50%);
		font-family: var(--mono);
		font-size: 0.7rem;
		color: var(--ink-soft);
	}
	.grid {
		position: absolute;
		top: -5px;
		bottom: -5px;
		width: 1px;
		background: var(--rule);
		opacity: 0.6;
	}
	.bar {
		position: absolute;
		top: 6px;
		height: 6px;
		border-radius: 3px;
		background: var(--accent);
		opacity: 0.3;
	}
	.dot {
		position: absolute;
		top: 9px;
		width: 5px;
		height: 5px;
		margin: -2.5px 0 0 -2.5px;
		border-radius: 50%;
		background: var(--ink);
	}
	.years {
		position: absolute;
		top: 0;
		padding-left: 8px;
		font-family: var(--mono);
		font-size: 0.7rem;
		line-height: 18px;
		color: var(--ink-soft);
		white-space: nowrap;
	}

	/* ---- the indexes ---- */
	.doors {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 200px), 1fr));
		gap: 10px;
	}
	.doors a {
		display: grid;
		grid-template-columns: auto 1fr;
		grid-template-rows: auto 1fr;
		column-gap: 12px;
		height: 100%;
		box-sizing: border-box;
		padding: 14px 16px;
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
		color: var(--ink);
		text-decoration: none;
		transition: border-color 120ms ease;
	}
	.doors a:hover {
		border-color: var(--ink-soft);
	}
	.doors a:hover .label {
		color: var(--accent);
	}
	.doors a:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
	}
	.count {
		grid-row: 1 / 3;
		font-family: var(--serif);
		font-size: 1.9rem;
		font-weight: 600;
		line-height: 1;
		font-variant-numeric: tabular-nums;
		min-width: 2.2ch;
	}
	.label {
		font-weight: 600;
	}
	.desc {
		font-size: 0.84rem;
		color: var(--ink-soft);
		line-height: 1.4;
	}

	@media (max-width: 960px) {
		.hero {
			grid-template-columns: minmax(0, 1fr);
			gap: 28px;
		}
		.how ol {
			grid-template-columns: minmax(0, 1fr);
		}
	}
	@media (max-width: 640px) {
		.home {
			gap: 40px;
		}
		/* Fifteen cards stacked would be most of the page on a phone; a row the
		   thumb swipes through keeps the threads and the indexes within reach. */
		.turning {
			grid-template-columns: none;
			grid-auto-flow: column;
			grid-auto-columns: 78%;
			overflow-x: auto;
			scroll-snap-type: x mandatory;
			overscroll-behavior-x: contain;
			margin-inline: -20px;
			padding: 2px 20px 8px;
			scroll-padding-inline: 20px;
			scrollbar-width: thin;
		}
		.turning li {
			scroll-snap-align: start;
		}
		.arc {
			grid-template-columns: minmax(0, 1fr);
			gap: 2px;
		}
		.axis > span:first-child {
			display: none;
		}
		.arcs .track {
			margin-right: 64px;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.turning a,
		.cta {
			transition: none;
		}
		.turning a:hover {
			transform: none;
		}
	}
</style>
