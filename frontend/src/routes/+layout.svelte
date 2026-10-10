<script lang="ts">
	import { onNavigate } from '$app/navigation';
	import { navigating, page } from '$app/state';
	import { prefersReducedMotion } from 'svelte/motion';
	import '$lib/fonts.css';
	import DraftNotice from '$lib/DraftNotice.svelte';
	import LangToggle from '$lib/LangToggle.svelte';
	import { ui } from '$lib/ui';
	import ThemeToggle from '$lib/ThemeToggle.svelte';

	let { children } = $props();

	const nav = $derived([
		{ href: '/', label: ui('page.atlas') },
		{ href: '/events', label: ui('page.events') },
		{ href: '/threads', label: ui('page.threads') },
		{ href: '/figures', label: ui('page.figures') },
		{ href: '/instruments', label: ui('page.instruments') },
		{ href: '/places', label: ui('page.places') },
		{ href: '/sources', label: ui('page.sources') }
	]);
	const current = (href: string) =>
		href === '/' ? page.url.pathname === '/' : page.url.pathname.startsWith(href);

	// The atlas is an instrument, not a document: it takes the whole window and
	// nothing on it scrolls but the list.
	const atlas = $derived(page.url.pathname === '/');

	// The header's height, for anything else that sticks: a rail or a sidebar
	// pinned to the top of the window would otherwise slide in under it.
	let headerH = $state(0);

	// Pages cross-fade. The browser does the work; this only tells it when a
	// navigation starts and when the new page is in place.
	onNavigate((navigation) => {
		if (!document.startViewTransition || prefersReducedMotion.current) return;
		return new Promise((resolve) => {
			document.startViewTransition(async () => {
				resolve();
				await navigation.complete;
			});
		});
	});
</script>

<svelte:head>
	<title>{ui('site.name')}</title>
	<meta name="description" content={ui('site.description')} />
	<meta property="og:site_name" content={ui('site.name')} />
	<meta property="og:title" content={ui('site.name')} />
	<meta property="og:description" content={ui('site.description')} />
	<meta property="og:type" content="website" />
	<meta property="og:url" content={page.url.href} />
	<meta name="twitter:card" content="summary" />
</svelte:head>

