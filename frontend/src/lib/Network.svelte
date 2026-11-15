<!--
	The figure graph, laid out by force.

	The layout runs to completion before anything is drawn rather than animating
	in: a settled picture is what a reader compares across filters, and d3-force's
	default random source is seeded, so the same input gives the same picture.
	A weak pull on x by the year a figure first acts makes the two centuries read
	left to right, so a cluster's place on the page says when it was.

	Every node is a link to the figure's page. Hover or focus lifts a figure and
	its neighbours and dims the rest; nothing here is state the URL needs.
-->
<script lang="ts">
	import {
		forceCollide,
		forceLink,
		forceManyBody,
		forceSimulation,
		forceX,
		forceY,
		type SimulationLinkDatum,
		type SimulationNodeDatum
	} from 'd3-force';
	import { num, t } from './lang.svelte';
	import type { NetworkEdge, NetworkNode, Polity } from './types';
	import { term, ui } from './ui';

	interface Props {
		nodes: NetworkNode[];
		/** already filtered; `weight` is the shared events that survive the filter */
		edges: (NetworkEdge & { weight: number })[];
		polities: Polity[];
		/** the id to ring, from `?focus=` on the page */
		focus?: string | null;
		/** the period on the page, so time runs across the figures shown, not the whole corpus */
		range?: [string, string | null] | null;
	}
	let { nodes, edges, polities, focus = null, range = null }: Props = $props();

	type SimNode = NetworkNode & SimulationNodeDatum & { r: number };
	type SimEdge = SimulationLinkDatum<SimNode> & {
		weight: number;
		tie: boolean;
	};

	const W = 960;
	const H = 700;
	const PAD = 24;

	const radius = (n: NetworkNode) => 4 + 1.6 * Math.sqrt(n.events.length);

	// Where on the page a figure's time sits: first event, else birth, else the middle.
	const span = $derived.by(() => {
		const years = nodes.map(firstYear).filter((y): y is number => y !== null);
		return years.length ? [Math.min(...years), Math.max(...years)] : [1821, 2023];
	});
	function firstYear(n: NetworkNode): number | null {
		const inRange = (iso: string) =>
			range === null || (range[0] <= iso && (range[1] === null || iso < range[1]));
		const d = n.events.find((e) => inRange(e.date))?.date ?? n.events[0]?.date ?? n.born;
		return d ? Number(d.slice(0, 4)) : null;
	}
	function xFor(n: NetworkNode): number {
		const y = firstYear(n);
		if (y === null || span[1] === span[0]) return W / 2;
		return PAD + 60 + ((y - span[0]) / (span[1] - span[0])) * (W - 2 * (PAD + 60));
	}

	const layout = $derived.by(() => {
		const ns: SimNode[] = nodes.map((n) => ({ ...n, r: radius(n) }));
		const byId = new Map(ns.map((n) => [n.id, n]));
		const es: SimEdge[] = edges
			.filter((e) => byId.has(e.source) && byId.has(e.target))
			.map((e) => ({
				source: e.source,
				target: e.target,
				weight: e.weight,
				tie: e.relations.length > 0
			}));
		forceSimulation(ns)
			.force(
				'link',
				forceLink<SimNode, SimEdge>(es)
					.id((d) => d.id)
					.distance((d) => 44 + 60 / (d.weight + 1))
					.strength((d) => Math.min(1, 0.2 + 0.2 * d.weight))
			)
			.force('charge', forceManyBody().strength(-220))
			.force('x', forceX<SimNode>((d) => xFor(d)).strength(0.1))
			.force('y', forceY(H / 2).strength(0.05))
			.force(
				'collide',
				forceCollide<SimNode>((d) => d.r + 9)
			)
			.stop()
			.tick(320);
		for (const n of ns) {
			n.x = Math.max(PAD + n.r, Math.min(W - PAD - n.r, n.x ?? W / 2));
			n.y = Math.max(PAD + n.r, Math.min(H - PAD - n.r, n.y ?? H / 2));
		}
		return { ns, es };
	});

	// Colour by the state a figure served. Greece is the default and is drawn in
	// the kingdom's blue, as on the map; a polity that is never drawn there has
	// no colour and takes the soft ink instead.
	const polity = (id: string | null) => polities.find((p) => p.id === (id ?? 'gr-kingdom'));
	const colour = (n: NetworkNode) => polity(n.polity)?.colour ?? 'var(--ink-soft)';
	const legend = $derived.by(() => {
		const seen = new Map<string, Polity | undefined>();
		for (const n of nodes) seen.set(n.polity ?? 'gr-kingdom', polity(n.polity));
		return [...seen.values()].filter((p): p is Polity => !!p);
	});

	let hovered = $state<string | null>(null);
	const lifted = $derived(hovered ?? focus);
	const near = $derived.by(() => {
		const out = new Set<string>();
		if (!lifted) return out;
		out.add(lifted);
		for (const e of layout.es) {
			const a = (e.source as SimNode).id;
			const b = (e.target as SimNode).id;
			if (a === lifted) out.add(b);
			if (b === lifted) out.add(a);
		}
		return out;
	});
	const dim = (id: string) => lifted !== null && !near.has(id);
	// Always-on labels are rationed: the 1910s are dense, and every name there
	// would sit on another. Hovering any figure names its neighbourhood.
	const labelled = (n: SimNode) =>
		nodes.length <= 24 || n.events.length >= 6 || near.has(n.id);

	// The tooltip follows the pointer inside the figure's own box.
	let tip = $state<{ x: number; y: number; node: SimNode } | null>(null);
	let box: HTMLDivElement | undefined = $state();
	function enter(n: SimNode, ev: PointerEvent | FocusEvent) {
		hovered = n.id;
		const rect = box?.getBoundingClientRect();
		if (ev instanceof PointerEvent && rect) {
			tip = { x: ev.clientX - rect.left, y: ev.clientY - rect.top, node: n };
		} else if (rect && box) {
			// keyboard focus: pin the tip to the node itself
			const sx = rect.width / W;
			tip = { x: (n.x ?? 0) * sx, y: (n.y ?? 0) * sx, node: n };
		}
	}
	function leave() {
		hovered = null;
		tip = null;
	}
	const events = (n: number) =>
		n === 1 ? ui('network.tip.events.one') : ui('network.tip.events', { n });
