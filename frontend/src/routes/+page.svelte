<!--
	The front page: what the atlas is, how to read its map, and the ways in.

	The atlas itself is an instrument with a lot on it at once. This page exists
	so that a first visit starts with one sentence and a moving picture rather
	than with a timeline, a ledger and a legend; everything below the hero is a
	door into one of the other pages, chosen from the corpus rather than written
	here, so it grows with the content.

	The page is the sea. The hero's map runs edge to edge under the words, and
	everything below keeps the usual measure through the layout's --inset.
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

	const counts: Record<string, number> = $derived({
		...data.counts,
		instruments: data.meta.instruments.length
	});
	type Door = 'events' | 'threads' | 'figures' | 'network' | 'instruments' | 'places' | 'sources';
	// The network is a view of the figures rather than an index, so it has no count.
	const doors: { href: string; key: Door }[] = [
		{ href: '/events', key: 'events' },
		{ href: '/threads', key: 'threads' },
		{ href: '/figures', key: 'figures' },
		{ href: '/network', key: 'network' },
		{ href: '/instruments', key: 'instruments' },
		{ href: '/places', key: 'places' },
		{ href: '/sources', key: 'sources' }
	];
	const pageKey = (k: string) => `page.${k}` as UiKey;
	const descKey = (k: string) => `${k}.description` as UiKey;

	// Wide, the words sit on the left over the faded edge of the map and the
	// camera frames Greece in the space to their right; these numbers mirror the
	// .pitch rules below. Narrow, the map is a band above the words.
	const WIDE = 900;
	const MEASURE = 520;
	let heroW = $state(0);
	const wide = $derived(heroW >= WIDE);
	const mapInsets = $derived.by(() => {
		if (!wide) return { top: 8, bottom: 48 };
		const gutter = Math.max(20, (heroW - 1280) / 2);
		return { left: gutter + Math.min(MEASURE, heroW * 0.46) + 24, top: 24, bottom: 88 };
	});
</script>

<svelte:head>
	<title>{ui('site.name')}</title>
</svelte:head>

