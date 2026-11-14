<!--
	The front page's picture: the map stepping through every date on which control
	changed, from the first to the last, and starting over. It fills whatever box
	the page gives it; the page says which part of that box its own words cover.

	It steps through the epochs rather than running a clock, because between two
	epochs nothing moves, and a century and a half at an even speed would spend most of
	the loop on a still map. A reader who prefers reduced motion gets the last
	date, still, with the play button to start it themselves. Clicking the map
	opens the atlas on the date it is showing.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { prefersReducedMotion } from 'svelte/motion';
	import Atlas, { type Insets } from './Atlas.svelte';
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
		/** the parts of the box the page has covered with something else */
		insets?: Insets;
	}
	let { atoms, land, meta, control, insets }: Props = $props();

	const STEP_MS = 900;
	/** the last frame is the map as the atlas leaves it; it is held long enough to be read */
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
		const id = setTimeout(() => (index = last ? 0 : index + 1), last ? HOLD_MS : STEP_MS);
		return () => clearTimeout(id);
	});
</script>

<figure class="hero-map" bind:this={el}>
	<a class="map" href={atlasHref({ on: date })} aria-label={ui('home.map.open', { year: year(date) })}>
		<Atlas
			{atoms}
			{land}
			{meta}
			{control}
			{date}
			{insets}
			interactive={false}
			showLabels={false}
			fill
		/>
	</a>
	<!-- The cartouche: the date and the size of the state on it. -->
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
				<svg viewBox="0 0 12 12" aria-hidden="true"><rect x="2.5" y="2" width="2.5" height="8" /><rect x="7" y="2" width="2.5" height="8" /></svg>
			{:else}
				<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3.5 2v8l6.5-4z" /></svg>
			{/if}
		</button>
	</figcaption>
</figure>

<style>
	.hero-map {
		position: relative;
		height: 100%;
		margin: 0;
	}
	.map {
		display: block;
		height: 100%;
		cursor: pointer;
	}
	.map:focus-visible {
		outline: 2px solid var(--ink);
		outline-offset: -2px;
	}
	figcaption {
		position: absolute;
		z-index: 3;
		right: var(--inset, 20px);
		bottom: 28px;
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 6px 8px 6px 14px;
		background: var(--panel);
		border: 1px solid var(--ink);
	}
	.year {
		font-family: var(--serif);
		font-size: 1.6rem;
		font-weight: 500;
		line-height: 1;
		font-variant-numeric: oldstyle-nums tabular-nums;
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
		width: 28px;
		height: 28px;
		padding: 0;
		border: 1px solid var(--ink);
		background: var(--panel);
		color: var(--ink);
		cursor: pointer;
	}
	.play:hover {
		background: var(--accent-soft);
	}
	.play:focus-visible {
		outline: 2px solid var(--ink);
		outline-offset: 2px;
	}
	.play svg {
		width: 12px;
		height: 12px;
		fill: currentColor;
	}
	@media (max-width: 899px) {
		figcaption {
			top: 12px;
			bottom: auto;
		}
	}
</style>
