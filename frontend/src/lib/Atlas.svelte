<script lang="ts">
	import { untrack } from 'svelte';
	import { cubicOut } from 'svelte/easing';
	import { prefersReducedMotion, Tween } from 'svelte/motion';
	import { polityLabels } from './labels';
	import { t } from './lang.svelte';
	import { ui } from './ui';
	import MapTooltip from './MapTooltip.svelte';
	import { angleFor, HATCH, STIPPLE } from './patterns';
	import {
		buildShapes,
		fitRect,
		frameRect,
		pathOf,
		project,
		WORLD,
		type FrameId,
		type Rect
	} from './projection';
	import { changedAtoms, heldAtoms, resolveOn, rowsFor, type Layered } from './resolve';
	import type { AtomFeature, ControlRow, LandFeature, Meta, Pin } from './types';

	/** A pin with how it is drawn: the selected one is named, the rest speak on hover. */
	export interface MapPin extends Pin {
		selected?: boolean;
		muted?: boolean;
		/** write the label beside the pin; off, the label is the hover title */
		labelled?: boolean;
	}

	interface Props {
		atoms: AtomFeature[];
		land: LandFeature;
		meta: Meta;
		control: ControlRow[];
		date: string;
		/** the preset the camera goes to; the reader may then move off it */
		frame?: FrameId;
		/** atom id to brighten */
		highlight?: string | null;
		/** atoms outside the current region filter; veiled rather than recoloured */
		dimmed?: Set<string>;
		/** a click on a territory, for region filtering */
		onpick?: (atom: string) => void;
		pins?: MapPin[];
		/** a click on a pin */
		onpin?: (id: string) => void;
		showOccupation?: boolean;
		showLabels?: boolean;
		/** hover tooltip, change flashes, zoom and pan; off for a static mini-map */
		interactive?: boolean;
		/** fill the parent's height instead of taking a fixed aspect ratio */
		fill?: boolean;
		/** what the camera is pointed at, in world units, whenever that changes */
		onview?: (view: Rect) => void;
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
		onpin,
		showOccupation = true,
		showLabels = true,
		interactive = true,
		fill = false,
		onview
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

	const shapes = $derived(buildShapes(atoms));
	const landPath = $derived(pathOf(land.geometry));
	const layered = $derived(resolveOn(control, date));
	const held = $derived(heldAtoms(layered));

	const overlayPolities = $derived([
		...new Set([...layered.occupied.keys(), ...layered.administered.keys()])
	]);
	const placed = $derived(
		pins
			.map((p) => ({ ...p, xy: project(p.lon, p.lat) }))
			.filter((p): p is MapPin & { xy: [number, number] } => p.xy !== null)
	);

	// ---- the camera -------------------------------------------------------
	//
	// A centre and a width in world units; the height follows the box the map is
	// drawn in, so the viewBox always matches the element and one scale factor
	// converts between world units and screen pixels.
	let width = $state(0);
	let height = $state(0);
	const DEFAULT_ASPECT = 760 / 680;
	const aspect = $derived(width > 0 && height > 0 ? width / height : DEFAULT_ASPECT);

	interface Cam {
		cx: number;
		cy: number;
		w: number;
	}
	const fitFrame = (f: FrameId, a: number): Cam => {
		const r = fitRect(frameRect(f), a);
		return { cx: r.x + r.w / 2, cy: r.y + r.h / 2, w: r.w };
	};
	// The starting value only; the effect below follows `frame` from then on.
	const cam = new Tween<Cam>(untrack(() => fitFrame(frame, DEFAULT_ASPECT)), {
		duration: 450,
		easing: cubicOut
	});
	const moveOpts = () => ({ duration: prefersReducedMotion.current ? 0 : 450 });

	// Zoom and pan stay inside sensible bounds: no closer than 8× the frame, no
	// further than the whole world, and never so far aside that the land leaves.
	function clampCam(c: Cam): Cam {
		const base = fitFrame(frame, aspect).w;
		const w = Math.min(Math.max(c.w, base / 8), Math.max(base, WORLD.w) * 1.1);
		const h = w / aspect;
		const slackX = w * 0.35;
		const slackY = h * 0.35;
		const loX = WORLD.x + w / 2 - slackX;
		const hiX = WORLD.x + WORLD.w - w / 2 + slackX;
		const loY = WORLD.y + h / 2 - slackY;
		const hiY = WORLD.y + WORLD.h - h / 2 + slackY;
		return {
			cx: loX > hiX ? WORLD.x + WORLD.w / 2 : Math.min(Math.max(c.cx, loX), hiX),
			cy: loY > hiY ? WORLD.y + WORLD.h / 2 : Math.min(Math.max(c.cy, loY), hiY),
			w
		};
	}

	// The reader can move the camera off the frame; a new frame brings it back.
	let offFrame = false;
	let shownFrame: FrameId | null = null;
	$effect(() => {
		const f = frame;
		const a = aspect;
		if (f !== shownFrame) {
			// A new frame: fly to it, or on the first paint simply be there.
			cam.set(fitFrame(f, a), shownFrame === null ? { duration: 0 } : moveOpts());
			shownFrame = f;
			offFrame = false;
		} else if (!offFrame) {
			// The box changed shape under a camera still sitting on its frame: refit
			// silently, so a window resize never leaves half a frame showing.
			cam.set(fitFrame(f, a), { duration: 0 });
		}
	});

	const rectOf = (c: Cam): Rect => {
		const h = c.w / aspect;
		return { x: c.cx - c.w / 2, y: c.cy - h / 2, w: c.w, h };
	};
	const vb = $derived(rectOf(cam.current));
	const view = $derived(rectOf(cam.target));
	$effect(() => {
		onview?.(view);
	});

	// World units per screen pixel: what keeps strokes, hatches, labels and pins
	// the same size on screen at every zoom.
	const k = $derived(width > 0 ? vb.w / width : 1);
	const toScreen = ([x, y]: [number, number]): [number, number] => [
		(x - vb.x) / k,
		(y - vb.y) / k
	];
	const toWorld = (sx: number, sy: number): [number, number] => [vb.x + sx * k, vb.y + sy * k];

	const zoomable = $derived(interactive);

	/** Zoom by `factor` about a screen point, which stays put. */
	function zoomAt(sx: number, sy: number, factor: number, animate = false) {
		const [px, py] = toWorld(sx, sy);
		const c = cam.target;
		const w = c.w / factor;
		const h = w / aspect;
		// The point under the cursor keeps its screen position after the zoom.
		const x = px - (sx / width) * w;
		const y = py - (sy / height) * h;
		cam.set(clampCam({ cx: x + w / 2, cy: y + h / 2, w }), animate ? moveOpts() : { duration: 0 });
		offFrame = true;
	}
	function zoomBy(factor: number) {
		zoomAt(width / 2, height / 2, factor, true);
	}
	function reset() {
		cam.set(fitFrame(frame, aspect), moveOpts());
		offFrame = false;
	}
	function wheel(e: WheelEvent) {
		if (!zoomable) return;
		e.preventDefault();
		const lines = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? 100 : 1;
		const factor = Math.exp(-e.deltaY * lines * 0.0018);
		const r = wrapper!.getBoundingClientRect();
		zoomAt(e.clientX - r.left, e.clientY - r.top, factor);
	}

	// One finger pans, two pinch. A press that moves is a drag, and a drag must not
	// end in a click on whatever territory happens to be under it.
	const pointers = new Map<number, { x: number; y: number }>();
	let dragDist = 0;
	let dragging = $state(false);
	let svgEl: SVGSVGElement | undefined = $state();
	function pointerDown(e: PointerEvent) {
		if (!zoomable) return;
		pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
		if (pointers.size === 1) dragDist = 0;
		// Capture is taken only once this turns into a drag (below): taken here, it
		// would retarget the click that ends a plain press away from the territory
		// under it, and no territory could ever be picked.
	}
	function pointerMove(e: PointerEvent) {
		if (!zoomable || !pointers.has(e.pointerId)) return;
		const prev = pointers.get(e.pointerId)!;
		const next = { x: e.clientX, y: e.clientY };
		if (pointers.size === 1) {
			if (!(e.buttons & 1) && e.pointerType === 'mouse') return;
			const dx = next.x - prev.x;
			const dy = next.y - prev.y;
			dragDist += Math.hypot(dx, dy);
			if (dragDist > 4) {
				if (!dragging) svgEl?.setPointerCapture(e.pointerId);
				dragging = true;
				tip = null;
				const c = cam.target;
				cam.set(clampCam({ cx: c.cx - dx * k, cy: c.cy - dy * k, w: c.w }), { duration: 0 });
				offFrame = true;
			}
		} else if (pointers.size === 2) {
			const [a, b] = [...pointers.entries()].map(([id, p]) => (id === e.pointerId ? next : p));
			const [a0, b0] = [...pointers.values()];
			const before = Math.hypot(a0.x - b0.x, a0.y - b0.y);
			const after = Math.hypot(a.x - b.x, a.y - b.y);
			dragDist += Math.abs(after - before) + 5;
			if (!dragging) for (const id of pointers.keys()) svgEl?.setPointerCapture(id);
			dragging = true;
			tip = null;
			const r = wrapper!.getBoundingClientRect();
			const mid = [(a.x + b.x) / 2 - r.left, (a.y + b.y) / 2 - r.top];
			const mid0 = [(a0.x + b0.x) / 2 - r.left, (a0.y + b0.y) / 2 - r.top];
			// Pan by the midpoint's drift, then zoom about where it now is.
			const c = cam.target;
			cam.set(
				clampCam({ cx: c.cx - (mid[0] - mid0[0]) * k, cy: c.cy - (mid[1] - mid0[1]) * k, w: c.w }),
				{ duration: 0 }
			);
			if (before > 0) zoomAt(mid[0], mid[1], after / before);
		}
		pointers.set(e.pointerId, next);
	}
	function pointerUp(e: PointerEvent) {
		pointers.delete(e.pointerId);
		if (!pointers.size) dragging = false;
	}
	/** Whether the press that just ended was a drag, so the click it ends in is ignored. */
	const wasDrag = () => dragDist > 4;

	// Patterns are in world units but strokes are in screen pixels. Scale the
	// tiles by `k` so a hatch is 7px on a phone, on a desktop, and at any zoom.
	const labels = $derived(
		showLabels ? polityLabels(layered, atoms, shapes, meta.polities, view, 48 * k) : []
	);

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
		if (!interactive || !wrapper || dragging) return;
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
			return Math.floor(ay / 90) - Math.floor(by / 90) || ax - bx;
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
			onclick: () => {
				if (!wasDrag()) onpick?.(id);
			},
			onkeydown: walk
		};
	}

	function showAt(id: string) {
		if (!interactive) return;
		const shape = shapes.get(id);
		if (!shape) return;
		const [x, y] = toScreen(shape.centroid);
		tip = { atom: id, x, y };
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
		if (e.key === '+' || e.key === '=') return zoomBy(1.5);
		if (e.key === '-') return zoomBy(1 / 1.5);
		if (e.key === '0') return reset();
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

	const px = (n: number) => `${n * k}px`;
</script>

<div
	class="wrap"
	class:fill
	class:dragging
	bind:this={wrapper}
	bind:clientWidth={width}
	bind:clientHeight={height}
>
	<svg
		bind:this={svgEl}
		viewBox="{vb.x} {vb.y} {vb.w} {vb.h}"
		class="atlas"
		class:zoomable
		role="img"
		aria-labelledby="{uid}-t"
		aria-describedby="{uid}-d"
		onwheel={wheel}
		onpointerdown={pointerDown}
		onpointermove={pointerMove}
		onpointerup={pointerUp}
		onpointercancel={pointerUp}
		ondblclick={() => zoomable && reset()}
	>
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

		<!-- 0. neighbouring land, at present-day extent, uncoloured; the sea is the background -->
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
					<path class="hairline" d={shapes.get(id)!.d} />
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
		     be disturbed by a filter. Always present, so it can fade. -->
		<g class="veil">
			{#each atoms as f (f.properties.id)}
				{@const id = f.properties.id}
				{#if held.has(id) && shapes.has(id)}
					<path class:on={dimmed?.has(id)} d={shapes.get(id)!.d} />
				{/if}
			{/each}
		</g>

		<!-- 5c. marks drawn above every texture: the territory under the pointer, the
		     one the selected event is about, and the ones that just changed hands -->
		<g class="marks">
			{#each [...flashing] as id (id)}
				{#if shapes.has(id)}<path class="changed" d={shapes.get(id)!.d} />{/if}
			{/each}
			{#if highlight && shapes.has(highlight)}
				<path class="hl-edge" d={shapes.get(highlight)!.d} />
			{/if}
			{#if tip && shapes.has(tip.atom)}
				<path class="hover-edge" d={shapes.get(tip.atom)!.d} />
			{/if}
		</g>

		<!-- 6. names of the sovereign powers -->
		<g class="labels" aria-hidden="true">
			{#each labels as l (l.polity)}
				<text
					class="label {l.tier}"
					style:transform="translate({l.x}px, {l.y}px)"
					style:font-size={px(l.tier === 'large' ? 15 : 10)}
					style:stroke-width={px(3)}>{l.text}</text
				>
			{/each}
		</g>

		<!-- 7. places and events -->
		<g class="pins" class:clickable={!!onpin}>
			{#each placed as p (p.id)}
				<!-- svelte-ignore a11y_click_events_have_key_events -->
				<g
					class="pin"
					class:selected={p.selected}
					class:muted={p.muted}
					role={onpin ? 'button' : undefined}
					aria-label={p.label}
					onclick={() => !wasDrag() && onpin?.(p.id)}
				>
					<title>{p.label}</title>
					<circle
						cx={p.xy[0]}
						cy={p.xy[1]}
						r={(p.selected ? 5.5 : 3.5) * k}
						style:stroke-width={px(1.5)}
					/>
					{#if p.labelled ?? true}
						<text
							class="pin-label"
							x={p.xy[0] + 7 * k}
							y={p.xy[1] + 4 * k}
							style:font-size={px(10)}
							style:stroke-width={px(3)}>{p.label}</text
						>
					{/if}
				</g>
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

	{#if zoomable}
		<div class="zoom" role="group" aria-label={ui('map.reset')}>
			<button type="button" onclick={() => zoomBy(1.6)} aria-label={ui('map.zoomin')} title={ui('map.zoomin')}>+</button>
			<button type="button" onclick={() => zoomBy(1 / 1.6)} aria-label={ui('map.zoomout')} title={ui('map.zoomout')}>−</button>
			<button type="button" onclick={reset} aria-label={ui('map.reset')} title={ui('map.reset')}>⌂</button>
		</div>
	{/if}
</div>

<style>
	.wrap {
		position: relative;
		aspect-ratio: 760 / 680;
		background: var(--sea);
		border-radius: var(--radius);
		overflow: hidden;
	}
	.wrap.fill {
		aspect-ratio: auto;
		height: 100%;
	}
	.atlas {
		width: 100%;
		height: 100%;
		display: block;
	}
	.atlas.zoomable {
		touch-action: none;
		cursor: grab;
	}
	.dragging .atlas.zoomable {
		cursor: grabbing;
	}
	path {
		vector-effect: non-scaling-stroke;
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
		filter: brightness(1.12);
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

	.hairlines,
	.occupation,
	.administered,
	.insurgency,
	.veil,
	.marks,
	.labels {
		pointer-events: none;
	}
	.hairline {
		fill: none;
		stroke: var(--hairline);
		stroke-width: 0.5;
	}
	/* Ground colour, not opacity on the fill: opacity would let the sea read
	   through an island and change its hue rather than recede it. */
	.veil path {
		fill: var(--ground);
		opacity: 0;
		transition: opacity 250ms ease;
	}
	.veil path.on {
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

	.marks path {
		fill: none;
		stroke-linejoin: round;
	}
	.changed {
		stroke: var(--accent);
		stroke-width: 2;
		animation: fade 700ms ease-out forwards;
	}
	@keyframes fade {
		to {
			opacity: 0;
		}
	}
	.hl-edge {
		stroke: var(--accent);
		stroke-width: 2;
	}
	.hover-edge {
		stroke: var(--ink);
		stroke-width: 1.4;
	}

	.label {
		font-family: var(--serif);
		font-variant: small-caps;
		letter-spacing: 0.08em;
		text-anchor: middle;
		fill: var(--label);
		paint-order: stroke;
		stroke: var(--label-halo);
		stroke-linejoin: round;
		transition: transform 300ms ease;
	}

	.pins {
		pointer-events: none;
	}
	.pins.clickable .pin {
		pointer-events: auto;
		cursor: pointer;
	}
	.pin circle {
		fill: var(--accent);
		stroke: var(--label-halo);
		transition: r 150ms ease;
	}
	.pin.muted circle {
		fill: var(--ink-soft);
		opacity: 0.55;
	}
	.pin.selected circle {
		stroke: var(--panel);
	}
	.pins.clickable .pin:hover circle {
		opacity: 1;
		fill: var(--accent);
	}
	.pin-label {
		font-family: var(--sans);
		fill: var(--label);
		paint-order: stroke;
		stroke: var(--label-halo);
	}

	.zoom {
		position: absolute;
		top: 8px;
		right: 8px;
		display: flex;
		flex-direction: column;
		gap: 1px;
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg, 8px);
		overflow: hidden;
		box-shadow: var(--elev-1, 0 1px 4px #0002);
	}
	.zoom button {
		font: inherit;
		font-size: 1rem;
		line-height: 1;
		width: 30px;
		height: 30px;
		padding: 0;
		border: 0;
		background: var(--panel);
		color: var(--ink);
		cursor: pointer;
	}
	.zoom button:hover {
		color: var(--accent);
		background: var(--accent-soft, var(--ground));
	}
	.zoom button:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: -2px;
	}

	@media (max-width: 480px) {
		.labels {
			display: none;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.sov,
		.label,
		.veil path,
		.pin circle {
			transition: none;
		}
		.changed {
			animation: none;
		}
	}
</style>
