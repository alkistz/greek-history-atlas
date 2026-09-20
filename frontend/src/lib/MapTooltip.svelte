<script lang="ts">
	import { prettyDate } from './time';

	interface Row {
		kind: string;
		polity: string;
		since: string;
		instrument: string | null;
		/** why the row is drawn as it is, where the atom grain approximates something */
		note: string | null;
		/** empire, protectorate, autonomous... shown only where it is not a plain state */
		polityKind: string | null;
	}
	interface Props {
		x: number;
		y: number;
		flip: boolean;
		title: string;
		region?: string | null;
		rows: Row[];
		/** the atom's own area, which is what the km² figure is built from */
		areaKm2?: number | null;
		/** outside the modern Greek state, so excluded from that figure */
		external?: boolean;
	}
	let {
		x,
		y,
		flip,
		title,
		region = null,
		rows,
		areaKm2 = null,
		external = false
	}: Props = $props();

	const km2 = (n: number) => `${n.toLocaleString('en-GB', { maximumFractionDigits: 0 })} km²`;

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
	{#if areaKm2 != null}
		<div class="area">
			{km2(areaKm2)}{#if external}<span class="ext"> · outside the modern state, not counted in the total</span>{/if}
		</div>
	{/if}
	{#each rows as r (r.kind + r.polity)}
		<div class="row">
			<span class="kind">{verb[r.kind] ?? r.kind}</span>
			{r.polity}{#if r.polityKind}<span class="pk"> ({r.polityKind})</span>{/if} since {prettyDate(r.since)}
			{#if r.instrument}<span class="inst">{r.instrument}</span>{/if}
			{#if r.note}<span class="note">{r.note}</span>{/if}
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
	.area {
		color: var(--ink-soft);
		font-family: var(--mono);
		font-size: 0.74rem;
		margin-bottom: 3px;
	}
	.ext {
		font-family: var(--sans);
		font-style: italic;
	}
	.pk {
		color: var(--ink-soft);
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
	.note {
		display: block;
		font-size: 0.74rem;
		font-style: italic;
		margin-top: 2px;
	}
	.muted {
		font-style: italic;
	}
</style>
