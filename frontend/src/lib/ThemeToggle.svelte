<script lang="ts">
	type Theme = 'auto' | 'light' | 'dark';

	const NEXT: Record<Theme, Theme> = { auto: 'light', light: 'dark', dark: 'auto' };
	const LABEL: Record<Theme, string> = { auto: 'Auto', light: 'Light', dark: 'Dark' };
	const GLYPH: Record<Theme, string> = { auto: '◐', light: '☀', dark: '☾' };

	function stored(): Theme {
		try {
			const v = localStorage.getItem('theme');
			if (v === 'light' || v === 'dark' || v === 'auto') return v;
		} catch {
			// private mode, blocked storage: fall through to the system preference
		}
		return 'auto';
	}

	let theme = $state<Theme>(stored());

	// `auto` removes the attribute so the media query in the layout decides. The
	// two explicit values set it, which is what the [data-theme] rules key off.
	$effect(() => {
		const root = document.documentElement;
		if (theme === 'auto') root.removeAttribute('data-theme');
		else root.setAttribute('data-theme', theme);
		try {
			localStorage.setItem('theme', theme);
		} catch {
			// nothing to do; the choice simply will not survive a reload
		}
	});
</script>

<button
	onclick={() => (theme = NEXT[theme])}
	title="Theme: {LABEL[theme]}"
	aria-label="Theme: {LABEL[theme]}. Switch to {LABEL[NEXT[theme]]}."
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
