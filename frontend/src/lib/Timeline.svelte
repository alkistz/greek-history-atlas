<script module lang="ts">
	export interface TimelineEvent {
		id: string;
		day: number;
		title: string;
		significance: number;
		/** outside the current filter: drawn faint, never removed */
		muted?: boolean;
	}
</script>

<script lang="ts">
	import { prettyDate, toDay, toISO, year } from './time';
	import { ui } from './ui';

	interface Props {
		/** days from the origin */
		day: number;
		maxDay: number;
		/** days on which the map changes: tick marks, snapping, and the step buttons */
		epochDays: number[];
		/** ISO date that day 0 counts from, for the year ruler */
		origin: string;
		events?: TimelineEvent[];
		selectedId?: string | null;
		onselectevent?: (id: string) => void;
	}

	let {
		day = $bindable(),
		maxDay,
		epochDays,
		origin,
		events = [],
		selectedId = null,
		onselectevent
	}: Props = $props();

	const H = 82;
	const PAD = 10;
	const AXIS = 42;

	let width = $state(0);
	const span = $derived(Math.max(width - PAD * 2, 1));
	const x = (d: number) => PAD + (d / maxDay) * span;
	const dayAt = (px: number) => clamp(Math.round(((px - PAD) / span) * maxDay));
	const clamp = (d: number) => Math.min(Math.max(Math.round(d), 0), maxDay);

	const date = $derived(toISO(day, origin));

	/** Pull a scrub within 6px of a change of control onto it, so exact dates are reachable. */
	function snap(d: number): number {
		let best = d;
		let bestDist = (6 / span) * maxDay;
		for (const e of epochDays) {
			const dist = Math.abs(e - d);
			if (dist <= bestDist) {
				best = e;
				bestDist = dist;
			}
		}
		return best;
	}

	// The ruler picks the coarsest step that still labels the whole span without
	// the years colliding, so it reads the same on a phone and on a desktop.
	const startYear = $derived(Number(year(origin)));
	const endYear = $derived(Number(year(toISO(maxDay, origin))));
	const step = $derived.by(() => {
		const years = Math.max(endYear - startYear, 1);
		for (const s of [5, 10, 20, 25, 50]) if ((years / s) * 62 <= width) return s;
		return 100;
	});
	const ticks = $derived.by(() => {
		const out: { y: number; x: number }[] = [];
		for (let y = Math.ceil(startYear / step) * step; y <= endYear; y += step) {
			out.push({ y, x: x(toDay(`${y}-01-01`, origin)) });
		}
		return out;
	});

	const ROWS = 4;
	const ROW_H = 8;
	const radius = (significance: number) => 2.5 + Math.min(Math.max(significance, 1), 5) * 0.6;

	/**
	 * Events cluster hard — a revolution is a decade of them — so markers stack into
	 * rows instead of piling into an unreadable blob on the axis.
	 */
	const marks = $derived.by(() => {
		const lastInRow: number[] = [];
		return [...events]
			.sort((a, b) => a.day - b.day)
			.map((e) => {
				const r = radius(e.significance);
				const cx = x(e.day);
				let row = 0;
				while (row < ROWS && lastInRow[row] !== undefined && cx - r < lastInRow[row] + 1.5) row++;
				if (row === ROWS) row = 0;
				lastInRow[row] = cx + r;
				return { ...e, cx, r, cy: AXIS - 12 - row * ROW_H };
			});
	});

	function step1(dir: -1 | 1) {
		const next =
			dir === 1 ? epochDays.find((d) => d > day) : [...epochDays].reverse().find((d) => d < day);
		if (next !== undefined) day = next;
	}

	// Drag and click both scrub; a pointerdown on an event marker selects it instead.
	let svg: SVGSVGElement | undefined = $state();
	let dragging = $state(false);

	function scrubTo(clientX: number) {
		if (!svg) return;
		day = snap(dayAt(clientX - svg.getBoundingClientRect().left));
	}
	function down(e: PointerEvent) {
		const id = (e.target as Element).getAttribute('data-event');
		if (id) {
			onselectevent?.(id);
			return;
		}
		dragging = true;
		(e.currentTarget as SVGSVGElement).setPointerCapture(e.pointerId);
		scrubTo(e.clientX);
	}
	function move(e: PointerEvent) {
		if (dragging) scrubTo(e.clientX);
	}
	function up(e: PointerEvent) {
		dragging = false;
		(e.currentTarget as SVGSVGElement).releasePointerCapture(e.pointerId);
	}

	function key(e: KeyboardEvent) {
		const big = e.shiftKey ? 365 : 1;
		const moves: Record<string, () => void> = {
			ArrowLeft: () => (day = clamp(day - big)),
			ArrowRight: () => (day = clamp(day + big)),
			ArrowDown: () => (day = clamp(day - big)),
			ArrowUp: () => (day = clamp(day + big)),
			PageDown: () => step1(-1),
			PageUp: () => step1(1),
			Home: () => (day = 0),
			End: () => (day = maxDay)
		};
		const fn = moves[e.key];
		if (!fn) return;
		e.preventDefault();
		fn();
	}

	// Playback walks the changes of control rather than sweeping the calendar:
	// the interesting frames are the ones where the map actually redraws.
	let playing = $state(false);
	$effect(() => {
		if (!playing) return;
		const id = setInterval(() => {
			const next = epochDays.find((d) => d > day);
			if (next === undefined) playing = false;
			else day = next;
		}, 1100);
		return () => clearInterval(id);
	});
	function play() {
		if (!playing && day >= maxDay) day = 0;
		playing = !playing;
	}
