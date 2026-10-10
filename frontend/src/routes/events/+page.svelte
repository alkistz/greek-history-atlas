<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import FilterBar from '$lib/FilterBar.svelte';
	import IndexPage from '$lib/IndexPage.svelte';
	import { both, t } from '$lib/lang.svelte';
	import { ui } from '$lib/ui';
	import { regimeLabel, regimeOn } from '$lib/regimes';
	import { REVIEW_FACETS, reviewLabel, reviewTags, tally } from '$lib/review';
	import ReviewBadge from '$lib/ReviewBadge.svelte';
	import Significance, { sigLabel } from '$lib/Significance.svelte';
	import { prettyPeriod, year } from '$lib/time';
	import type { LangText } from '$lib/types';
	import { list, matches, params, replaceParams } from '$lib/urlstate';
	import { atlasHref } from '$lib/viewstate';

	let { data } = $props();

	let query = $state(untrack(() => page.url.searchParams.get('q') ?? ''));
	let regions = $state<string[]>(untrack(() => list(page.url, 'regions')));
	let regimes = $state<string[]>(untrack(() => list(page.url, 'regimes')));
	let threads = $state<string[]>(untrack(() => list(page.url, 'threads')));
	let sig = $state<string[]>(untrack(() => list(page.url, 'sig')));
	let review = $state<string[]>(untrack(() => list(page.url, 'review')));

	$effect(() => replaceParams(params({ q: query, regions, regimes, threads, sig, review })));

	const regionOf = $derived(
		new Map(data.meta.regions.flatMap((r) => r.atoms.map((a) => [a, r.id] as const)))
	);
	// The lookup maps hold the `LangText` rather than one side of it, so the same
	// map can serve the display, which follows the switch, and the search, which
	// deliberately does not.
	const regionName = $derived(new Map(data.meta.regions.map((r) => [r.id, r.name])));
	const regionItems = $derived(data.meta.regions.map((r) => ({ id: r.id, label: t(r.name) })));

	// Nothing is stored per event: an event's regime is a lookup from its start date,
	// the way its region is a lookup from its atom. The chips are already in order,
	// so the row doubles as a chronological spine for the century the map cannot show.
	const regimeItems = $derived(
		data.meta.regimes.map((r) => ({ id: r.id, label: regimeLabel(r) }))
	);

	// Membership is authored on the thread, so this is the inverse, built once.
	const arcsOf = $derived.by(() => {
		const out = new Map<string, { id: string; name: LangText }[]>();
		for (const thread of data.threads) {
			for (const id of thread.events) {
				const list = out.get(id) ?? [];
				list.push({ id: thread.id, name: thread.name });
				out.set(id, list);
			}
		}
		return out;
	});
	const threadItems = $derived(
		data.threads.map((thread) => ({ id: thread.id, label: `${t(thread.name)} (${thread.count})` }))
	);

	const placeName = $derived(new Map(data.places.map((p) => [p.id, p.names[0].name])));
	const instrumentName = $derived(new Map(data.meta.instruments.map((i) => [i.id, i.name])));

	// Both vocabularies come from the corpus, so no chip is ever offered that can
	// only return nothing — and a `manual` chip appears the day someone makes a
	// manual pass, without this file changing.
	const sigItems = $derived(
		[...new Set(data.events.map((e) => e.significance))]
			.sort((a, b) => b - a)
			.map((n) => ({ id: String(n), label: sigLabel(n) }))
	);
	const reviewCounts = $derived(tally(data.events, (e) => e.review));
	const reviewItems = $derived(
		REVIEW_FACETS.filter((f) => reviewCounts.has(f)).map((f) => ({
			id: f,
			label: ui('facet.count', { label: reviewLabel(f), n: reviewCounts.get(f) ?? 0 })
		}))
	);

	const facetCount = $derived(
		regions.length + regimes.length + threads.length + sig.length + review.length
	);
	const active = $derived(query.trim().length > 0 || facetCount > 0);

	const shown = $derived(
		data.events.filter((e) => {
			const region = e.atom ? regionOf.get(e.atom) : undefined;
			if (regions.length && (!region || !regions.includes(region))) return false;
			const regime = regimeOn(data.meta.regimes, e.period[0]);
			if (regimes.length && (!regime || !regimes.includes(regime.id))) return false;
			const arcs = arcsOf.get(e.id) ?? [];
			if (threads.length && !arcs.some((a) => threads.includes(a.id))) return false;
			if (sig.length && !sig.includes(String(e.significance))) return false;
			if (review.length && !reviewTags(e.review).some((tag) => review.includes(tag))) return false;
			return matches(
				query,
				// Both languages throughout, because half the corpus is written in the
				// other one and the switch must not narrow what can be found.
				...both(e.title),
				...both(e.summary),
				e.period[0],
				...both(e.place ? placeName.get(e.place) : null),
				...both(e.instrument ? instrumentName.get(e.instrument) : null),
				...both(region ? regionName.get(region) : null),
				...both(regime?.name),
				arcs.flatMap((a) => both(a.name)).join(' ')
			);
		})
	);

	const decades = $derived.by(() => {
		const out: { decade: string; events: typeof shown }[] = [];
		for (const e of shown) {
			const decade = `${e.period[0].slice(0, 3)}0s`;
			const last = out.at(-1);
			if (last?.decade === decade) last.events.push(e);
			else out.push({ decade, events: [e] });
		}
		return out;
	});

	/**
	 * Two columns read down, then across, like an index. Each card is laid in
	 * its own column rather than a grid row, because a title that wraps makes
	 * its card taller and a grid row then leaves a hole under its neighbour.
	 * The cut balances the columns by lines, not by count: a title past about
	 * forty-five characters pushes its tags onto a second line at the widths
	 * the page takes, so its card is twice the height of a one-line card.
	 */
	function columns<T extends { title: LangText }>(events: T[]): [T[], T[]] {
		const weight = (e: T) => (t(e.title).length > 45 ? 2 : 1);
		const total = events.reduce((n, e) => n + weight(e), 0);
		let acc = 0;
		let cut = events.length;
		for (let i = 0; i < events.length; i++) {
			acc += weight(events[i]);
			if (acc >= total / 2) {
				cut = i + 1;
				break;
			}
		}
		return [events.slice(0, cut), events.slice(cut)];
	}

	const toggle = (current: string[], id: string) =>
		current.includes(id) ? current.filter((x) => x !== id) : [...current, id];

	function clear() {
		query = '';
		regions = [];
		regimes = [];
		threads = [];
		sig = [];
		review = [];
	}
