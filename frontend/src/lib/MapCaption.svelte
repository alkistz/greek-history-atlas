<script lang="ts">
	import TerritoryTrend, { type TrendPoint } from './TerritoryTrend.svelte';
	import { prettyDate } from './time';

	interface Props {
		date: string;
		areaKm2: number;
		instruments: { id: string; name: string }[];
		/** the same figure across the whole period, as context for today's */
		trend?: TrendPoint[];
		day?: number;
		maxDay?: number;
	}
	let { date, areaKm2, instruments, trend = [], day = 0, maxDay = 1 }: Props = $props();
</script>

<div class="caption">
	<div class="date">{prettyDate(date)}</div>
	<div class="figures">
		<div class="value">
			<span class="km2">{areaKm2.toLocaleString('en-GB', { maximumFractionDigits: 0 })} km²</span>
			<span class="km2-label">Greek sovereign territory</span>
		</div>
		{#if trend.length}
			<TerritoryTrend points={trend} {day} {maxDay} />
		{/if}
	</div>
</div>
{#if instruments.length}
	<p class="instrument">
		In force from today:
		{#each instruments as i, n (i.id)}{n ? '; ' : ''}<a href="/instruments/{i.id}">{i.name}</a>{/each}
	</p>
{/if}

<style>
	.caption {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 16px;
		flex-wrap: wrap;
		margin-top: 14px;
	}
	.date {
		font-family: var(--serif);
		font-size: 1.4rem;
	}
	.figures {
		display: flex;
		align-items: flex-end;
		gap: 14px;
	}
	.value {
		display: flex;
		align-items: baseline;
		gap: 8px;
	}
	.km2 {
		white-space: nowrap;
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 1.05rem;
	}
	.km2-label {
		color: var(--ink-soft);
		font-size: 0.85rem;
	}
	.instrument {
		margin: 6px 0 0;
		color: var(--accent);
		font-size: 0.9rem;
	}
	.instrument a {
		color: inherit;
	}

	@media (max-width: 620px) {
		.figures {
			flex-direction: column;
			align-items: flex-start;
			gap: 6px;
		}
	}
</style>