{#if navigating.to}
	<div class="progress" role="progressbar" aria-label={ui('site.loading')}></div>
{/if}

<div class="shell" class:atlas style:--header-h="{atlas ? 0 : headerH}px">
	<header bind:clientHeight={headerH}>
		<a class="brand" href="/">{ui('site.name')}</a>
		<nav>
			{#each nav as n (n.href)}
				<a href={n.href} aria-current={current(n.href) ? 'page' : undefined}>{n.label}</a>
			{/each}
		</nav>
		<div class="tools">
			<LangToggle />
			<ThemeToggle />
		</div>
	</header>

	<DraftNotice />

	{@render children()}

	{#if !atlas}
		<footer>
			<p>{ui('site.footer')}</p>
		</footer>
	{/if}
</div>

<style>
	:global(:root) {
		--ground: #f5f5f2;
		--panel: #ffffff;
		--ink: #1a1a18;
		--ink-soft: #5d5f5e;
		--rule: #d6d7d3;
		/* Wine: the one chromatic hue clear of every polity fill. The accent is also
		   painted on the map (pins, the selected outline), so it must not match any
		   territory. */
		--accent: #7c1d34;
		--accent-soft: #7c1d341a;
		/* the draft notice; amber rather than the accent, which means "a link" here */
		--warn-ink: #8a5a12;
		--warn-bg: #faf3e2;
		--warn-rule: #e3d0a4;
		--radius: 4px;
		--radius-lg: 8px;
		--elev-1: 0 1px 3px #0002, 0 4px 14px #0001;

		/* The map. A real sea: land stands out by lightness, not only by hue, so coasts read
		   at every zoom. The land stays in the lightness band the polity search
		   validated. */
		--sea: #aec3d1;
		--land: #ebe7dc;
		--coast: #6f8291;
		--hairline: #ffffff99;
		--label: #1a1a18;
		--label-halo: #ebe7dcdd;

		/* Served from /fonts (see lib/fonts.css); the rest is what draws until they land. */
		--serif:
			'Source Serif 4', 'Iowan Old Style', 'Palatino Linotype', Palatino, 'Noto Serif',
			Georgia, serif;
		--sans:
			'Source Sans 3', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', 'Noto Sans',
			sans-serif;
		--mono: ui-monospace, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;
		color-scheme: light;

		/* Reserve the scrollbar's width whether or not one is showing. The page
		   height moves with the legend's row count and whether the revolt note is
		   present, so scrubbing across 1831 to 1832 flips the scrollbar on and off
		   and slides the whole layout sideways under the reader. */
		scrollbar-gutter: stable;
	}

	/* The polity palette was validated against both land surfaces, so only the
	   surroundings change in dark mode; the fills do not. */
	:global(:root:not([data-theme='light'])) {
		@media (prefers-color-scheme: dark) {
			--ground: #141618;
			--panel: #1d2023;
			--ink: #ecebe6;
			--ink-soft: #9a9c99;
			--rule: #33373b;
			/* The light accent fails on a dark ground (under 3:1), so it is lifted here. */
			--accent: #e9899a;
			--accent-soft: #e9899a33;
			--elev-1: 0 1px 3px #0006, 0 4px 14px #0004;
			--sea: #06111f;
			--land: #34322c;
			--coast: #51616f;
			--hairline: #00000088;
			--label: #f3f1ea;
			--label-halo: #34322cdd;
			--warn-ink: #dcab4c;
			--warn-bg: #27231a;
			--warn-rule: #4a4026;
			color-scheme: dark;
		}
	}

	/* The same tokens, but chosen rather than inherited from the system. */
	:global(:root[data-theme='dark']) {
		--ground: #141618;
		--panel: #1d2023;
		--ink: #ecebe6;
		--ink-soft: #9a9c99;
		--rule: #33373b;
		/* The light accent fails on a dark ground (under 3:1), so it is lifted here. */
		--accent: #e9899a;
		--accent-soft: #e9899a33;
		--elev-1: 0 1px 3px #0006, 0 4px 14px #0004;
		--sea: #06111f;
		--land: #34322c;
		--coast: #51616f;
		--hairline: #00000088;
		--label: #f3f1ea;
		--label-halo: #34322cdd;
		--warn-ink: #dcab4c;
		--warn-bg: #27231a;
		--warn-rule: #4a4026;
		color-scheme: dark;
	}

	:global(body) {
		margin: 0;
		background: var(--ground);
		color: var(--ink);
		font-family: var(--sans);
		/* Source Sans runs small for its size; a point up keeps the measure the same. */
		font-size: 16px;
		line-height: 1.55;
		-webkit-font-smoothing: antialiased;
		font-feature-settings: 'kern', 'liga', 'calt';
	}
	:global(button, input, select, textarea) {
		font-family: inherit;
	}
	:global(a) {
		color: var(--accent);
	}
	:global(h1, h2, h3) {
		font-family: var(--serif);
		font-weight: 600;
		letter-spacing: -0.01em;
		text-wrap: balance;
	}

	/* Route changes cross-fade, briefly. */
	:global(::view-transition-old(root)),
	:global(::view-transition-new(root)) {
		animation-duration: 160ms;
	}

	/* A data fetch between pages is otherwise invisible: the old page just sits
	   there. The bar says something is on its way. */
	.progress {
		position: fixed;
		top: 0;
		left: 0;
		height: 2px;
		width: 40%;
		background: var(--accent);
		z-index: 10;
		animation: slide 900ms ease-in-out infinite alternate;
	}
	@keyframes slide {
		from {
			transform: translateX(-30%);
		}
		to {
			transform: translateX(200%);
		}
	}

	.shell {
		max-width: 1320px;
		margin: 0 auto;
		padding-block: 20px 48px;
		padding-inline: 20px;
		/* Nothing inside may widen the page: a child that overflows is clipped
		   rather than handing the reader a sideways scroll on every route. */
		overflow-x: clip;
	}
	.shell.atlas {
		max-width: none;
		height: 100dvh;
		box-sizing: border-box;
		display: flex;
		flex-direction: column;
		padding-block: 14px 14px;
	}
	.shell.atlas header {
		margin-bottom: 12px;
	}
	/* The header stays as the page scrolls, as a strip of frosted ground: the
	   way back to the other indexes is always one glance up. On the atlas page
	   nothing scrolls past it, so there it simply sits. */
	header {
		position: sticky;
		top: 0;
		z-index: 5;
		display: flex;
		align-items: baseline;
		gap: 24px;
		margin: 0 -20px 20px;
		padding: 0 20px 10px;
		flex-wrap: wrap;
		background: color-mix(in srgb, var(--ground) 86%, transparent);
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
	}
	header::after {
		content: '';
		position: absolute;
		left: 20px;
		right: 20px;
		bottom: 0;
		height: 1px;
		background: var(--rule);
		opacity: 0.7;
	}
	.shell.atlas header {
		position: static;
		margin: 0 0 12px;
		padding: 0;
		background: none;
		backdrop-filter: none;
	}
	.shell.atlas header::after {
		display: none;
	}
	/* The two toggles travel together, so the header's free space opens once,
	   before them, rather than once before each. */
	.tools {
		display: flex;
		align-items: baseline;
		gap: 8px;
		margin-left: auto;
	}
	.brand {
		font-family: var(--serif);
		font-size: 1.6rem;
		font-weight: 600;
		color: var(--ink);
		text-decoration: none;
	}
	nav {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 16px;
		min-width: 0;
	}
	nav a {
		position: relative;
		color: var(--ink-soft);
		text-decoration: none;
		font-size: 0.95rem;
		padding: 2px 0;
		transition: color 120ms ease;
	}
	nav a[aria-current='page'],
	nav a:hover {
		color: var(--accent);
	}
	/* The current page is underlined by a short rule, not only coloured: colour
	   alone is lost on the one reader in twelve who cannot tell it apart. */
	nav a[aria-current='page']::after {
		content: '';
		position: absolute;
		left: 0;
		right: 0;
		bottom: -2px;
		height: 2px;
		border-radius: 1px;
		background: var(--accent);
	}
	nav a:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: 2px;
		border-radius: var(--radius);
	}
	footer {
		margin-top: 36px;
		padding-top: 14px;
		border-top: 1px solid var(--rule);
		color: var(--ink-soft);
		font-size: 0.8rem;
	}
	footer p {
		margin: 0;
		max-width: 80ch;
	}
	/* On a phone the brand and the toggles share the first row and the links
	   take the second, wrapping as they need to. */
	@media (max-width: 560px) {
		header {
			gap: 10px 16px;
		}
		.tools {
			order: 1;
		}
		nav {
			order: 2;
			flex-basis: 100%;
		}
	}
	/* Below the two-column width the atlas is a tall page again: the map sticks
	   at the top (see the page) and the list scrolls beneath it. */
	@media (max-width: 900px) {
		.shell.atlas {
			height: auto;
			display: block;
			padding-bottom: 24px;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.progress {
			animation: none;
			width: 100%;
		}
		nav a {
			transition: none;
		}
	}
</style>
