<script lang="ts">
	import { prettyDate } from './time';

	interface Row {
		kind: string;
		polity: string;
		since: string;
		instrument: string | null;
	}
	interface Props {
		x: number;
		y: number;
		flip: boolean;
		title: string;
		region?: string | null;
		rows: Row[];
	}
	let { x, y, flip, title, region = null, rows }: Props = $props();

	const verb: Record<string, string> = {
		sovereign: 'Sovereign',
		administered: 'Administered by',
		occupied: 'Occupied by',
		insurgent: 'In revolt'
	};
</script>

<div
	class="tip"
	class:flip
	role="status"
	style:left="{x}px"
	style:top="{y}px"
>
	<div class="title">{title}</div>
	{#if region}<div class="region">{region}</div>{/if}
	{#each rows as r (r.kind + r.polity)}
		<div class="row">
			<span class="kind">{verb[r.kind] ?? r.kind}</span>
			{r.polity} since {prettyDate(r.since)}
			{#if r.instrument}<span class="inst">{r.instrument}</span>{/if}
		</div>
	{:else}
		<div class="row muted">Not modelled on this date</div>
	{/each}
</div>

<style>
	.tip {
		position: absolute;
		transform: translate(12px, 12px);
		max-width: 260px;
		background: var(--panel);
		color: var(--ink);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		box-shadow: 0 2px 10px #0002;
		padding: 6px 9px;
		font-size: 0.8rem;
		line-height: 1.4;
		pointer-events: none;
		z-index: 2;
	}
	.tip.flip {
		transform: translate(calc(-100% - 12px), 12px);
	}
	.title {
		font-family: var(--serif);
		font-size: 0.95rem;
		margin-bottom: 2px;
	}
	.region {
		color: var(--ink-soft);
		font-size: 0.74rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		margin-bottom: 3px;
	}
	.row {
		color: var(--ink-soft);
	}
	.kind {
		color: var(--ink);
		font-weight: 600;
	}
	.inst {
		display: block;
		font-size: 0.74rem;
	}
	.muted {
		font-style: italic;
	}
</style>
