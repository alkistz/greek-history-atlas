<script lang="ts">
	import { untrack } from 'svelte';
	import { page } from '$app/state';
	import ChipGroup from '$lib/ChipGroup.svelte';
	import IndexPage from '$lib/IndexPage.svelte';
	import Network from '$lib/Network.svelte';
	import { num, t } from '$lib/lang.svelte';
	import { regimeLabel } from '$lib/regimes';
	import type { NetworkEdge, NetworkNode } from '$lib/types';
	import { ui } from '$lib/ui';
	import { params, replaceParams } from '$lib/urlstate';

	let { data } = $props();

	// Which regime, and how many shared events a link needs. Both in the URL, so
	// a filtered picture can be sent; `focus` arrives from a figure page.
	let regime = $state(untrack(() => page.url.searchParams.get('regime') ?? ''));
	let min = $state(untrack(() => Number(page.url.searchParams.get('min') ?? 1) || 1));
	const focus = $derived(page.url.searchParams.get('focus'));
	$effect(() => replaceParams(params({ regime, min: min > 1 ? String(min) : '', focus: focus ?? '' })));

	const range = $derived.by((): [string, string | null] | null => {
		const r = data.meta.regimes.find((r) => r.id === regime);
		return r ? [r.from, r.to] : null;
	});
	const inRange = (iso: string) =>
		range === null || (range[0] <= iso && (range[1] === null || iso < range[1]));

	// A figure is on the page if they acted under the regime; a link if enough
	// of the events it rests on fall there. A recorded tie has no date and stays
	// as long as both ends do, since a rivalry is not confined to one regime.
	const nodes = $derived.by((): NetworkNode[] =>
		range === null
			? data.network.nodes
			: data.network.nodes.filter((n) => n.events.some((e) => inRange(e.date)))
	);
	const edges = $derived.by((): (NetworkEdge & { weight: number })[] => {
		const ids = new Set(nodes.map((n) => n.id));
		return data.network.edges
			.map((e) => ({ ...e, weight: e.events.filter((ev) => inRange(ev.date)).length }))
			.filter(
				(e) =>
					ids.has(e.source) &&
					ids.has(e.target) &&
					(e.weight >= min || (min <= 1 && e.relations.length > 0))
			);
	});

	// Both tables rank what is on the page under the current filter, so a reader
	// can ask who bridged the Occupation rather than only the whole corpus.
	// Betweenness is corpus-wide; degree is recounted from the links shown.
	const degree = $derived.by(() => {
		const d = new Map<string, number>();
		for (const e of edges) {
			d.set(e.source, (d.get(e.source) ?? 0) + 1);
			d.set(e.target, (d.get(e.target) ?? 0) + 1);
		}
		return d;
	});
	const bridges = $derived(
		[...nodes].sort((a, b) => b.betweenness - a.betweenness).slice(0, 10)
	);
	const hubs = $derived(
		[...nodes]
			.map((n) => ({ ...n, shown: degree.get(n.id) ?? 0 }))
			.sort((a, b) => b.shown - a.shown || b.events.length - a.events.length)
			.slice(0, 10)
	);

	const minChips = [1, 2, 3].map((n) => ({ id: String(n), label: ui('network.atleast', { n }) }));
</script>

<svelte:head>
	<title>{ui('page.title', { page: ui('page.network'), site: ui('site.name') })}</title>
	<meta name="description" content={ui('network.description')} />
</svelte:head>

<IndexPage title={ui('page.network')} lead={ui('network.lead')}>
	{#snippet filters()}
		<div class="filters">
			<label class="field">
				<span class="caption">{ui('facet.regime')}</span>
				<select bind:value={regime}>
					<option value="">{ui('network.all')}</option>
					{#each data.meta.regimes as r (r.id)}
						<option value={r.id}>{regimeLabel(r)}</option>
					{/each}
				</select>
			</label>
			<ChipGroup
				label={ui('network.min')}
				items={minChips}
				selected={[String(min)]}
				ontoggle={(id) => (min = Number(id))}
			/>
			<p class="count">{ui('network.shown', { n: nodes.length, m: edges.length })}</p>
			<p class="caveat">{ui('network.caveat')}</p>
		</div>
	{/snippet}

	{#if edges.length}
		<Network {nodes} {edges} polities={data.meta.polities} {focus} {range} />
	{:else}
		<p class="empty">{ui('network.empty')}</p>
	{/if}

	<div class="tables">
		<section>
			<h2>{ui('network.bridges')}</h2>
			<p class="lead">{ui('network.bridges.lead')}</p>
			<ol>
				{#each bridges as n (n.id)}
					<li>
						<a href="/figures/{n.id}">{t(n.name)}</a>
						<span class="mono">{num(n.betweenness, 2)}</span>
					</li>
				{/each}
			</ol>
		</section>
		<section>
			<h2>{ui('network.hubs')}</h2>
			<p class="lead">{ui('network.hubs.lead')}</p>
			<ol>
				{#each hubs as n (n.id)}
					<li>
						<a href="/figures/{n.id}">{t(n.name)}</a>
						<span class="mono">{n.shown}</span>
					</li>
				{/each}
			</ol>
		</section>
	</div>
</IndexPage>

<style>
	.filters {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}
	.field {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}
	.caption {
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
		color: var(--ink-soft);
	}
	select {
		padding: 6px 8px;
		background: var(--panel);
		color: var(--ink);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		font-size: 0.9rem;
	}
	.count {
		margin: 0;
		font-size: 0.85rem;
		color: var(--ink-soft);
	}
	.caveat {
		margin: 0;
		font-size: 0.82rem;
		color: var(--ink-soft);
		max-width: 36ch;
	}
	.empty {
		color: var(--ink-soft);
	}
	.tables {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
		gap: 24px;
		margin-top: 20px;
	}
	h2 {
		font-size: 1.05rem;
		margin: 0 0 4px;
	}
	.lead {
		margin: 0 0 8px;
		font-size: 0.85rem;
		color: var(--ink-soft);
	}
	ol {
		margin: 0;
		padding-left: 1.6em;
	}
	li {
		display: flex;
		justify-content: space-between;
		gap: 12px;
		margin: 2px 0;
	}
	li a {
		text-decoration: none;
	}
	li a:hover {
		text-decoration: underline;
	}
	.mono {
		font-family: var(--figures);
		font-variant-numeric: tabular-nums;
		font-size: 0.85rem;
		color: var(--ink-soft);
	}
</style>
