<script module lang="ts">
	/**
	 * What an event changed, 2 to 5. Fifteen events across two centuries are 5s,
	 * and the scale is meant to stay that steep, so the labels say what the number
	 * claims rather than leaving a bare digit to be read as a score out of five.
	 */
	export const SIGNIFICANCE_LABELS: Record<number, string> = {
		1: 'Minor',
		2: 'Notable',
		3: 'Consequential',
		4: 'Major',
		5: 'Changed the state'
	};
</script>

<script lang="ts">
	interface Props {
		significance: number;
		/** dots only, for a dense row */
		compact?: boolean;
	}
	let { significance, compact = false }: Props = $props();

	const n = $derived(Math.min(Math.max(significance, 1), 5));
	const label = $derived(SIGNIFICANCE_LABELS[n] ?? String(n));
</script>

<!-- The visible parts are hidden from assistive tech and said once, in full, by
     the text below them: otherwise "Changed the state" is read twice, and once
     without the word that says what it is measuring. -->
<span class="sig" title="Significance {n} of 5 — {label}">
	<span class="dots" aria-hidden="true">
		{#each [1, 2, 3, 4, 5] as i (i)}
			<span class="dot" class:on={i <= n}></span>
		{/each}
	</span>
	{#if !compact}<span class="label" aria-hidden="true">{label}</span>{/if}
	<span class="sr">Significance {n} of 5, {label}</span>
</span>

<style>
	.sig {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		cursor: help;
	}
	.dots {
		display: inline-flex;
		gap: 2px;
	}
	.dot {
		width: 5px;
		height: 5px;
		border-radius: 50%;
		border: 1px solid var(--ink-soft);
		opacity: 0.55;
	}
	.dot.on {
		background: var(--accent);
		border-color: var(--accent);
		opacity: 1;
	}
	.label {
		color: var(--ink-soft);
		font-size: 0.74rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	.sr {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip-path: inset(50%);
	}
</style>
