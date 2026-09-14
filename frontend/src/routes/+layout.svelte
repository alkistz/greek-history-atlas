<script lang="ts">
	let { children } = $props();
</script>

<svelte:head>
	<title>after1821 — an atlas of Greek history</title>
	<meta
		name="description"
		content="An interactive atlas of Greek history from 1821, where the map redraws as territorial control changes."
	/>
</svelte:head>

{@render children()}

<style>
	:global(:root) {
		--ground: #f4f1ea;
		--panel: #fbf9f5;
		--ink: #26231e;
		--ink-soft: #6b655c;
		--rule: #ddd6c9;
		--hairline: #ffffff88;
		--unmodelled: #e3ded2;
		--accent: #a8443a;
		--radius: 4px;
		--serif: 'Iowan Old Style', 'Palatino Linotype', Palatino, Georgia, serif;
		--sans: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif;
		--mono: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
		color-scheme: light;
	}

	:global(:root:not([data-theme='light'])) {
		@media (prefers-color-scheme: dark) {
			--ground: #1b1a17;
			--panel: #232120;
			--ink: #ece7dc;
			--ink-soft: #9a9287;
			--rule: #3a3631;
			--hairline: #00000066;
			--unmodelled: #2e2b27;
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
</style>
