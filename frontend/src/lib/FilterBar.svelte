<script lang="ts">
	import { untrack, type Snippet } from 'svelte';

	interface Props {
		query: string;
		placeholder?: string;
		/** how many rows survive the filter, and how many there are in all */
		shown: number;
		total: number;
		noun: string;
		/** whether anything is narrowing the list, so a Clear is worth offering */
		active: boolean;
		onclear: () => void;
		/** chip groups for whatever facets the page has */
		facets?: Snippet;
		/**
		 * Fold the facets behind a disclosure. Worth it past about three groups,
		 * where the chip rows stand taller than the list they filter; noise below that.
		 */
		collapsible?: boolean;
		/** how many facet selections are in force, shown on the closed disclosure */
		facetCount?: number;
	}
	let {
		query = $bindable(),
		placeholder = 'Search…',
		shown,
		total,
		noun,
		active,
		onclear,
		facets,
		collapsible = false,
		facetCount = 0
	}: Props = $props();
	const uid = $props.id();

	// Opens itself when the page is reached with filters already in the URL, so a
	// shared link shows what is narrowing it rather than an unexplained short list.
	// Deliberately the arrival value only: past that the disclosure is the reader's.
	let open = $state(untrack(() => facetCount > 0));
</script>

<div class="bar">
	<div class="row">
		<input
			id="{uid}-q"
			type="search"
			aria-label="Search {noun}"
			bind:value={query}
			{placeholder}
			autocomplete="off"
		/>
		<p class="count" aria-live="polite">
			{#if active}{shown} of {total} {noun}{:else}{total} {noun}{/if}
		</p>
		{#if active}
			<button class="clear" onclick={onclear}>Clear</button>
		{/if}
	</div>
	{#if facets && collapsible}
		<details class="fold" bind:open>
			<summary>
				Filters{#if facetCount}<span class="badge">{facetCount}</span>{/if}
			</summary>
			<div class="facets">{@render facets()}</div>
		</details>
	{:else if facets}
		<div class="facets">{@render facets()}</div>
	{/if}
</div>

<style>
	.bar {
		max-width: 76ch;
		margin-bottom: 18px;
		display: flex;
		flex-direction: column;
		gap: 9px;
	}
	.row {
		display: flex;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
	}
	input[type='search'] {
		flex: 1;
		min-width: 12rem;
		font: inherit;
		font-size: 0.9rem;
		background: var(--panel);
		color: var(--ink);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 5px 10px;
	}
	input[type='search']:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: -1px;
		border-color: transparent;
	}
	.count {
		margin: 0;
		flex: none;
		color: var(--ink-soft);
		font-size: 0.8rem;
		font-variant-numeric: tabular-nums;
	}
	.fold summary {
		cursor: pointer;
		color: var(--ink-soft);
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
	}
	.fold summary:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
		border-radius: var(--radius);
	}
	.fold .facets {
		display: flex;
		flex-direction: column;
		gap: 9px;
		margin-top: 9px;
	}
	.badge {
		margin-left: 6px;
		color: var(--accent);
		font-variant-numeric: tabular-nums;
	}
	.clear {
		flex: none;
		font: inherit;
		font-size: 0.8rem;
		background: none;
		border: 0;
		color: var(--accent);
		text-decoration: underline;
		cursor: pointer;
		padding: 0;
	}
</style>
