<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import FilterBar from '$lib/FilterBar.svelte';
	import { REVIEW_FACETS, REVIEW_LABELS, reviewTags, tally } from '$lib/review';
	import ReviewBadge from '$lib/ReviewBadge.svelte';
	import { year } from '$lib/time';
	import { list, matches, params, replaceParams } from '$lib/urlstate';

	let { data } = $props();

	let query = $state(untrack(() => page.url.searchParams.get('q') ?? ''));
	let roles = $state<string[]>(untrack(() => list(page.url, 'roles')));
	let review = $state<string[]>(untrack(() => list(page.url, 'review')));
	let born = $state<string[]>(untrack(() => list(page.url, 'born')));

	$effect(() => replaceParams(params({ q: query, roles, review, born })));

	// Taken from the corpus rather than the Literal in the backend, so a role that
	// nobody holds never appears as a chip that can only ever return nothing.
	const roleItems = $derived(
		[...new Set(data.figures.flatMap((f) => f.roles))]
			.sort()
			.map((r) => ({ id: r, label: r[0].toUpperCase() + r.slice(1) }))
	);

	const reviewCounts = $derived(tally(data.figures, (f) => f.review));
	const reviewItems = $derived(
		REVIEW_FACETS.filter((f) => reviewCounts.has(f)).map((f) => ({
			id: f,
			label: `${REVIEW_LABELS[f]} (${reviewCounts.get(f)})`
		}))
	);

	/** The century a life belongs to, by birth. The corpus spans three of them. */
	const centuryOf = (f: (typeof data.figures)[number]) =>
		f.born ? `${Math.floor(Number(year(f.born.date)) / 100) + 1}` : null;
	const centuryItems = $derived(
		[...new Set(data.figures.map(centuryOf).filter((c) => c !== null))]
			.sort()
			.map((c) => ({ id: c, label: `${c}th century` }))
	);

	const facetCount = $derived(roles.length + review.length + born.length);
	const active = $derived(query.trim().length > 0 || facetCount > 0);
	const shown = $derived(
		data.figures.filter((f) => {
			if (roles.length && !f.roles.some((r) => roles.includes(r))) return false;
			if (review.length && !reviewTags(f.review).some((t) => review.includes(t))) return false;
			const century = centuryOf(f);
			if (born.length && (!century || !born.includes(century))) return false;
			return matches(
				query,
				f.name.en,
				f.name.el,
				f.summary.en,
				// Both languages, and the dates: "1864" should find Venizelos.
				f.summary.el,
				f.roles.join(' '),
				f.born?.date,
				f.died?.date,
				...f.also_known_as.flatMap((n) => [n.en, n.el])
			);
		})
	);

	const toggle = (current: string[], id: string) =>
		current.includes(id) ? current.filter((x) => x !== id) : [...current, id];

	function clear() {
		query = '';
		roles = [];
		review = [];
		born = [];
	}
</script>

<svelte:head>
	<title>Figures — Greek History Atlas</title>
	<meta name="description" content="The people behind the events." />
</svelte:head>

<h1>Figures</h1>
<p class="lead">
	The people behind the events, in order of birth. Search reaches both languages, other
	spellings and the dates.
</p>

<FilterBar
	bind:query
	placeholder="Search names, roles, other spellings, years…"
	shown={shown.length}
	total={data.figures.length}
	noun="figures"
	{active}
	{facetCount}
	collapsible
	onclear={clear}
>
	{#snippet facets()}
		<ChipGroup
			label="Role"
			items={roleItems}
			selected={roles}
			ontoggle={(id) => (roles = toggle(roles, id))}
			onclear={() => (roles = [])}
		/>
		<ChipGroup
			label="Born"
			items={centuryItems}
			selected={born}
			ontoggle={(id) => (born = toggle(born, id))}
			onclear={() => (born = [])}
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

<ol class="figures">
	{#each shown as f (f.id)}
		<li>
			<span class="dates">
				{f.born ? year(f.born.date) : '?'}–{f.died ? year(f.died.date) : ''}
			</span>
			<div>
				<a href="/figures/{f.id}">{f.name.en}</a>
				<span class="roles">{f.roles.join(', ')}</span>
				<ReviewBadge review={f.review} />
				{#if f.also_known_as.length}
					<p class="aka">{f.also_known_as.map((n) => n.en).join('; ')}</p>
				{/if}
				<p>{f.summary.en}</p>
			</div>
		</li>
	{:else}
		<li class="empty">No figure matches that.</li>
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
	}
	.figures {
		list-style: none;
		padding: 0;
		margin: 0;
		max-width: 76ch;
		border-top: 1px solid var(--rule);
	}
	.figures li {
		display: grid;
		grid-template-columns: 9ch 1fr;
		gap: 12px;
		padding: 12px 0;
		border-bottom: 1px solid var(--rule);
	}
	.dates {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.85rem;
		color: var(--ink-soft);
		padding-top: 3px;
	}
	.figures a {
		font-family: var(--serif);
		font-size: 1.1rem;
		font-weight: 600;
		text-decoration: none;
		color: var(--ink);
	}
	.figures a:hover {
		color: var(--accent);
	}
	.roles {
		margin-left: 8px;
		margin-right: 6px;
		color: var(--ink-soft);
		font-size: 0.82rem;
	}
	.aka {
		font-style: italic;
	}
	.figures p {
		margin: 4px 0 0;
		color: var(--ink-soft);
		font-size: 0.92rem;
	}
	.empty {
		display: block;
		color: var(--ink-soft);
		padding: 14px 0;
	}
</style>
