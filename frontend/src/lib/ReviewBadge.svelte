<script lang="ts">
	import { badgeLabel, strongest, toneOf } from './review';
	import type { Review } from './types';

	interface Props {
		review: Review | null | undefined;
		/** the bare result, for dense rows where the word "pass" is noise */
		compact?: boolean;
	}
	let { review, compact = false }: Props = $props();

	const shown = $derived(strongest(review));
	const tone = $derived(toneOf(review));
	const label = $derived(compact ? (shown?.pass.result ?? 'unreviewed') : badgeLabel(review));
	// The title carries what the badge has no room for: who, when, and in which
	// languages. A badge that only says "corrected" invites the wrong inference.
	const hint = $derived.by(() => {
		if (!shown) return 'Nobody has looked at this entry yet.';
		const who = shown.track === 'manual' ? 'Reviewed by a person' : 'Machine pass';
		return `${who}, ${shown.pass.date}${shown.pass.by ? ` — ${shown.pass.by}` : ''}`;
	});
</script>

<span class="badge {tone}" class:compact title={hint}>{label}</span>

<style>
	.badge {
		display: inline-block;
		font-family: var(--mono);
		font-size: 0.66rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
		white-space: nowrap;
		border: 1px solid currentColor;
		border-radius: var(--radius);
		padding: 0 5px;
		vertical-align: 1px;
		cursor: help;
	}
	.compact {
		letter-spacing: 0.05em;
	}
	.muted {
		color: var(--ink-soft);
		opacity: 0.8;
	}
	.warn {
		color: var(--warn-ink);
	}
	.ok {
		color: var(--ink-soft);
		border-color: var(--ink-soft);
	}
	.strong {
		color: var(--accent);
	}
</style>
