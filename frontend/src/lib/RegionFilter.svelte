<script lang="ts">
	import type { Region } from './types';

	interface Props {
		regions: Region[];
		/** selected region ids; empty means the whole map */
		selected: string[];
		ontoggle: (id: string) => void;
		onclear: () => void;
	}
	let { regions, selected, ontoggle, onclear }: Props = $props();
</script>

<!-- Every region is listed rather than hidden behind a menu: Cyprus and Asia Minor
     are not visible in the default frame, so the map alone could never reach them. -->
<div class="regions" role="group" aria-label="Filter by region">
	{#each regions as r (r.id)}
		{@const on = selected.includes(r.id)}
		<button class:on aria-pressed={on} onclick={() => ontoggle(r.id)}>{r.name.en}</button>
	{/each}
	{#if selected.length}
		<button class="clear" onclick={onclear}>Clear</button>
	{/if}
</div>

<style>
	.regions {
		display: flex;
		flex-wrap: wrap;
		gap: 4px;
		margin-bottom: 10px;
	}
	button {
		font: inherit;
		font-size: 0.78rem;
		line-height: 1.35;
		background: var(--panel);
		color: var(--ink-soft);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 1px 7px;
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
