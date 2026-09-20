<script lang="ts">
	import { ENDONYM, lang } from '$lib/lang.svelte';
	import { ui } from '$lib/ui';

	// The corpus is bilingual and complete in both, so this is a plain two-way
	// switch rather than a menu: there is never a third option to reach for.

	// `app.html` ships `lang="en"`; keep the document honest, so a screen reader
	// switches voice with the prose and the browser hyphenates it correctly.
	$effect(() => {
		document.documentElement.lang = lang.current;
	});
</script>

<button
	onclick={() => lang.set(lang.other)}
	lang={lang.other}
	title={ui('lang.current', { name: ENDONYM[lang.current] })}
	aria-label={ui('lang.switch', { name: ENDONYM[lang.current], other: ENDONYM[lang.other] })}
>
	<span aria-hidden="true">{lang.other.toUpperCase()}</span>
	{ENDONYM[lang.other]}
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
	span {
		font-family: var(--mono);
		font-size: 0.72rem;
		letter-spacing: 0.04em;
		opacity: 0.75;
	}
</style>
