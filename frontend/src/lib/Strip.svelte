<script module lang="ts">
	/** A dot on the strip; with an href it is a link. */
	export interface StripMark {
		id: string;
		day: number;
		title: string;
		significance?: number;
		href?: string;
	}
</script>

<script lang="ts">
	import { toDay, toISO, year } from './time';
	import { ui } from './ui';

	interface Props {
		/** ISO date that day 0 counts from */
		origin: string;
		maxDay: number;
		marks?: StripMark[];
		/** a span drawn as a bar: a life, or an arc's first to last event */
		span?: [number, number] | null;
		/** the words for the span, for a reader who cannot see it */
		label?: string;
	}
	let { origin, maxDay, marks = [], span = null, label = '' }: Props = $props();

	const H = 40;
	const PAD = 6;
	const AXIS = 24;

	let width = $state(0);
	const inner = $derived(Math.max(width - PAD * 2, 1));
	const x = (d: number) => PAD + (Math.min(Math.max(d, 0), maxDay) / maxDay) * inner;

	const startYear = $derived(Number(year(origin)));
	const endYear = $derived(Number(year(toISO(maxDay, origin))));
	const step = $derived.by(() => {
		const years = Math.max(endYear - startYear, 1);
		for (const s of [10, 20, 25, 50]) if ((years / s) * 52 <= width) return s;
		return 100;
	});
	const ticks = $derived.by(() => {
		const out: { y: number; x: number }[] = [];
		for (let y = Math.ceil(startYear / step) * step; y <= endYear; y += step) {
			out.push({ y, x: x(toDay(`${y}-01-01`, origin)) });
		}
		return out;
	});

	const radius = (s: number | undefined) => 2 + Math.min(Math.max(s ?? 3, 1), 5) * 0.5;
	// Rows, as on the timeline, so a busy decade does not pile into one blot.
	const placed = $derived.by(() => {
		const lastInRow: number[] = [];
		return [...marks]
			.sort((a, b) => a.day - b.day)
			.map((m) => {
				const r = radius(m.significance);
				const cx = x(m.day);
				let row = 0;
				while (row < 2 && lastInRow[row] !== undefined && cx - r < lastInRow[row] + 1.5) row++;
				if (row === 2) row = 0;
				lastInRow[row] = cx + r;
				return { ...m, cx, r, cy: AXIS - 8 - row * 7 };
			});
	});
	const aria = $derived(
		label || ui('strip.aria', { n: marks.length, from: startYear, to: endYear })
	);
</script>

<div class="strip" bind:clientWidth={width}>
	{#if width > 0}
		<svg viewBox="0 0 {width} {H}" width={width} height={H} role="img" aria-label={aria}>
			<line class="axis" x1={PAD} y1={AXIS} x2={width - PAD} y2={AXIS} />
			{#each ticks as t (t.y)}
				<line class="tick" x1={t.x} y1={AXIS} x2={t.x} y2={AXIS + 4} />
				<text class="tick-label" x={t.x} y={AXIS + 14}>{t.y}</text>
			{/each}
			{#if span}
				<rect class="span" x={x(span[0])} y={AXIS - 3} width={Math.max(x(span[1]) - x(span[0]), 2)} height={6} rx="3" />
			{/if}
			{#each placed as m (m.id)}
				{#if m.href}
					<a href={m.href}>
						<circle class="mark" cx={m.cx} cy={m.cy} r={m.r}><title>{m.title}</title></circle>
					</a>
				{:else}
					<circle class="mark" cx={m.cx} cy={m.cy} r={m.r}><title>{m.title}</title></circle>
				{/if}
			{/each}
		</svg>
	{/if}
</div>

<style>
	.strip {
		width: 100%;
	}
	svg {
		display: block;
		overflow: visible;
	}
	.axis,
	.tick {
		stroke: var(--rule);
		stroke-width: 1;
	}
	.tick-label {
		font-family: var(--mono);
		font-size: 9px;
		fill: var(--ink-soft);
		text-anchor: middle;
	}
	.span {
		fill: var(--accent);
		opacity: 0.35;
	}
	.mark {
		fill: var(--ink);
		opacity: 0.8;
		transition: fill 120ms ease;
	}
	a .mark:hover {
		fill: var(--accent);
		opacity: 1;
	}
	a:focus-visible .mark {
		fill: var(--accent);
		stroke: var(--accent);
		stroke-width: 3;
		stroke-opacity: 0.35;
	}
</style>
