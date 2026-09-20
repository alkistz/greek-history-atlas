<script lang="ts">
	import type { Snippet } from 'svelte';

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
	}
	let {
		query = $bindable(),
		placeholder = 'Search…',
		shown,
		total,
		noun,
		active,
		onclear,
		facets
	}: Props = $props();
	const uid = $props.id();
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
	{#if facets}
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