</script>

<div class="wrap" bind:this={box}>
	<svg viewBox="0 0 {W} {H}" role="img" aria-label={ui('network.aria')}>
		<g class="edges">
			{#each layout.es as e ((e.source as SimNode).id + (e.target as SimNode).id)}
				{@const a = e.source as SimNode}
				{@const b = e.target as SimNode}
				{@const faded = dim(a.id) || dim(b.id)}
				{#if e.weight > 0}
					<line
						x1={a.x}
						y1={a.y}
						x2={b.x}
						y2={b.y}
						class="shared"
						class:faded
						stroke-width={0.8 + 0.7 * e.weight}
					/>
				{/if}
				{#if e.tie}
					<line x1={a.x} y1={a.y} x2={b.x} y2={b.y} class="tie" class:faded />
				{/if}
			{/each}
		</g>
		<g class="nodes">
			{#each layout.ns as n (n.id)}
				<a
					href="/figures/{n.id}"
					class="node"
					class:faded={dim(n.id)}
					class:focus={n.id === focus}
					onpointerenter={(ev) => enter(n, ev)}
					onpointermove={(ev) => enter(n, ev)}
					onpointerleave={leave}
					onfocus={(ev) => enter(n, ev)}
					onblur={leave}
				>
					<title>{t(n.name)}</title>
					<circle cx={n.x} cy={n.y} r={n.r} fill={colour(n)} />
					{#if n.id === focus}
						<circle cx={n.x} cy={n.y} r={n.r + 4} class="ring" />
					{/if}
					{#if labelled(n)}
						<text x={(n.x ?? 0) + n.r + 3} y={(n.y ?? 0) + 3.5}>{t(n.name)}</text>
					{/if}
				</a>
			{/each}
		</g>
	</svg>

	{#if tip}
		<div
			class="tip"
			role="status"
			style:left="{tip.x}px"
			style:top="{tip.y}px"
			class:flip={tip.x > (box?.clientWidth ?? W) * 0.6}
		>
			<div class="name">{t(tip.node.name)}</div>
			<div class="meta">
				{tip.node.roles.map((r) => term('role.figure', r)).join(' · ')}
				{#if polity(tip.node.polity)}
					· {t(polity(tip.node.polity)!.name)}
				{/if}
			</div>
			<div class="meta">
				{events(tip.node.events.length)} ·
				{ui('network.tip.degree', { n: tip.node.degree })} ·
				{ui('network.tip.between', { n: num(tip.node.betweenness, 2) })}
			</div>
		</div>
	{/if}

	<ul class="legend" aria-label={ui('network.legend')}>
		{#each legend as p (p.id)}
			<li><span class="swatch" style:background={p.colour ?? 'var(--ink-soft)'}></span>{t(p.name)}</li>
		{/each}
		<li><span class="line shared"></span>{ui('network.legend.shared')}</li>
		<li><span class="line tie"></span>{ui('network.legend.tie')}</li>
	</ul>
</div>

<style>
	.wrap {
		position: relative;
		background: var(--panel);
		border: 1px solid var(--ink);
		padding: 8px;
	}
	svg {
		display: block;
		width: 100%;
		height: auto;
		font-family: var(--sans);
	}
	/* The accent is ink, the same as the text, so the two kinds of edge differ in
	   weight rather than colour: shared events are hairlines, recorded ties are rules. */
	line.shared {
		stroke: var(--ink-soft);
		stroke-opacity: 0.35;
		stroke-linecap: round;
		transition: stroke-opacity 120ms ease;
	}
	line.tie {
		stroke: var(--ink);
		stroke-width: 2;
		stroke-opacity: 0.85;
		transition: stroke-opacity 120ms ease;
	}
	line.faded {
		stroke-opacity: 0.08;
	}
	.node {
		cursor: pointer;
		transition: opacity 120ms ease;
	}
	.node circle {
		stroke: var(--panel);
		stroke-width: 1.2;
	}
	.node.faded {
		opacity: 0.18;
	}
	.node:focus-visible {
		outline: none;
	}
	.node:focus-visible circle {
		stroke: var(--ink);
		stroke-width: 2.5;
	}
	.ring {
		fill: none;
		stroke: var(--ink);
		stroke-width: 2;
	}
	text {
		font-size: 11px;
		fill: var(--ink);
		paint-order: stroke;
		stroke: var(--panel);
		stroke-width: 3px;
		stroke-linejoin: round;
		pointer-events: none;
	}
	.tip {
		position: absolute;
		transform: translate(14px, 14px);
		max-width: 26ch;
		padding: 6px 10px;
		background: var(--panel);
		border: 1px solid var(--ink);
		font-size: 0.82rem;
		pointer-events: none;
		z-index: 2;
	}
	.tip.flip {
		transform: translate(calc(-100% - 14px), 14px);
	}
	.tip .name {
		font-family: var(--serif);
		font-weight: 600;
	}
	.tip .meta {
		color: var(--ink-soft);
	}
	.legend {
		list-style: none;
		display: flex;
		flex-wrap: wrap;
		gap: 4px 14px;
		margin: 6px 4px 0;
		padding: 0;
		font-size: 0.78rem;
		color: var(--ink-soft);
	}
	.legend li {
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	.swatch {
		width: 10px;
		height: 10px;
		border-radius: 50%;
	}
	.line {
		width: 18px;
		height: 0;
		border-top: 1px solid var(--ink-soft);
	}
	.line.tie {
		border-top: 2px solid var(--ink);
	}
	@media (prefers-reduced-motion: reduce) {
		line,
		.node {
			transition: none;
		}
	}
</style>
