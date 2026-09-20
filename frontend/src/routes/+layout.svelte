<script lang="ts">
	import { page } from '$app/state';
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

<div class="shell">
	<header>
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

	<footer>
		<p>{ui('site.footer')}</p>
	</footer>
</div>

<style>
	:global(:root) {
		--ground: #f4f1ea;
		--panel: #fbf9f5;
		--ink: #26231e;
		--ink-soft: #6b655c;
		--rule: #ddd6c9;
		--accent: #a8443a;
		/* the draft notice; amber rather than the accent, which means "a link" here */
		--warn-ink: #8a5a12;
		--warn-bg: #faf2e0;
		--warn-rule: #e3d0a4;
		--radius: 4px;

		/* the map */
		--sea: #dfe7ec;
		--land: #ece7db;
		--coast: #a9a190;
		--hairline: #ffffff99;
		--label: #26231e;
		--label-halo: #ece7dbdd;

		--serif:
			'Iowan Old Style', 'Palatino Linotype', Palatino, 'Source Serif 4', 'Noto Serif',
			'Liberation Serif', Georgia, serif;
		--sans: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', 'Noto Sans', sans-serif;
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
			--ground: #1b1a17;
			--panel: #232120;
			--ink: #ece7dc;
			--ink-soft: #9a9287;
			--rule: #3a3631;
			--sea: #1a2026;
			--land: #2c2a26;
			--coast: #57524a;
			--hairline: #00000088;
			--label: #f0ebe0;
			--label-halo: #2c2a26dd;
			--warn-ink: #d9a441;
			--warn-bg: #292317;
			--warn-rule: #4c3f23;
			color-scheme: dark;
		}
	}

	/* The same tokens, but chosen rather than inherited from the system. */
	:global(:root[data-theme='dark']) {
		--ground: #1b1a17;
		--panel: #232120;
		--ink: #ece7dc;
		--ink-soft: #9a9287;
		--rule: #3a3631;
		--sea: #1a2026;
		--land: #2c2a26;
		--coast: #57524a;
		--hairline: #00000088;
		--label: #f0ebe0;
		--label-halo: #2c2a26dd;
		--warn-ink: #d9a441;
		--warn-bg: #292317;
		--warn-rule: #4c3f23;
		color-scheme: dark;
	}

	:global(body) {
		margin: 0;
		background: var(--ground);
		color: var(--ink);
		font-family: var(--sans);
		font-size: 15px;
		line-height: 1.55;
		-webkit-font-smoothing: antialiased;
	}
	:global(a) {
		color: var(--accent);
	}
	:global(h1, h2, h3) {
		font-family: var(--serif);
		font-weight: 600;
		letter-spacing: -0.01em;
	}

	.shell {
		max-width: 1320px;
		margin: 0 auto;
		padding-block: 20px 48px;
		padding-inline: 20px;
	}
	header {
		display: flex;
		align-items: baseline;
		gap: 24px;
		margin-bottom: 20px;
		flex-wrap: wrap;
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
		gap: 16px;
	}
	nav a {
		color: var(--ink-soft);
		text-decoration: none;
		font-size: 0.95rem;
	}
	nav a[aria-current='page'],
	nav a:hover {
		color: var(--accent);
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
</style>