<main class="home">
	<section class="hero" bind:clientWidth={heroW}>
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
		<div class="backdrop">
			<HeroMap
				atoms={data.atoms.features}
				land={data.land}
				meta={data.meta}
				control={data.control}
				insets={mapInsets}
			/>
		</div>
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
		<!-- A gazetteer: the year in the margin, the entry beside it. -->
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
		<!-- A table of contents, with dotted leaders to the count. -->
		<ul class="doors">
			{#each doors as d (d.key)}
				<li>
					<a href={d.href}>
						<span class="label">{ui(pageKey(d.key))}</span>
						{#if counts[d.key] !== undefined}<span class="count">{counts[d.key]}</span>{/if}
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
	.home > section:not(.hero) {
		margin-inline: var(--inset, 20px);
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
	a:focus-visible {
		outline: 2px solid var(--ink);
		outline-offset: 2px;
	}

	/* ---- the hero: words on the left, the map under everything ---- */
	.hero {
		position: relative;
		isolation: isolate;
		display: flex;
		align-items: center;
		min-height: 640px;
		margin-top: -16px;
	}
	.backdrop {
		position: absolute;
		inset: 0;
	}
	/* The map fades into the page under the words and at its top and foot, so
	   it has no edge anywhere: the page is the same sea. */
	.hero::before {
		content: '';
		position: absolute;
		inset: 0;
		z-index: 1;
		pointer-events: none;
		background:
			linear-gradient(90deg, var(--ground) calc(var(--inset, 20px) + 280px), transparent calc(var(--inset, 20px) + 600px)),
			linear-gradient(0deg, var(--ground) 0%, transparent 16%),
			linear-gradient(180deg, var(--ground) 0%, transparent 10%);
	}
	.pitch {
		position: relative;
		z-index: 2;
		box-sizing: content-box;
		max-width: min(520px, 46%);
		padding-block: 120px;
		padding-left: var(--inset, 20px);
	}
	.eyebrow {
		margin: 0 0 12px;
		font-family: var(--serif);
		font-variant-caps: all-small-caps;
		letter-spacing: 0.14em;
		font-size: 1.02rem;
		color: var(--ink-soft);
	}
	h1 {
		font-size: clamp(2.4rem, 1.4rem + 3vw, 4rem);
		font-weight: 500;
		line-height: 1.06;
		letter-spacing: -0.015em;
		margin: 0 0 20px;
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
		border: 1px solid var(--ink);
		color: var(--ink);
		text-decoration: none;
		font-weight: 600;
		transition: background 120ms ease;
	}
	.cta:hover {
		background: var(--accent-soft);
	}
	.cta.primary {
		background: var(--ink);
		color: var(--ground);
	}
	.cta.primary:hover {
		background: color-mix(in srgb, var(--ink) 86%, var(--ground));
	}

	/* ---- how to read the map: three columns between rules ---- */
	.how ol {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
	}
	.how ol > li {
		display: flex;
		gap: 14px;
		padding: 2px 24px;
		border-left: 1px solid var(--rule);
	}
	.how ol > li:first-child {
		border-left: 0;
		padding-left: 0;
	}
	.step {
		flex: none;
		font-family: var(--serif);
		font-size: 1.7rem;
		line-height: 1;
		color: var(--ink);
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

	/* ---- section heads: small caps over an ink rule ---- */
	.section-head {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 4px 18px;
		padding-bottom: 8px;
		border-bottom: 1px solid var(--ink);
	}
	h2 {
		font-size: 1.6rem;
		font-weight: 500;
		font-variant-caps: small-caps;
		letter-spacing: 0.04em;
		margin: 0;
	}
	.section-head p {
		margin: 0;
		color: var(--ink-soft);
		font-size: 0.92rem;
		max-width: 66ch;
	}

	/* ---- turning points: a gazetteer ---- */
	.turning {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 330px), 1fr));
		gap: 0 36px;
	}
	.turning a {
		display: grid;
		grid-template-columns: 3.4rem minmax(0, 1fr);
		column-gap: 10px;
		align-content: start;
		height: 100%;
		box-sizing: border-box;
		padding: 12px 0;
		border-bottom: 1px solid var(--rule);
		color: var(--ink);
		text-decoration: none;
	}
	.when {
		grid-row: 1 / 3;
		font-family: var(--serif);
		font-size: 1.2rem;
		line-height: 1.25;
		font-variant-numeric: tabular-nums;
	}
	.what {
		font-family: var(--serif);
		font-size: 1.04rem;
		font-weight: 600;
		line-height: 1.3;
	}
	.turning a:hover .what {
		text-decoration: underline;
		text-underline-offset: 3px;
	}
	.why {
		margin-top: 2px;
		font-size: 0.86rem;
		color: var(--ink-soft);
		display: -webkit-box;
		-webkit-line-clamp: 2;
		line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	/* ---- threads on one ruler ---- */
	.arcs {
		padding-top: 6px;
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
		color: var(--ink);
		text-decoration: none;
	}
	a.arc:hover {
		background: var(--accent-soft);
	}
	a.arc:focus-visible {
		outline-offset: -2px;
	}
	.name {
		font-family: var(--serif);
		font-size: 1rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.track {
		position: relative;
		display: block;
		height: 18px;
		/* The years sit at the end of the bar; the last arcs run to the end of the range,
		   so the track keeps a margin for the label to land in. */
		margin-right: 76px;
	}
	.axis .track {
		height: 16px;
	}
	.tick {
		position: absolute;
		top: 0;
		transform: translateX(-50%);
		font-family: var(--figures);
		font-size: 0.82rem;
		color: var(--ink-soft);
	}
	.grid {
		position: absolute;
		top: -5px;
		bottom: -5px;
		width: 1px;
		background: var(--rule);
	}
	.bar {
		position: absolute;
		top: 7px;
		height: 4px;
		background: color-mix(in oklab, var(--ink) 22%, var(--ground));
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
		font-family: var(--figures);
		font-size: 0.82rem;
		line-height: 18px;
		color: var(--ink-soft);
		white-space: nowrap;
	}

	/* ---- the indexes: a table of contents ---- */
	.doors {
		list-style: none;
		margin: 0;
		padding: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 340px), 1fr));
		gap: 0 44px;
	}
	.doors a {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0 8px;
		padding: 11px 0;
		border-bottom: 1px solid var(--rule);
		color: var(--ink);
		text-decoration: none;
	}
	.label {
		flex: 1;
		display: flex;
		align-items: baseline;
		gap: 8px;
		font-family: var(--serif);
		font-size: 1.18rem;
		font-weight: 500;
	}
	.label::after {
		content: '';
		flex: 1;
		border-bottom: 1px dotted var(--ink-soft);
	}
	.doors a:hover .label {
		text-decoration: underline;
		text-underline-offset: 3px;
	}
	.count {
		font-family: var(--serif);
		font-size: 1.18rem;
		font-weight: 500;
		font-variant-numeric: tabular-nums;
	}
	.desc {
		flex-basis: 100%;
		font-size: 0.84rem;
		color: var(--ink-soft);
		line-height: 1.4;
	}

	/* Narrow, the map is a band across the top and the words follow it on the
	   same sea; the hero's fades turn to run down instead of across. */
	@media (max-width: 899px) {
		.hero {
			display: flex;
			flex-direction: column;
			align-items: stretch;
			min-height: 0;
			margin-top: -8px;
		}
		.backdrop {
			position: relative;
			order: -1;
			height: min(400px, 56vh);
		}
		.hero::before {
			inset: 0 0 auto;
			height: min(400px, 56vh);
			background:
				linear-gradient(0deg, var(--ground) 0%, transparent 30%),
				linear-gradient(180deg, var(--ground) 0%, transparent 10%);
		}
		.pitch {
			max-width: none;
			margin-top: -36px;
			padding: 0 var(--inset, 20px) 8px;
		}
	}
	@media (max-width: 960px) {
		.how ol {
			grid-template-columns: minmax(0, 1fr);
		}
		.how ol > li,
		.how ol > li:first-child {
			border-left: 0;
			border-top: 1px solid var(--rule);
			padding: 14px 0;
		}
		.how ol > li:first-child {
			border-top: 0;
			padding-top: 0;
		}
	}
	@media (max-width: 640px) {
		.home {
			gap: 40px;
		}
		/* On a phone the gazetteer is a list of years and names; the entry is
		   one tap away. */
		.why {
			display: none;
		}
		.arc {
			grid-template-columns: minmax(0, 1fr);
			gap: 2px;
		}
		.axis > span:first-child {
			display: none;
		}
		.track {
			margin-right: 64px;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.cta {
			transition: none;
		}
	}
</style>
