<script lang="ts">
	import { navigating, page } from '$app/state';
	import '$lib/fonts.css';
	import DraftNotice from '$lib/DraftNotice.svelte';
	import LangToggle from '$lib/LangToggle.svelte';
	import { ui } from '$lib/ui';
	import ThemeToggle from '$lib/ThemeToggle.svelte';
	import { provideChrome } from '$lib/chrome.svelte';
	import { ATLAS_PATH } from '$lib/viewstate';

	let { children } = $props();

	const nav = $derived([
		{ href: ATLAS_PATH, label: ui('page.atlas') },
		{ href: '/events', label: ui('page.events') },
		{ href: '/threads', label: ui('page.threads') },
		{ href: '/figures', label: ui('page.figures') },
		{ href: '/instruments', label: ui('page.instruments') },
		{ href: '/places', label: ui('page.places') },
		{ href: '/sources', label: ui('page.sources') }
	]);
	// The front page is the brand's link and has no tab of its own.
	const current = (href: string) => page.url.pathname.startsWith(href);

	// The atlas is an instrument, not a document: it takes the whole window and
	// nothing on it scrolls but the list.
	const atlas = $derived(page.url.pathname === ATLAS_PATH);
	// The front page runs edge to edge, so its map can.
	const home = $derived(page.url.pathname === '/');

	// The header's and the notice's heights: for anything else that sticks, which
	// would otherwise slide in under the header, and for the atlas, where both
	// float over the map and the camera has to fit around them.
	const chrome = provideChrome();

	// Pages do not cross-fade. A view transition holds the old page frozen until
	// the new one has loaded and rendered, then animates on top of that, and its
	// snapshots of a full-window map are expensive: measured, it was the largest
	// single source of lag when moving between tabs.
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

<div
	class="shell"
	class:atlas
	class:home
	style:--header-h="{chrome.header}px"
	style:--notice-h="{chrome.notice}px"
>
	<header bind:offsetHeight={chrome.header}>
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

	<div class="notice-slot" bind:offsetHeight={chrome.notice}>
		<DraftNotice />
	</div>

	{@render children()}

	{#if !atlas}
		<footer>
			<p>{ui('site.footer')}</p>
		</footer>
	{/if}
</div>

<style>
	/* The page is the sea. The surfaces, the ink and the accent are one cool
	   blue family, so the polity colours on the map are the only saturated
	   things on screen. */
	:global(:root) {
		--ground: #dbe6ed;
		--panel: #ffffff;
		--ink: #13202b;
		--ink-soft: #536373;
		--rule: #bccbd5;
		/* The accent is the ink. Wine was the one hue clear of every polity fill,
		   and the accent is painted on the map (pins, the selected outline), so
		   without wine nothing chromatic is left that the map does not use. */
		--accent: #13202b;
		--accent-soft: #13202b12;
		/* the draft notice: amber, because it is a status and not a link */
		--warn-ink: #8a5a12;
		--radius: 0px;
		--radius-lg: 0px;
		--elev-1: none;

		/* The map. Sea and page are one colour, so the map has no edge; the
		   water-lining is drawn a step darker, out from every coast. */
		--sea: #dbe6ed;
		--waterline: #a6bccb;
		--land: #f7f7f4;
		--coast: #9db3c3;
		--hairline: #ffffffb3;
		--label: #13202b;
		--label-halo: #f7f7f4cc;

		/* Served from /fonts (see lib/fonts.css); the rest is what draws until they land. */
		--serif:
			'Source Serif 4', 'Iowan Old Style', 'Palatino Linotype', Palatino, 'Noto Serif',
			Georgia, serif;
		--sans:
			'Source Sans 3', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', 'Noto Sans',
			sans-serif;
		/* Dates, years and quantities: the serif, as an atlas sets them. */
		--figures: var(--serif);
		color-scheme: light;

		/* Reserve the scrollbar's width whether or not one is showing. The page
		   height moves with the legend's row count and whether the revolt note is
		   present, so scrubbing across 1831 to 1832 flips the scrollbar on and off
		   and slides the whole layout sideways under the reader. */
		scrollbar-gutter: stable;
	}

	/* A night chart: the same family, deep navy. The polity fills do not change. */
	:global(:root:not([data-theme='light'])) {
		@media (prefers-color-scheme: dark) {
			--ground: #08111a;
			--panel: #0f1b27;
			--ink: #e6edf2;
			--ink-soft: #8a9cad;
			--rule: #24364a;
			--accent: #e6edf2;
			--accent-soft: #e6edf21c;
			--sea: #08111a;
			--waterline: #22384b;
			--land: #18212a;
			--coast: #2b4152;
			--hairline: #08111a99;
			--label: #eef3f7;
			--label-halo: #08111acc;
			--warn-ink: #dcab4c;
			color-scheme: dark;
		}
	}

	/* The same tokens, but chosen rather than inherited from the system. */
	:global(:root[data-theme='dark']) {
		--ground: #08111a;
		--panel: #0f1b27;
		--ink: #e6edf2;
		--ink-soft: #8a9cad;
		--rule: #24364a;
		--accent: #e6edf2;
		--accent-soft: #e6edf21c;
		--sea: #08111a;
		--waterline: #22384b;
		--land: #18212a;
		--coast: #2b4152;
		--hairline: #08111a99;
		--label: #eef3f7;
		--label-halo: #08111acc;
		--warn-ink: #dcab4c;
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
		/* Old-style figures throughout, as in a printed atlas; tabular columns
		   still set tabular-nums on top of them. */
		font-feature-settings: 'kern', 'liga', 'calt', 'onum';
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
	/* The front page runs edge to edge so its map can. Everything else on it
	   keeps the usual measure through --inset, which resolves against whatever
	   full-width box it is used in. */
	.shell.home {
		max-width: none;
		padding-inline: 0;
		--inset: max(20px, calc((100% - 1280px) / 2));
	}
	.shell.home > header {
		margin-inline: calc(var(--inset) - 20px);
	}
	.shell.home > .notice-slot,
	.shell.home > footer {
		margin-inline: var(--inset);
	}
	/* Narrow, the atlas is a tall page: the map sticks at the top (see the page)
	   and the list scrolls beneath it. */
	.shell.atlas {
		max-width: none;
		box-sizing: border-box;
		padding-block: 14px 24px;
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
	/* Wide, the atlas takes the whole window: the map lies under everything and
	   the header and the notice float over it, as panels on a chart. Below this
	   width the panels would leave too little map, so it stays a tall page; the
	   atlas page uses the same breakpoint. */
	@media (min-width: 1100px) {
		.shell.atlas {
			position: relative;
			height: 100dvh;
			display: flex;
			flex-direction: column;
			padding: 0;
		}
		.shell.atlas header {
			position: absolute;
			z-index: 7;
			top: 12px;
			left: 12px;
			right: 12px;
			margin: 0;
			padding: 8px 16px;
			align-items: center;
			background: var(--panel);
			border: 1px solid var(--ink);
		}
		.shell.atlas .notice-slot {
			position: absolute;
			z-index: 7;
			top: calc(12px + var(--header-h) + 8px);
			left: 12px;
			max-width: min(640px, calc(100% - 444px));
		}
		.shell.atlas .notice-slot :global(.notice) {
			margin: 0;
			padding: 5px 10px;
			background: var(--panel);
			border: 1px solid var(--ink);
		}
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
		font-weight: 500;
		font-variant-caps: small-caps;
		letter-spacing: 0.05em;
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
		font-size: 1.04rem;
		font-variant-caps: all-small-caps;
		letter-spacing: 0.08em;
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
		bottom: 0;
		height: 1px;
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
