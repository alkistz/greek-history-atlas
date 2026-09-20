<script lang="ts">
	import type { FrameId } from './projection';
	import { prettyDate } from './time';

	interface Props {
		date: string;
		areaKm2: number;
		instruments: { id: string; name: string }[];
		frame: FrameId;
		onreset?: () => void;
	}
	let { date, areaKm2, instruments, frame, onreset }: Props = $props();
</script>

<div class="caption">
	<div class="date">{prettyDate(date)}</div>
	<div class="figures">
		<span class="km2">{areaKm2.toLocaleString('en-GB', { maximumFractionDigits: 0 })} km²</span>
		<span class="km2-label">Greek sovereign territory</span>
	</div>
</div>
{#if instruments.length}
	<p class="instrument">
		In force from today:
		{#each instruments as i, n (i.id)}{n ? '; ' : ''}<a href="/instruments/{i.id}">{i.name}</a>{/each}
	</p>
{/if}
{#if frame !== 'greece'}
	<p class="frame">
		Showing the <em>{frame}</em> frame. <button onclick={onreset}>Back to Greece</button>
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
		align-items: baseline;
		gap: 8px;
	}
	.km2 {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 1.05rem;
	}
	.km2-label {
		color: var(--ink-soft);
		font-size: 0.85rem;
	}
	.instrument,
	.frame {
		margin: 6px 0 0;
		color: var(--accent);
		font-size: 0.9rem;
	}
	.instrument a {
		color: inherit;
	}
	.frame button {
		font: inherit;
		font-size: 0.85rem;
		background: none;
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		color: var(--ink);
		padding: 1px 8px;
		cursor: pointer;
	}
</style>
