<!--
	The front page's picture: the map stepping through every date on which control
	changed, from the first to the last, and starting over.

	It steps through the epochs rather than running a clock, because between two
	epochs nothing moves, and two centuries at an even speed would spend most of
	the loop on a still map. A reader who prefers reduced motion gets the last
	date, still, with the play button to start it themselves. Clicking the map
	opens the atlas on the date it is showing.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { prefersReducedMotion } from 'svelte/motion';
	import Atlas from './Atlas.svelte';
	import { num } from './lang.svelte';
	import { greekArea, resolveOn } from './resolve';
	import { year } from './time';
	import { ui } from './ui';
	import { atlasHref } from './viewstate';
	import type { AtomFeature, ControlRow, LandFeature, Meta } from './types';

	interface Props {
		atoms: AtomFeature[];
		land: LandFeature;
		meta: Meta;
		control: ControlRow[];
	}
	let { atoms, land, meta, control }: Props = $props();

	const STEP_MS = 900;
	/** the last frame is today's map; it is held long enough to be read */
	const HOLD_MS = 3500;

	const epochs = $derived(meta.epochs);
	let index = $state(0);
	let playing = $state(false);
	let visible = $state(true);
	let el: HTMLElement;

	const date = $derived(epochs[index] ?? meta.range.from);
	const km2 = $derived(greekArea(resolveOn(control, date).sovereign, atoms));

	onMount(() => {
		if (prefersReducedMotion.current) index = epochs.length - 1;
		else playing = true;
		// Off screen, the loop stops; it picks up where it was on the way back.
		const io = new IntersectionObserver(([e]) => (visible = e.isIntersecting));
		io.observe(el);
		return () => io.disconnect();
	});

	$effect(() => {
		if (!playing || !visible) return;
		const last = index >= epochs.length - 1;
		const id = setTimeout(
			() => (index = last ? 0 : index + 1),
			last ? HOLD_MS : STEP_MS
		);
		return () => clearTimeout(id);
	});
</script>

<figure class="hero-map" bind:this={el}>
	<a class="map" href={atlasHref({ on: date })} aria-label={ui('home.map.open', { year: year(date) })}>
		<Atlas {atoms} {land} {meta} {control} {date} interactive={false} showLabels={false} />
	</a>
	<!-- The progress through the two centuries, as a hairline under the map. -->
	<div class="progress" aria-hidden="true">
		<span style:width="{(index / Math.max(epochs.length - 1, 1)) * 100}%"></span>
	</div>
	<figcaption>
		<span class="year">{year(date)}</span>
		<!-- Before the first sovereign government there is a revolt on the map and
		     no state under it; nought km² would read as a broken figure. -->
		<span class="area">{km2 > 0 ? ui('home.map.area', { km2: num(km2) }) : ui('home.map.nostate')}</span>
		<button
			type="button"
			class="play"
			onclick={() => (playing = !playing)}
			aria-pressed={playing}
			aria-label={ui(playing ? 'home.map.pause' : 'home.map.play')}
			title={ui(playing ? 'home.map.pause' : 'home.map.play')}
		>
			{#if playing}
				<svg viewBox="0 0 12 12" aria-hidden="true"><rect x="2" y="1.5" width="2.8" height="9" rx="0.8" /><rect x="7.2" y="1.5" width="2.8" height="9" rx="0.8" /></svg>
			{:else}
				<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3 1.6v8.8a.6.6 0 0 0 .9.5l7-4.4a.6.6 0 0 0 0-1L3.9 1.1a.6.6 0 0 0-.9.5z" /></svg>
			{/if}
		</button>
	</figcaption>
</figure>

<style>
	.hero-map {
		position: relative;
		margin: 0;
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
		overflow: hidden;
		background: var(--sea);
		box-shadow: var(--elev-1);
	}
	.map {
		display: block;
		cursor: pointer;
	}
	.map :global(.wrap) {
		border-radius: 0;
	}
	.map:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: -2px;
	}
	figcaption {
		position: absolute;
		left: 10px;
		bottom: 12px;
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 6px 8px 6px 12px;
		background: color-mix(in srgb, var(--panel) 86%, transparent);
		backdrop-filter: blur(6px);
		-webkit-backdrop-filter: blur(6px);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
	}
	.year {
		font-family: var(--serif);
		font-size: 1.6rem;
		font-weight: 600;
		line-height: 1;
		font-variant-numeric: tabular-nums;
		min-width: 4ch;
	}
	.area {
		font-size: 0.82rem;
		color: var(--ink-soft);
		font-variant-numeric: tabular-nums;
		line-height: 1.2;
	}
	.play {
		display: grid;
		place-items: center;
		width: 30px;
		height: 30px;
		padding: 0;
		border: 1px solid var(--rule);
		border-radius: 50%;
		background: var(--panel);
		color: var(--ink);
		cursor: pointer;
	}
	.play:hover {
		border-color: var(--ink-soft);
	}
	.play:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
	}
	.play svg {
		width: 12px;
		height: 12px;
		fill: currentColor;
	}
	.progress {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0;
		height: 3px;
		background: color-mix(in srgb, var(--panel) 50%, transparent);
	}
	.progress span {
		display: block;
		height: 100%;
		background: var(--accent);
		transition: width 300ms linear;
	}
	@media (prefers-reduced-motion: reduce) {
		.progress span {
			transition: none;
		}
	}
</style>