</script>

<div class="timeline">
	<div class="buttons">
		<button onclick={() => step1(-1)} title={ui('timeline.prev')} aria-label={ui('timeline.prev')}>
			&#9664;&#9664;
		</button>
		<button
			class="play"
			onclick={play}
			title={ui(playing ? 'timeline.pause' : 'timeline.play')}
			aria-label={ui(playing ? 'timeline.pause' : 'timeline.play')}
			aria-pressed={playing}
		>
			{playing ? '❙❙' : '▶'}
		</button>
		<button onclick={() => step1(1)} title={ui('timeline.next')} aria-label={ui('timeline.next')}>
			&#9654;&#9654;
		</button>
	</div>

	<div
		class="track"
		bind:clientWidth={width}
		role="slider"
		tabindex="0"
		aria-label={ui('timeline.date')}
		aria-valuemin={0}
		aria-valuemax={maxDay}
		aria-valuenow={day}
		aria-valuetext={prettyDate(date)}
		onkeydown={key}
	>
		{#if width > 0}
			<svg
				bind:this={svg}
				viewBox="0 0 {width} {H}"
				width={width}
				height={H}
				role="presentation"
				aria-hidden="true"
				class:dragging
				onpointerdown={down}
				onpointermove={move}
				onpointerup={up}
				onpointercancel={up}
			>
				<!-- 1. the years -->
				<line class="axis" x1={PAD} y1={AXIS} x2={width - PAD} y2={AXIS} />
				{#each ticks as t (t.y)}
					<line class="tick" x1={t.x} y1={AXIS} x2={t.x} y2={AXIS + 5} />
					<text class="tick-label" x={t.x} y={AXIS + 18}>{t.y}</text>
				{/each}

				<!-- 2. one mark per change of control, so the dense decades are visible -->
				<g class="epochs">
					{#each epochDays as d (d)}
						<line x1={x(d)} y1={AXIS - 7} x2={x(d)} y2={AXIS} />
					{/each}
				</g>

				<!-- 3. events, sized by significance -->
				<g class="events">
					{#each marks as e (e.id)}
						<circle
							class="event"
							class:muted={e.muted}
							class:selected={selectedId === e.id}
							data-event={e.id}
							cx={e.cx}
							cy={e.cy}
							r={e.r}
						>
							<title>{e.title}</title>
						</circle>
					{/each}
				</g>

				<!-- 4. where we are -->
				<g class="handle" style:transform="translateX({x(day)}px)">
					<line y1={AXIS - 12 - ROWS * ROW_H} y2={AXIS + 5} />
					<circle cy={AXIS} r="4.5" />
				</g>
			</svg>
		{/if}
	</div>

	<span class="readout">{year(date)}</span>
</div>

<style>
	.timeline {
		display: flex;
		align-items: center;
		gap: 10px;
	}
	.buttons {
		display: flex;
		gap: 4px;
		flex: none;
	}
	button {
		font: inherit;
		font-size: 0.8rem;
		line-height: 1;
		background: var(--panel);
		color: var(--ink);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 7px 9px;
		cursor: pointer;
	}
	button:hover {
		border-color: var(--accent);
		color: var(--accent);
	}
	.play[aria-pressed='true'] {
		border-color: var(--accent);
		color: var(--accent);
	}

	.track {
		flex: 1;
		min-width: 0;
		border-radius: var(--radius);
	}
	.track:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
	}
	svg {
		display: block;
		cursor: pointer;
		touch-action: none;
	}
	svg.dragging {
		cursor: grabbing;
	}

	.axis {
		stroke: var(--rule);
		stroke-width: 1;
	}
	.tick {
		stroke: var(--rule);
		stroke-width: 1;
	}
	.tick-label {
		font-family: var(--mono);
		font-size: 10px;
		fill: var(--ink-soft);
		text-anchor: middle;
	}
	.epochs line {
		stroke: var(--coast);
		stroke-width: 1;
		opacity: 0.55;
	}
	.event {
		fill: var(--panel);
		stroke: var(--ink-soft);
		stroke-width: 1.2;
		cursor: pointer;
		transition: fill 120ms ease;
	}
	/* Pushed back, never removed: the reader should still see that something was
	   happening then, only not there. */
	.event.muted {
		stroke: var(--rule);
		opacity: 0.55;
	}
	.event.muted:hover {
		opacity: 1;
	}
	.event:hover {
		fill: var(--accent);
		stroke: var(--accent);
	}
	.event.selected {
		fill: var(--accent);
		stroke: var(--accent);
	}
	.handle line {
		stroke: var(--accent);
		stroke-width: 1.5;
	}
	.handle circle {
		fill: var(--accent);
		stroke: var(--panel);
		stroke-width: 1.5;
	}

	.readout {
		flex: none;
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.95rem;
		min-width: 4ch;
		text-align: right;
	}

	@media (max-width: 560px) {
		.timeline {
			flex-wrap: wrap;
		}
		.track {
			order: -1;
			flex-basis: 100%;
		}
	}
</style>
