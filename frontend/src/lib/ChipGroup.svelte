<script module lang="ts">
	export interface Chip {
		id: string;
		label: string;
	}
</script>

<script lang="ts">
	import { ui } from './ui';

	interface Props {
		/** shown before the chips, and used as the group's accessible name */
		label: string;
		items: Chip[];
		selected: string[];
		ontoggle: (id: string) => void;
		/** a Clear appears once anything is selected */
		onclear?: () => void;
		/** hide the visible caption but keep the accessible one */
		quiet?: boolean;
	}
	let { label, items, selected, ontoggle, onclear, quiet = false }: Props = $props();
</script>

<div class="chips" role="group" aria-label={label}>
	{#if !quiet}<span class="caption">{label}</span>{/if}
	{#each items as item (item.id)}
		{@const on = selected.includes(item.id)}
		<button class:on aria-pressed={on} onclick={() => ontoggle(item.id)}>{item.label}</button>
	{/each}
	{#if onclear && selected.length}
		<button class="clear" onclick={onclear}>{ui('filter.clear')}</button>
	{/if}
</div>

<style>
	.chips {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 5px;
	}
	.caption {
		color: var(--ink-soft);
		font-size: 0.74rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
		margin-right: 3px;
	}
	button {
		font: inherit;
		font-size: 0.8rem;
		line-height: 1.35;
		background: var(--panel);
		color: var(--ink-soft);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 1px 8px;
		cursor: pointer;
	}
	button:hover {
		color: var(--accent);
		border-color: var(--accent);
	}
	button.on {
		background: transparent;
		color: var(--accent);
		border-color: var(--accent);
		font-weight: 600;
	}
	.clear {
		background: none;
		border-color: transparent;
		text-decoration: underline;
	}
</style>
