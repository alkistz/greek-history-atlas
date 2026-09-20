<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import FilterBar from '$lib/FilterBar.svelte';
	import { both, collator, t } from '$lib/lang.svelte';
	import { term, Term, ui } from '$lib/ui';
	import { REVIEW_FACETS, reviewLabel, reviewTags, tally } from '$lib/review';
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
	const polityName = $derived(new Map(data.meta.polities.map((p) => [p.id, p.name] as const)));
	const sorted = $derived([...data.instruments].sort((a, b) => a.signed.localeCompare(b.signed)));

	// Both facet vocabularies come from the instruments themselves, so no chip can
	// ever be offered that returns nothing.
	const kindItems = $derived(
		[...new Set(sorted.map((i) => i.kind))]
			.sort()
			.map((k) => ({ id: k, label: Term('kind.instrument', k) }))
	);
	const partyItems = $derived(
		[...new Set(sorted.flatMap((i) => i.parties))]
			.map((id) => ({ id, label: t(polity.get(id)?.short) || t(polityName.get(id)) || id }))
			.sort((a, b) => collator().compare(a.label, b.label))
	);

	const reviewCounts = $derived(tally(sorted, (i) => i.review));
	const reviewItems = $derived(
		REVIEW_FACETS.filter((f) => reviewCounts.has(f)).map((f) => ({
			id: f,
			label: ui('facet.count', { label: reviewLabel(f), n: reviewCounts.get(f) ?? 0 })
		}))
	);
	// A treaty's own text is the most authoritative thing the atlas can point at,
	// and 23 of 32 have none yet, so which is which is worth filtering on.
	const linked = $derived(sorted.filter((i) => i.text_url).length);
	const textItems = $derived([
		{ id: 'yes', label: ui('instruments.textyes', { n: linked }) },
		{ id: 'no', label: ui('instruments.textno', { n: sorted.length - linked }) }
	]);

	const facetCount = $derived(kinds.length + parties.length + review.length + text.length);
	const active = $derived(query.trim().length > 0 || facetCount > 0);
	const shown = $derived(
		sorted.filter((i) => {
			if (kinds.length && !kinds.includes(i.kind)) return false;
			if (parties.length && !i.parties.some((p) => parties.includes(p))) return false;
			if (review.length && !reviewTags(i.review).some((tag) => review.includes(tag))) return false;
			if (text.length && !text.includes(i.text_url ? 'yes' : 'no')) return false;
			return matches(
				query,
				...both(i.name),
				...both(i.summary),
				i.kind,
				// The signing date, so "1913" finds the five treaties of that year.
				i.signed,
				i.parties.flatMap((p) => both(polityName.get(p))).join(' ')
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
	<title>{ui('page.title', { page: ui('page.instruments'), site: ui('site.name') })}</title>
	<meta name="description" content={ui('instruments.description')} />
</svelte:head>

<h1>{ui('page.instruments')}</h1>
<p class="lead">{ui('instruments.lead')}</p>

<FilterBar
	bind:query
	placeholder={ui('instruments.placeholder')}
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
			label={ui('facet.kind')}
			items={kindItems}
			selected={kinds}
			ontoggle={(id) => (kinds = toggle(kinds, id))}
			onclear={() => (kinds = [])}
		/>
		<ChipGroup
			label={ui('facet.party')}
			items={partyItems}
			selected={parties}
			ontoggle={(id) => (parties = toggle(parties, id))}
			onclear={() => (parties = [])}
		/>
		<ChipGroup
			label={ui('facet.text')}
			items={textItems}
			selected={text}
			ontoggle={(id) => (text = toggle(text, id))}
			onclear={() => (text = [])}
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

<ol class="instruments">
	{#each shown as i (i.id)}
		<li>
			<span class="when">{year(i.signed)}</span>
			<div>
				<a class="title" href="/instruments/{i.id}">{t(i.name)}</a>
				<span class="kind">{term('kind.instrument', i.kind)}</span>
				<ReviewBadge review={i.review} />
				<p class="parties">{i.parties.map((p) => t(polityName.get(p)) || p).join(' · ')}</p>
				{#if i.summary}<p>{t(i.summary)}</p>{/if}
				<p class="meta">
					<span>{ui('instruments.signed', { date: prettyDate(i.signed) })}</span>
					<a href={atlasHref({ on: i.signed })}>{ui('events.openatlas')}</a>
					{#if i.text_url}
						<a href={i.text_url} rel="noreferrer">{ui('instruments.readtext')}</a>
					{/if}
				</p>
			</div>
		</li>
	{:else}
		<li class="empty">{ui('instruments.empty')}</li>
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
