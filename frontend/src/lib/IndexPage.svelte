<!--
	The shape every index shares: a heading, a lead, the filters, the list.

	Wide, the filters stand in a column of their own beside the list and stay put
	while it scrolls, so what is narrowing the list is always in view. Narrow, they
	sit above it, as they always did.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		title: string;
		lead?: string;
		filters?: Snippet;
		children: Snippet;
	}
	let { title, lead, filters, children }: Props = $props();
</script>

<h1>{title}</h1>
{#if lead}<p class="lead">{lead}</p>{/if}

<div class="index" class:sidebar={!!filters}>
	{#if filters}
		<aside class="filters">{@render filters()}</aside>
	{/if}
	<div class="list">{@render children()}</div>
</div>

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
	.index {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: 20px 32px;
		align-items: start;
	}
	.list {
		min-width: 0;
	}
	@media (min-width: 1100px) {
		.index.sidebar {
			grid-template-columns: 260px minmax(0, 1fr);
		}
		.filters {
			position: sticky;
			top: calc(var(--header-h, 0px) + 12px);
			max-height: calc(100vh - var(--header-h, 0px) - 24px);
			overflow: auto;
			padding-right: 4px;
		}
	}
</style>
