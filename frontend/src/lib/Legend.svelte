<script lang="ts">
	import { t } from './lang.svelte';
	import { term } from './ui';
	import type { LegendEntry } from './resolve';
	import Swatch from './Swatch.svelte';

	interface Props {
		entries: LegendEntry[];
	}
	let { entries }: Props = $props();
</script>

<ul class="legend">
	{#each entries as e (e.polity.id + e.role)}
		<li>
			<Swatch colour={e.polity.colour ?? 'transparent'} role={e.role} polityId={e.polity.id} />
			<span class="pname">{t(e.polity.name)}</span>
			<span class="prole">{term('role.map', e.role)}</span>
		</li>
	{/each}
</ul>

<style>
	.legend {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 4px 14px;
	}
	.legend li {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 0.86rem;
	}
	.prole {
		color: var(--ink-soft);
		font-size: 0.78rem;
	}
</style>
