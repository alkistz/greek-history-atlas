<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import FilterBar from '$lib/FilterBar.svelte';
	import { REVIEW_FACETS, REVIEW_LABELS, reviewTags, tally } from '$lib/review';
	import ReviewBadge from '$lib/ReviewBadge.svelte';
	import { prettyDate, year } from '$lib/time';
	import { list, matches, params, replaceParams } from '$lib/urlstate';
	import { atlasHref } from '$lib/viewstate';

	let { data } = $props();

	let query = $state(untrack(() => page.url.searchParams.get('q') ?? ''));
	let kinds = $state<string[]>(untrack(() => list(page.url, 'kinds')));
	let parties = $state<string[]>(untrack(() => list(page.url, 'parties')));
	let review = $state<string[]>(untrack(() => list(page.url, 'review')));
	let text = $state<string[]>(untrack(() => list(page.url, 'text')));

	$effect(() => replaceParams(params({ q: query, kinds, parties, review, text })));

	const polity = $derived(new Map(data.meta.polities.map((p) => [p.id, p])));
	const polityName = $derived(
		new Map(data.meta.polities.map((p) => [p.id, p.name.en] as const))
	);
	const sorted = $derived([...data.instruments].sort((a, b) => a.signed.localeCompare(b.signed)));

	// Both facet vocabularies come from the instruments themselves, so no chip can
	// ever be offered that returns nothing.
	const kindItems = $derived(
		[...new Set(sorted.map((i) => i.kind))]
			.sort()
			.map((k) => ({ id: k, label: k[0].toUpperCase() + k.slice(1) }))
	);
	const partyItems = $derived(
		[...new Set(sorted.flatMap((i) => i.parties))]
			.map((id) => ({ id, label: polity.get(id)?.short?.en ?? polityName.get(id) ?? id }))
			.sort((a, b) => a.label.localeCompare(b.label))
	);

	const reviewCounts = $derived(tally(sorted, (i) => i.review));
	const reviewItems = $derived(
		REVIEW_FACETS.filter((f) => reviewCounts.has(f)).map((f) => ({
			id: f,
			label: `${REVIEW_LABELS[f]} (${reviewCounts.get(f)})`
		}))
	);
	// A treaty's own text is the most authoritative thing the atlas can point at,
	// and 23 of 32 have none yet, so which is which is worth filtering on.
	const linked = $derived(sorted.filter((i) => i.text_url).length);
	const textItems = $derived([
		{ id: 'yes', label: `Text linked (${linked})` },
		{ id: 'no', label: `No text yet (${sorted.length - linked})` }
	]);

	const facetCount = $derived(kinds.length + parties.length + review.length + text.length);
	const active = $derived(query.trim().length > 0 || facetCount > 0);
	const shown = $derived(
		sorted.filter((i) => {
			if (kinds.length && !kinds.includes(i.kind)) return false;
			if (parties.length && !i.parties.some((p) => parties.includes(p))) return false;
			if (review.length && !reviewTags(i.review).some((t) => review.includes(t))) return false;
			if (text.length && !text.includes(i.text_url ? 'yes' : 'no')) return false;
			return matches(
				query,
				i.name.en,
				i.name.el,
				i.summary?.en,
				i.summary?.el,
				i.kind,
				// The signing date, so "1913" finds the five treaties of that year.
				i.signed,
				i.parties.map((p) => polityName.get(p) ?? p).join(' ')
			);
		})
	);

	const toggle = (current: string[], id: string) =>
		current.includes(id) ? current.filter((x) => x !== id) : [...current, id];

	function clear() {
		query = '';
		kinds = [];
		parties = [];
		review = [];
		text = [];
	}
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

<FilterBar
	bind:query
	placeholder="Search treaties, parties, years…"
	shown={shown.length}
	total={sorted.length}
	noun="instruments"
	{active}
	{facetCount}
	collapsible
	onclear={clear}
>
	{#snippet facets()}
		<ChipGroup
			label="Kind"
			items={kindItems}
			selected={kinds}
			ontoggle={(id) => (kinds = toggle(kinds, id))}
			onclear={() => (kinds = [])}
		/>
		<ChipGroup
			label="Party"
			items={partyItems}
			selected={parties}
			ontoggle={(id) => (parties = toggle(parties, id))}
			onclear={() => (parties = [])}
		/>
		<ChipGroup
			label="Own text"
			items={textItems}
			selected={text}
			ontoggle={(id) => (text = toggle(text, id))}
			onclear={() => (text = [])}
		/>
		<ChipGroup
			label="Review"
			items={reviewItems}
			selected={review}
			ontoggle={(id) => (review = toggle(review, id))}
			onclear={() => (review = [])}
		/>
	{/snippet}
</FilterBar>

<ol class="instruments">
	{#each shown as i (i.id)}
		<li>
			<span class="when">{year(i.signed)}</span>
			<div>
				<a class="title" href="/instruments/{i.id}">{i.name.en}</a>
				<span class="kind">{i.kind}</span>
				<ReviewBadge review={i.review} />
				<p class="parties">{i.parties.map((p) => polityName.get(p) ?? p).join(' · ')}</p>
				{#if i.summary}<p>{i.summary.en}</p>{/if}
				<p class="meta">
					<span>Signed {prettyDate(i.signed)}</span>
					<a href={atlasHref({ on: i.signed })}>Open on the atlas</a>
					{#if i.text_url}
						<a href={i.text_url} rel="noreferrer">Read the text</a>
					{/if}
				</p>
			</div>
		</li>
	{:else}
		<li class="empty">No instrument matches that.</li>
	{/each}
</ol>

<style>
	h1 {
		font-size: 1.9rem;
		margin: 0 0 4px;
	}
	.lead {
		color: var(--ink-soft);
		margin: 0 0 18px;
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
		margin-right: 6px;
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
	.empty {
		display: block;
		color: var(--ink-soft);
		padding: 14px 0;
	}
</style>