</script>

<svelte:head>
	<title>{ui('page.title', { page: ui('page.events'), site: ui('site.name') })}</title>
	<meta name="description" content={ui('events.description')} />
</svelte:head>

<IndexPage title={ui('page.events')} lead={ui('events.lead')}>
	{#snippet filters()}
		<FilterBar
			bind:query
			placeholder={ui('events.placeholder')}
			shown={shown.length}
			total={data.events.length}
			noun="events"
			{active}
			{facetCount}
			collapsible
			onclear={clear}
		>
			{#snippet facets()}
				<ChipGroup
					label={ui('facet.region')}
					items={regionItems}
					selected={regions}
					ontoggle={(id) => (regions = toggle(regions, id))}
					onclear={() => (regions = [])}
				/>
				<ChipGroup
					label={ui('facet.thread')}
					items={threadItems}
					selected={threads}
					ontoggle={(id) => (threads = toggle(threads, id))}
					onclear={() => (threads = [])}
				/>
				<ChipGroup
					label={ui('facet.regime')}
					items={regimeItems}
					selected={regimes}
					ontoggle={(id) => (regimes = toggle(regimes, id))}
					onclear={() => (regimes = [])}
				/>
				<ChipGroup
					label={ui('facet.significance')}
					items={sigItems}
					selected={sig}
					ontoggle={(id) => (sig = toggle(sig, id))}
					onclear={() => (sig = [])}
				/>
				<ChipGroup
					label={ui('facet.review')}
					items={reviewItems}
					selected={review}
					ontoggle={(id) => (review = toggle(review, id))}
					onclear={() => (review = [])}
				/>
			{/snippet}
		</FilterBar>
	{/snippet}

	{#if decades.length > 1}
		<!-- A rail of decades: two centuries of rows is a long way to scroll for 1974. -->
		<nav class="decades" aria-label={ui('index.decades')}>
			{#each decades as g (g.decade)}
				<a href="#d-{g.decade}">{g.decade}</a>
			{/each}
		</nav>
	{/if}

	{#each decades as g (g.decade)}
		<section id="d-{g.decade}">
			<h2>{g.decade}</h2>
			<div class="cards">
				{#each columns(g.events) as col, i (i)}
					<div class="col">
						{#each col as e (e.id)}
							{@const regime = regimeOn(data.meta.regimes, e.period[0])}
							{@const arcs = arcsOf.get(e.id) ?? []}
							{@const region = e.atom ? regionOf.get(e.atom) : undefined}
							<!-- Closed, a card is one line: the year, the name, where, how much it
							     mattered. Open, it says what happened and where to go next. -->
							<details class="card">
								<summary>
									<span class="when">{year(e.period[0])}</span>
									<span class="head">
										<span class="title">{t(e.title)}</span>
										<span class="tags">
											{#if region}<span class="region">{t(regionName.get(region))}</span>{/if}
											<Significance significance={e.significance} compact />
										</span>
									</span>
								</summary>
								<div class="body">
									<p class="summary">{t(e.summary)}</p>
									<p class="marks">
										<Significance significance={e.significance} />
										<ReviewBadge review={e.review} />
										{#if regime}<span class="regime">{t(regime.name)}</span>{/if}
									</p>
									<p class="meta">
										<span>{prettyPeriod(e.period, e.precision)}</span>
										{#if e.place && placeName.get(e.place)}
											<span class="where">{t(placeName.get(e.place))}</span>
										{/if}
										{#if e.instrument && instrumentName.get(e.instrument)}
											<a href="/instruments/{e.instrument}">{t(instrumentName.get(e.instrument))}</a>
										{/if}
									</p>
									{#if arcs.length}
										<p class="arcs">
											{#each arcs as a (a.id)}<a href="/threads/{a.id}">{t(a.name)}</a>{/each}
										</p>
									{/if}
									<p class="links">
										<a class="go" href="/events/{e.id}">{ui('index.readmore')}</a>
										<a href={atlasHref({ on: e.period[0], frame: e.frame, event: e.id })}>
											{ui('events.openatlas')}
										</a>
									</p>
								</div>
							</details>
						{/each}
					</div>
				{/each}
			</div>
		</section>
	{:else}
		<p class="empty">{ui('events.empty')}</p>
	{/each}
</IndexPage>

<style>
	.decades {
		position: sticky;
		top: var(--header-h, 0px);
		z-index: 2;
		display: flex;
		flex-wrap: wrap;
		gap: 2px 10px;
		padding: 8px 0;
		margin-bottom: 4px;
		background: var(--ground);
		border-bottom: 1px solid var(--rule);
		font-family: var(--mono);
		font-size: 0.76rem;
		letter-spacing: 0.06em;
	}
	.decades a {
		color: var(--ink-soft);
		text-decoration: none;
		padding: 1px 4px;
		border-radius: var(--radius);
	}
	.decades a:hover {
		color: var(--accent);
		background: var(--accent-soft);
	}
	section {
		scroll-margin-top: calc(var(--header-h, 0px) + 44px);
		container-type: inline-size;
	}
	h2 {
		font-family: var(--mono);
		font-size: 0.78rem;
		letter-spacing: 0.1em;
		color: var(--ink-soft);
		margin: 22px 0 8px;
	}
	.cards {
		display: grid;
		grid-template-columns: 1fr;
		gap: 8px;
		align-items: start;
	}
	/* The same width at which two 380px cards used to fit side by side. Below
	   it the two columns stack, first then second, and the order still reads. */
	@container (min-width: 768px) {
		.cards {
			grid-template-columns: 1fr 1fr;
		}
	}
	.col {
		display: flex;
		flex-direction: column;
		gap: 8px;
		min-width: 0;
	}
	.card {
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
		transition:
			border-color 120ms ease,
			box-shadow 120ms ease;
	}
	.card:hover,
	.card[open] {
		border-color: var(--ink-soft);
	}
	.card[open] {
		box-shadow: var(--elev-1);
	}
	summary {
		display: flex;
		gap: 10px;
		align-items: baseline;
		padding: 8px 12px;
		cursor: pointer;
		list-style: none;
	}
	summary::-webkit-details-marker {
		display: none;
	}
	summary:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: -2px;
		border-radius: var(--radius-lg);
	}
	.when {
		flex: none;
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.82rem;
		color: var(--ink-soft);
	}
	.head {
		min-width: 0;
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 2px 10px;
	}
	.title {
		font-family: var(--serif);
		font-size: 1.02rem;
		font-weight: 600;
		color: var(--ink);
	}
	.card:hover .title {
		color: var(--accent);
	}
	.tags {
		display: inline-flex;
		align-items: center;
		gap: 10px;
	}
	.region,
	.regime {
		color: var(--ink-soft);
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		white-space: nowrap;
	}
	.body {
		padding: 0 12px 10px 12px;
	}
	.body p {
		margin: 4px 0 0;
		color: var(--ink-soft);
		font-size: 0.9rem;
	}
	.summary {
		color: var(--ink);
	}
	.marks {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
	}
	.meta,
	.links {
		display: flex;
		gap: 14px;
		flex-wrap: wrap;
		font-size: 0.82rem;
	}
	.links {
		margin-top: 8px;
	}
	.go {
		font-weight: 600;
	}
	.where::before {
		content: '· ';
	}
	.arcs {
		display: flex;
		gap: 10px;
		flex-wrap: wrap;
		font-size: 0.78rem;
	}
	.arcs a {
		color: var(--ink-soft);
		text-decoration: none;
		border-bottom: 1px dotted var(--rule);
	}
	.arcs a:hover {
		color: var(--accent);
	}
	.empty {
		color: var(--ink-soft);
		max-width: 60ch;
	}
	@media (prefers-reduced-motion: reduce) {
		.card {
			transition: none;
		}
	}
</style>
