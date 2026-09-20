<script module lang="ts">
	export interface TrendPoint {
		day: number;
		km2: number;
	}
</script>

<script lang="ts">
	import { num } from './lang.svelte';
	import { ui } from './ui';

	interface Props {
		points: TrendPoint[];
		/** the day the map is showing, marked on the trend */
		day: number;
		maxDay: number;
	}
	let { points, day, maxDay }: Props = $props();

	const W = 168;
	const H = 38;
	const BASE = H - 3;
	const TOP = 3;

	// Zero baseline, never the minimum: a truncated axis would make a frontier
	// adjustment look like the country doubling.
	const peak = $derived(Math.max(...points.map((p) => p.km2), 1));
	const x = (d: number) => (d / maxDay) * W;
	const y = (km2: number) => BASE - (km2 / peak) * (BASE - TOP);

	/**
	 * A step, not a slope. Territory moved on the day a treaty took effect; drawing
	 * a diagonal between two dates would invent a decade of gradual annexation.
	 */
	const steps = $derived.by(() => {
		if (!points.length) return { line: '', area: '' };
		let line = `M ${x(points[0].day).toFixed(1)} ${y(points[0].km2).toFixed(1)}`;
		for (const p of points.slice(1)) {
			line += ` H ${x(p.day).toFixed(1)} V ${y(p.km2).toFixed(1)}`;
		}
		line += ` H ${W}`;
		const area = `${line} V ${BASE} H ${x(points[0].day).toFixed(1)} Z`;
		return { line, area };
	});

	const now = $derived.by(() => {
		let km2 = 0;
		for (const p of points) if (p.day <= day) km2 = p.km2;
		return { x: x(day), y: y(km2) };
	});
</script>

<svg
	class="trend"
	viewBox="0 0 {W} {H}"
	width={W}
	height={H}
	role="img"
	aria-label={ui('trend.aria', { n: num(peak) })}
>
	<path class="area" d={steps.area} />
	<path class="line" d={steps.line} />
	<line class="baseline" x1="0" y1={BASE} x2={W} y2={BASE} />
	<circle class="now" cx={now.x} cy={now.y} r="2.75" />
</svg>

<style>
	.trend {
		display: block;
		overflow: visible;
	}
	/* Recessive by design: the figure beside it is the reading, this is its context. */
	.area {
		fill: var(--coast);
		opacity: 0.18;
	}
	.line {
		fill: none;
		stroke: var(--coast);
		stroke-width: 1.5;
		stroke-linejoin: round;
		vector-effect: non-scaling-stroke;
	}
	.baseline {
		stroke: var(--rule);
		stroke-width: 1;
	}
	.now {
		fill: var(--accent);
		stroke: var(--ground);
		stroke-width: 1.5;
	}
</style>
