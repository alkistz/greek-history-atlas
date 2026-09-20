<script lang="ts">
	import { polityLabels } from './labels';
	import { t } from './lang.svelte';
	import { ui } from './ui';
	import MapTooltip from './MapTooltip.svelte';
	import { angleFor, HATCH, STIPPLE } from './patterns';
	import { buildShapes, pathOf, project, REF_H, REF_W, VIEWBOX, type FrameId } from './projection';
	import { changedAtoms, heldAtoms, resolveOn, rowsFor, type Layered } from './resolve';
	import type { AtomFeature, ControlRow, LandFeature, Meta, Pin } from './types';

	interface Props {
		atoms: AtomFeature[];
		land: LandFeature;
		meta: Meta;
		control: ControlRow[];
		date: string;
		frame?: FrameId;
		/** atom id to brighten */
		highlight?: string | null;
		/** atoms outside the current region filter; veiled rather than recoloured */
		dimmed?: Set<string>;
		/** a click on a territory, for region filtering */
		onpick?: (atom: string) => void;
		pins?: Pin[];
		showOccupation?: boolean;
		showLabels?: boolean;
		/** hover tooltip and change flashes; off for a static mini-map */
		interactive?: boolean;
	}

	let {
		atoms,
		land,
		meta,
		control,
		date,
		frame = 'greece',
		highlight = null,
		dimmed,
		onpick,
		pins = [],
		showOccupation = true,
		showLabels = true,
		interactive = true
	}: Props = $props();

	// Unique per instance, so two maps on one page never share a pattern id.
	const uid = $props.id();

	const colour = $derived(new Map(meta.polities.map((p) => [p.id, p.colour ?? 'transparent'])));
	const nameOf = $derived(new Map(meta.polities.map((p) => [p.id, t(p.name)])));
	// `state` is the unmarked case; naming it on every row would be noise. An empire,
	// a protectorate or an autonomy is the thing a reader cannot infer from a colour.
	const kindOf = $derived(
		new Map(meta.polities.filter((p) => p.kind !== 'state').map((p) => [p.id, p.kind]))
	);
	const propsOf = $derived(new Map(atoms.map((f) => [f.properties.id, f.properties])));
	const atomName = $derived(new Map(atoms.map((f) => [f.properties.id, t(f.properties.name)])));
	const instrumentName = $derived(new Map(meta.instruments.map((i) => [i.id, t(i.name)])));
	// Naming the region in the tooltip is how a reader learns the vocabulary — at
	// the exact spot where clicking would filter by it.
	const regionName = $derived(
		new Map(meta.regions.flatMap((r) => r.atoms.map((a) => [a, t(r.name)] as const)))
	);

	const shapes = $derived(buildShapes(atoms, frame));
	const landPath = $derived(pathOf(land.geometry, frame));
	const layered = $derived(resolveOn(control, date));
	const held = $derived(heldAtoms(layered));

	const overlayPolities = $derived([
		...new Set([...layered.occupied.keys(), ...layered.administered.keys()])
	]);
	const labels = $derived(showLabels ? polityLabels(layered, atoms, shapes, meta.polities) : []);
	const placed = $derived(
		pins
			.map((p) => ({ ...p, xy: project(p.lon, p.lat, frame) }))
			.filter((p): p is Pin & { xy: [number, number] } => p.xy !== null)
	);

	// Patterns are in viewBox units but strokes are in screen pixels. Scale the
	// tiles by the rendered size so a hatch is 7px on a phone and on a desktop.
	let width = $state(0);
	const k = $derived(width ? REF_W / width : 1);

	// A change of holder flashes the atom's outline for a moment.
	let flashing = $state(new Set<string>());
	let previous: Layered | null = null;
	$effect(() => {
		const next = layered;
		const changed = previous && interactive ? changedAtoms(previous, next) : new Set<string>();
		previous = next;
		if (!changed.size) return;
		flashing = changed;
		const t = setTimeout(() => (flashing = new Set()), 700);
		return () => clearTimeout(t);
	});

	// One delegated handler on the sovereignty layer, reading data-atom off the path.
	let wrapper: HTMLDivElement | undefined = $state();
	let tip = $state<{ atom: string; x: number; y: number } | null>(null);
	function move(e: PointerEvent) {
		if (!interactive || !wrapper) return;
		const atom = (e.target as Element).getAttribute('data-atom');
		if (!atom) {
			tip = null;
			return;
		}
		const r = wrapper.getBoundingClientRect();
		tip = { atom, x: e.clientX - r.left, y: e.clientY - r.top };
	}
	// Keyboard and screen-reader access to what the pointer gets. The map is one
	// tab stop; the arrow keys then walk the atoms in reading order.
	const focusOrder = $derived.by(() => {
		const ids = [...held].filter((id) => shapes.has(id));
		return ids.sort((a, b) => {
			const [ax, ay] = shapes.get(a)!.centroid;
			const [bx, by] = shapes.get(b)!.centroid;
			// Banded, so a chain of islands reads left to right rather than by latitude.
			return Math.floor(ay / 60) - Math.floor(by / 60) || ax - bx;
		});
	});
	let cursor = $state(0);

	function labelFor(id: string): string {
		const holder = layered.sovereign.get(id);
		const name = atomName.get(id) ?? id;
		return holder ? `${name}, ${nameOf.get(holder) ?? holder}` : name;
	}

	/** Attributes that only make sense on the live map, not on a static mini-map. */
	function reach(id: string) {
		if (!interactive) return {};
		return {
			role: 'button',
			tabindex: focusOrder[cursor] === id ? 0 : -1,
			'aria-label': labelFor(id),
			onclick: () => onpick?.(id),
			onkeydown: walk
		};
	}

	function showAt(id: string) {
		if (!interactive) return;
		const shape = shapes.get(id);
		if (!shape) return;
		const scale = width ? width / REF_W : 1;
		tip = { atom: id, x: shape.centroid[0] * scale, y: shape.centroid[1] * scale };
		const i = focusOrder.indexOf(id);
		if (i >= 0) cursor = i;
	}

	function walk(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			tip = null;
			return;
		}
		// role="button" promises Enter and Space work; browsers do not deliver that
		// for anything but a real <button>, so honour it here.
		if (e.key === 'Enter' || e.key === ' ') {
			const id = (e.currentTarget as Element).getAttribute('data-atom');
			if (id) {
				e.preventDefault();
				onpick?.(id);
			}
			return;
		}
		const dir = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
		if (dir === undefined || !wrapper || !focusOrder.length) return;
		e.preventDefault();
		const i = Math.min(Math.max(cursor + dir, 0), focusOrder.length - 1);
		wrapper.querySelector<SVGPathElement>(`[data-atom="${CSS.escape(focusOrder[i])}"]`)?.focus();
	}

	/** The region, unless it just repeats the territory's own name. */
	function regionLabel(atom: string): string | null {
		const region = regionName.get(atom);
		return region && region !== atomName.get(atom) ? region : null;
	}

	const tipRows = $derived(
		tip
			? rowsFor(control, tip.atom, date).map((r) => ({
					kind: r.kind,
					polity: nameOf.get(r.polity) ?? r.polity,
					since: r.from,
					instrument: r.instrument ? (instrumentName.get(r.instrument) ?? null) : null,
					note: r.note,
					polityKind: kindOf.get(r.polity) ?? null
				}))
			: []
	);

	// The map's spoken description, for a reader who cannot see it.
	const summary = $derived.by(() => {
		const named = (ids: Iterable<string>) =>
			[...ids].map((p) => nameOf.get(p) ?? p).join(', ');
		const sov = new Set(layered.sovereign.values());
		const bits = [ui('map.sovereignty', { polities: named(sov) })];
		const occ = [...layered.occupied.keys()];
		if (occ.length) bits.push(ui('map.occupied', { polities: named(occ) }));
		for (const p of layered.insurgent.keys()) {
			bits.push(ui('map.revolt', { polity: nameOf.get(p) ?? p }));
		}
		return bits.join('. ') + '.';
	});
