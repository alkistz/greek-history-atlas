<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import FilterBar from '$lib/FilterBar.svelte';
	import IndexPage from '$lib/IndexPage.svelte';
	import { both, t } from '$lib/lang.svelte';
	import { term, Term, ui } from '$lib/ui';
	import { REVIEW_FACETS, reviewLabel, reviewTags, tally } from '$lib/review';
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
			.map((r) => ({ id: r, label: Term('role.figure', r) }))
	);

	const reviewCounts = $derived(tally(data.figures, (f) => f.review));
	const reviewItems = $derived(
		REVIEW_FACETS.filter((f) => reviewCounts.has(f)).map((f) => ({
			id: f,
			label: ui('facet.count', { label: reviewLabel(f), n: reviewCounts.get(f) ?? 0 })
		}))
	);

	/** The century a life belongs to, by birth. The corpus spans three of them. */
	const centuryOf = (f: (typeof data.figures)[number]) =>
		f.born ? `${Math.floor(Number(year(f.born.date)) / 100) + 1}` : null;
	const centuryItems = $derived(
		[...new Set(data.figures.map(centuryOf).filter((c) => c !== null))]
			.sort()
			.map((c) => ({ id: c, label: term('century', c) }))
	);

	const facetCount = $derived(roles.length + review.length + born.length);
	const active = $derived(query.trim().length > 0 || facetCount > 0);
	const shown = $derived(
		data.figures.filter((f) => {
			if (roles.length && !f.roles.some((r) => roles.includes(r))) return false;
			if (review.length && !reviewTags(f.review).some((tag) => review.includes(tag))) return false;
			const century = centuryOf(f);
			if (born.length && (!century || !born.includes(century))) return false;
			return matches(
				query,
				// Both languages, and the dates: "1864" should find Venizelos.
				...both(f.name),
				...both(f.summary),
				f.roles.join(' '),
				f.born?.date,
				f.died?.date,
				...f.also_known_as.flatMap(both)
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
	<title>{ui('page.title', { page: ui('page.figures'), site: ui('site.name') })}</title>
	<meta name="description" content={ui('figures.description')} />
</svelte:head>

<IndexPage title={ui('page.figures')} lead={ui('figures.lead')}>
	{#snippet filters()}
		<FilterBar
			bind:query
			placeholder={ui('figures.placeholder')}
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
					label={ui('facet.role')}
					items={roleItems}
					selected={roles}
					ontoggle={(id) => (roles = toggle(roles, id))}
					onclear={() => (roles = [])}
				/>
				<ChipGroup
					label={ui('facet.born')}
					items={centuryItems}
					selected={born}
					ontoggle={(id) => (born = toggle(born, id))}
					onclear={() => (born = [])}
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

	<ol class="figures">
		{#each shown as f (f.id)}
			<li>
				<a class="card" href="/figures/{f.id}">
					<span class="dates">
						{f.born ? year(f.born.date) : '?'}–{f.died ? year(f.died.date) : ''}
					</span>
					<span class="name">{t(f.name)}</span>
					{#if f.also_known_as.length}
						<span class="aka">{f.also_known_as.map(t).join('; ')}</span>
					{/if}
					<span class="roles">{f.roles.map((r) => term('role.figure', r)).join(', ')}</span>
					<span class="summary">{t(f.summary)}</span>
					<span class="foot"><ReviewBadge review={f.review} /></span>
				</a>
			</li>
		{:else}
			<li class="empty">{ui('figures.empty')}</li>
		{/each}
	</ol>
</IndexPage>

<style>
	.figures {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 270px), 1fr));
		gap: 10px;
	}
	.card {
		display: flex;
		flex-direction: column;
		gap: 2px;
		height: 100%;
		box-sizing: border-box;
		padding: 12px 14px;
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
		color: inherit;
		text-decoration: none;
		transition:
			border-color 120ms ease,
			box-shadow 120ms ease,
			transform 120ms ease;
	}
	.card:hover {
		border-color: var(--ink-soft);
		box-shadow: var(--elev-1);
		transform: translateY(-1px);
	}
	.card:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
	}
	.dates {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.78rem;
		color: var(--ink-soft);
	}
	.name {
		font-family: var(--serif);
		font-size: 1.12rem;
		font-weight: 600;
		color: var(--ink);
	}
	.card:hover .name {
		color: var(--accent);
	}
	.aka {
		font-style: italic;
		font-size: 0.85rem;
		color: var(--ink-soft);
	}
	.roles {
		color: var(--ink-soft);
		font-size: 0.76rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	.summary {
		margin-top: 6px;
		color: var(--ink-soft);
		font-size: 0.88rem;
		display: -webkit-box;
		-webkit-line-clamp: 4;
		line-clamp: 4;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
	.foot {
		margin-top: auto;
		padding-top: 8px;
	}
	.empty {
		display: block;
		color: var(--ink-soft);
		padding: 14px 0;
	}
	@media (prefers-reduced-motion: reduce) {
		.card {
			transition: none;
		}
		.card:hover {
			transform: none;
		}
	}
</style>
