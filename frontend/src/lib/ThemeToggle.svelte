<script lang="ts">
	type Theme = 'light' | 'dark';

	const LABEL: Record<Theme, string> = { light: 'Light', dark: 'Dark' };
	const GLYPH: Record<Theme, string> = { light: '☀', dark: '☾' };

	/** A stored choice wins; otherwise take the system preference once and keep it. */
	function initial(): Theme {
		try {
			const v = localStorage.getItem('theme');
			if (v === 'light' || v === 'dark') return v;
		} catch {
			// private mode, blocked storage: fall through to the system preference
		}
		return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
	}

	let theme = $state<Theme>(initial());

	$effect(() => {
		document.documentElement.setAttribute('data-theme', theme);
		try {
			localStorage.setItem('theme', theme);
		} catch {
			// nothing to do; the choice simply will not survive a reload
		}
	});
</script>

<button
	onclick={() => (theme = theme === 'light' ? 'dark' : 'light')}
	title="Theme: {LABEL[theme]}"
	aria-label="Theme: {LABEL[theme]}. Switch to {LABEL[theme === 'light' ? 'dark' : 'light']}."
>
	<span aria-hidden="true">{GLYPH[theme]}</span>
	{LABEL[theme]}
</button>

<style>
	button {
		font: inherit;
		font-size: 0.82rem;
		background: none;
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		color: var(--ink-soft);
		padding: 2px 9px;
		cursor: pointer;
		display: inline-flex;
		align-items: center;
		gap: 6px;
	}
	button:hover {
		color: var(--accent);
		border-color: var(--accent);
	}
</style>
