<script lang="ts">
	import { ui } from './ui';
	import type { Review } from './types';

	interface Props {
		review: Review | null | undefined;
		/** kept for the call sites; the one label shown is short already */
		compact?: boolean;
	}
	let { review, compact = false }: Props = $props();

	// Only a person's pass earns a mark. The machine track still drives the
	// index filters, but as a badge it confused more than it told: "corrected"
	// described the entry's history, not its state, and the note that explained
	// it was never on screen. Nothing is shown for an auto pass or no pass at all.
	const pass = $derived(review?.manual ?? null);
	const hint = $derived.by(() => {
		if (!pass) return '';
		const who = ui('review.manual');
		return pass.by
			? ui('review.tip.by', { who, date: pass.date, by: pass.by })
			: ui('review.tip', { who, date: pass.date });
	});
</script>

{#if pass}
	<span class="badge" class:compact title={hint}>{ui('review.by.manual')}</span>
{/if}

<style>
	.badge {
		display: inline-block;
		font-family: var(--mono);
		font-size: 0.66rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
		white-space: nowrap;
		color: var(--accent);
		border: 1px solid currentColor;
		border-radius: var(--radius);
		padding: 0 5px;
		vertical-align: 1px;
		cursor: help;
	}
	.compact {
		letter-spacing: 0.05em;
	}
</style>
