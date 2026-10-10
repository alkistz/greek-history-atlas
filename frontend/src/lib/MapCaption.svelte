<script lang="ts">
	import TerritoryTrend, { type TrendPoint } from './TerritoryTrend.svelte';
	import { num, t } from './lang.svelte';
	import { prettyDate } from './time';
	import { term, ui } from './ui';
	import type { Regime } from './types';

	interface Props {
		date: string;
		areaKm2: number;
		instruments: { id: string; name: string }[];
		/** the same figure across the whole period, as context for today's */
		trend?: TrendPoint[];
		day?: number;
		maxDay?: number;
		/**
		 * What the Greek state itself was on this date. Control says who held the
		 * ground; after 1960 the ground stops moving and this does not, which is
		 * the whole reason the axis exists.
		 */
		regime?: Regime | null;
		/** one line for the regime, no gloss: the deck under a map has no room for prose */
		compact?: boolean;
	}
	let {
		date,
		areaKm2,
		instruments,
		trend = [],
		day = 0,
		maxDay = 1,
		regime = null,
		compact = false
	}: Props = $props();

	const kindLabel = (kind: string) => term('kind.regime', kind);
</script>

<div class="caption" class:compact>
	<div class="date">{prettyDate(date)}</div>
	<div class="figures">
		<div class="value">
			<span class="km2">{num(areaKm2)} km²</span>
			<span class="km2-label">{ui('caption.territory')}</span>
		</div>
		{#if trend.length}
			<TerritoryTrend points={trend} {day} {maxDay} />
		{/if}
	</div>
</div>
{#if regime}
	<p class="regime" class:compact>
		<a href="/events?regimes={regime.id}">{t(regime.name)}</a>
		<span class="kind">{kindLabel(regime.kind)}</span>
		{#if regime.summary && !compact}<span class="gloss">{t(regime.summary)}</span>{/if}
		{#if instruments.length}
			<span class="instrument">
				· {ui('caption.inforce')}
				{#each instruments as i, n (i.id)}{n ? '; ' : ''}<a href="/instruments/{i.id}">{i.name}</a>{/each}
			</span>
		{/if}
	</p>
{:else if instruments.length}
	<p class="regime" class:compact>
		<span class="instrument">
			{ui('caption.inforce')}
			{#each instruments as i, n (i.id)}{n ? '; ' : ''}<a href="/instruments/{i.id}">{i.name}</a>{/each}
		</span>
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
	.caption.compact {
		margin-top: 8px;
	}
	.date {
		font-family: var(--serif);
		font-size: 1.4rem;
		font-variant-numeric: tabular-nums;
	}
	.compact .date {
		font-size: 1.25rem;
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
	.regime {
		margin: 8px 0 0;
		font-size: 0.88rem;
		color: var(--ink-soft);
	}
	.regime.compact {
		margin-top: 2px;
		font-size: 0.84rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.regime .kind {
		margin-left: 8px;
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		opacity: 0.8;
	}
	.regime .gloss {
		display: block;
		font-size: 0.84rem;
	}
	.instrument {
		color: var(--accent);
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
		.compact .figures {
			flex-direction: row;
			align-items: baseline;
		}
		.compact .km2-label {
			display: none;
		}
		.caption.compact {
			margin-top: 4px;
		}
		.compact .date {
			font-size: 1.1rem;
		}
	}
</style>
