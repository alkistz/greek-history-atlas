<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import FilterBar from '$lib/FilterBar.svelte';
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

<h1>{ui('page.events')}</h1>
<p class="lead">{ui('events.lead')}</p>

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

{#each decades as g (g.decade)}
	<section>
		<h2>{g.decade}</h2>
		<ol class="events">
			{#each g.events as e (e.id)}
				{@const regime = regimeOn(data.meta.regimes, e.period[0])}
				{@const arcs = arcsOf.get(e.id) ?? []}
				<li>
					<span class="when">{year(e.period[0])}</span>
					<div>
						<a class="title" href="/events/{e.id}">{t(e.title)}</a>
						{#if e.atom && regionOf.get(e.atom)}
							<span class="region">{t(regionName.get(regionOf.get(e.atom)!))}</span>
						{/if}
						{#if regime}<span class="regime">{t(regime.name)}</span>{/if}
						<p class="marks">
							<Significance significance={e.significance} />
							<ReviewBadge review={e.review} />
						</p>
						<p>{t(e.summary)}</p>
						<p class="meta">
							<span>{prettyPeriod(e.period, e.precision)}</span>
							{#if e.place && placeName.get(e.place)}
								<span class="where">{t(placeName.get(e.place))}</span>
							{/if}
							{#if e.instrument && instrumentName.get(e.instrument)}
								<a href="/instruments/{e.instrument}">{t(instrumentName.get(e.instrument))}</a>
							{/if}
							<a href={atlasHref({ on: e.period[0], frame: e.frame, event: e.id })}>
								{ui('events.openatlas')}
							</a>
						</p>
						{#if arcs.length}
							<p class="arcs">
								{#each arcs as a (a.id)}<a href="/threads/{a.id}">{t(a.name)}</a>{/each}
							</p>
						{/if}
					</div>
				</li>
			{/each}
		</ol>
	</section>
{:else}
	<p class="empty">{ui('events.empty')}</p>
{/each}

<style>
	h1 {
		font-size: 1.9rem;
		margin: 0 0 4px;
	}
	.lead {
		color: var(--ink-soft);
		margin: 0 0 18px;
		max-width: 66ch;
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
	.region,
	.regime {
		margin-left: 8px;
		color: var(--ink-soft);
		font-size: 0.74rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		/* As a unit, so "Provisional administrations" does not break across lines
		   and read as two separate labels. */
		white-space: nowrap;
	}
	/* The regime is the softer of the two: it is context for the row, not its
	   subject, and the mark keeps the two from running together as one phrase. */
	.regime {
		opacity: 0.72;
	}
	.regime::before {
		content: '· ';
	}
	.marks {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
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
</style>