</script>

<div class="wrap" bind:this={wrapper} bind:clientWidth={width}>
	<svg viewBox={VIEWBOX} class="atlas" role="img" aria-labelledby="{uid}-t" aria-describedby="{uid}-d">
		<title id="{uid}-t">{ui('map.title', { date })}</title>
		<desc id="{uid}-d">{summary}</desc>

		<defs>
			{#each overlayPolities as pid (pid)}
				<pattern
					id="{uid}-hatch-{pid}"
					patternUnits="userSpaceOnUse"
					width={HATCH.size}
					height={HATCH.size}
					patternTransform="rotate({angleFor(pid)}) scale({k})"
				>
					<!-- No background rect: the sovereign fill must read through. That
					     transparency is the entire mechanism of the two-layer model. -->
					<line x1="0" y1="0" x2="0" y2={HATCH.size} stroke={colour.get(pid)} stroke-width={HATCH.stroke} />
				</pattern>
			{/each}
			{#each [...layered.insurgent.keys()] as pid (pid)}
				<pattern
					id="{uid}-stipple-{pid}"
					patternUnits="userSpaceOnUse"
					width={STIPPLE.size}
					height={STIPPLE.size}
					patternTransform="scale({k})"
				>
					<circle cx={STIPPLE.size * 0.28} cy={STIPPLE.size * 0.28} r={STIPPLE.r} fill={colour.get(pid)} />
					<circle cx={STIPPLE.size * 0.78} cy={STIPPLE.size * 0.78} r={STIPPLE.r} fill={colour.get(pid)} />
				</pattern>
			{/each}
		</defs>

		<!-- 0. sea and neighbouring land, at present-day extent, uncoloured -->
		<rect class="sea" width={REF_W} height={REF_H} />
		<path class="land" d={landPath} />

		<!-- 1. sovereignty: the base fill -->
		<g
			class="sovereignty"
			role="group"
			aria-label={ui('map.territories')}
			onpointermove={move}
			onpointerdown={move}
			onpointerleave={() => (tip = null)}
		>
			{#each atoms as f (f.properties.id)}
				{@const id = f.properties.id}
				{@const holder = layered.sovereign.get(id)}
				{#if holder && shapes.has(id)}
					<path
						class="sov"
						class:highlighted={highlight === id}
						data-atom={id}
						{...reach(id)}
						onfocus={() => showAt(id)}
						onblur={() => (tip = null)}
						style:fill={colour.get(holder)}
						d={shapes.get(id)!.d}
					/>
				{/if}
			{/each}
		</g>

		<!-- 2. atom outlines, only where something is drawn -->
		<g class="hairlines">
			{#each atoms as f (f.properties.id)}
				{@const id = f.properties.id}
				{#if held.has(id) && shapes.has(id)}
					<path class="hairline" class:changed={flashing.has(id)} d={shapes.get(id)!.d} />
				{/if}
			{/each}
		</g>

		<!-- 3. occupation, layered ON TOP of sovereignty rather than replacing it -->
		{#if showOccupation}
			<g class="occupation">
				{#each [...layered.occupied] as [pid, ids] (pid)}
					{#each ids as id (id)}
						{#if shapes.has(id)}
							<path class="occ" fill="url(#{uid}-hatch-{pid})" d={shapes.get(id)!.d} />
							<path class="occ-edge" style:stroke={colour.get(pid)} d={shapes.get(id)!.d} />
						{/if}
					{/each}
				{/each}
			</g>
		{/if}

		<!-- 4. administering powers over someone else's sovereignty, or over no one's -->
		<g class="administered">
			{#each [...layered.administered] as [pid, ids] (pid)}
				{#each ids as id (id)}
					{#if shapes.has(id)}
						<path class="adm" fill="url(#{uid}-hatch-{pid})" d={shapes.get(id)!.d} />
					{/if}
				{/each}
			{/each}
		</g>

		<!-- 5. insurgency: stipple and a broken edge, never a flat fill, because
		     there was no frontier to draw -->
		<g class="insurgency">
			{#each [...layered.insurgent] as [pid, ids] (pid)}
				{#each ids as id (id)}
					{#if shapes.has(id)}
						<path class="ins" fill="url(#{uid}-stipple-{pid})" d={shapes.get(id)!.d} />
						<path class="ins-edge" style:stroke={colour.get(pid)} d={shapes.get(id)!.d} />
					{/if}
				{/each}
			{/each}
		</g>

		<!-- 5b. region filter: veil what is out of scope rather than recolour it. The
		     polity palette was chosen against these two land surfaces and must not
		     be disturbed by a filter. -->
		{#if dimmed?.size}
			<g class="veil">
				{#each atoms as f (f.properties.id)}
					{@const id = f.properties.id}
					{#if dimmed.has(id) && held.has(id) && shapes.has(id)}
						<path d={shapes.get(id)!.d} />
					{/if}
				{/each}
			</g>
		{/if}

		<!-- 6. names of the sovereign powers -->
		<g class="labels" aria-hidden="true">
			{#each labels as l (l.polity)}
				<text class="label {l.tier}" style:transform="translate({l.x}px, {l.y}px)">{l.text}</text>
			{/each}
		</g>

		<!-- 7. places -->
		<g class="pins" aria-hidden="true">
			{#each placed as p (p.id)}
				<circle class="pin" cx={p.xy[0]} cy={p.xy[1]} r="4" />
				<text class="pin-label" x={p.xy[0] + 7} y={p.xy[1] + 4}>{p.label}</text>
			{/each}
		</g>
	</svg>

	{#if tip}
		<MapTooltip
			x={tip.x}
			y={tip.y}
			flip={tip.x > width * 0.6}
			title={atomName.get(tip.atom) ?? tip.atom}
			region={regionLabel(tip.atom)}
			rows={tipRows}
			areaKm2={propsOf.get(tip.atom)?.area_km2 ?? null}
			external={propsOf.get(tip.atom)?.external ?? false}
		/>
	{/if}
</div>

<style>
	.wrap {
		position: relative;
	}
	.atlas {
		width: 100%;
		height: auto;
		display: block;
		border-radius: var(--radius);
	}
	path {
		vector-effect: non-scaling-stroke;
	}

	.sea {
		fill: var(--sea);
	}
	.land {
		fill: var(--land);
		stroke: var(--coast);
		stroke-width: 0.8;
	}

	.sov {
		stroke: none;
		transition: fill 180ms ease;
	}
	.sov.highlighted {
		filter: brightness(1.18);
	}
	/* An outline on an SVG path is drawn round its bounding box, so the UA ring
	   reads as a black rectangle over the sea. Suppress it and mark focus on the
	   shape itself. */
	.sov:focus {
		outline: none;
	}
	.sov:focus-visible {
		stroke: var(--accent);
		stroke-width: 2;
	}

	.hairlines {
		pointer-events: none;
	}
	.hairline {
		fill: none;
		stroke: var(--hairline);
		stroke-width: 0.5;
		transition: stroke 600ms ease;
	}
	.hairline.changed {
		stroke: var(--accent);
		stroke-width: 1.5;
		transition: none;
	}

	.occupation,
	.administered,
	.insurgency,
	.veil,
	.labels,
	.pins {
		pointer-events: none;
	}
	/* Ground colour, not opacity on the fill: opacity would let the sea read
	   through an island and change its hue rather than recede it. */
	.veil path {
		fill: var(--ground);
		opacity: 0.66;
	}
	.occ-edge {
		fill: none;
		stroke-width: 1.4;
		stroke-dasharray: 5 2.5;
	}
	.adm {
		opacity: 0.75;
	}
	.ins-edge {
		fill: none;
		stroke-width: 1.6;
		stroke-dasharray: 2 4 7 4;
		stroke-linecap: round;
	}

	.label {
		font-family: var(--serif);
		font-variant: small-caps;
		letter-spacing: 0.08em;
		text-anchor: middle;
		fill: var(--label);
		paint-order: stroke;
		stroke: var(--label-halo);
		stroke-width: 3px;
		stroke-linejoin: round;
		transition: transform 300ms ease;
	}
	.label.large {
		font-size: 15px;
	}
	.label.small {
		font-size: 10px;
	}

	.pin {
		fill: var(--accent);
		stroke: var(--label-halo);
		stroke-width: 1.5;
	}
	.pin-label {
		font-family: var(--sans);
		font-size: 10px;
		fill: var(--label);
		paint-order: stroke;
		stroke: var(--label-halo);
		stroke-width: 3px;
	}

	@media (max-width: 480px) {
		.labels {
			display: none;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.sov,
		.hairline,
		.label {
			transition: none;
		}
	}
</style>
