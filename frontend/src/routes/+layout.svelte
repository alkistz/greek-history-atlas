<script lang="ts">
	import { page } from '$app/state';

	let { children } = $props();

	const nav = [
		{ href: '/', label: 'Atlas' },
		{ href: '/figures', label: 'Figures' }
	];
	const current = (href: string) =>
		href === '/' ? page.url.pathname === '/' : page.url.pathname.startsWith(href);
</script>

<svelte:head>
	<title>Greek History Atlas</title>
	<meta
		name="description"
		content="An interactive atlas of Greek history from 1821, where the map redraws as territorial control changes."
	/>
</svelte:head>

<div class="shell">
	<header>
		<a class="brand" href="/">Greek History Atlas</a>
		<nav>
			{#each nav as n (n.href)}
				<a href={n.href} aria-current={current(n.href) ? 'page' : undefined}>{n.label}</a>
			{/each}
		</nav>
	</header>

	{@render children()}

	<footer>
		<p>
			Boundaries from Eurostat Nuts2json (2021, 03M), dissolved into atoms. Neighbouring land
			is drawn at present-day extent and uncoloured. Several historical frontiers are
			approximated; see the README for the list.
		</p>
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
			color-scheme: dark;
		}
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
