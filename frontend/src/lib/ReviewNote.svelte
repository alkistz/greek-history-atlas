<script lang="ts">
	import { isSourced, langList } from './review';
	import { term, ui } from './ui';
	import { prettyDate } from './time';
	import type { Pass, Review } from './types';

	let { review }: { review: Review | null | undefined } = $props();

	const tracks = $derived(
		[
			{ track: 'manual' as const, pass: review?.manual ?? null },
			{ track: 'auto' as const, pass: review?.auto ?? null }
		].filter((t): t is { track: 'manual' | 'auto'; pass: Pass } => t.pass !== null)
	);

	// Said in full rather than as a word, because "clean" on its own reads as a
	// verdict about the history when it is a statement about the reading.
	const said = (result: string) => term('reviewnote.said', result);
</script>

<section class="review">
	<h2>{ui('reviewnote.heading')}</h2>
	{#if !tracks.length}
		<p class="none">{ui('reviewnote.none')}</p>
	{:else}
		{#each tracks as t (t.track)}
			<div class="track">
				<p class="line">
					<span class="what">{term('reviewnote.track', t.track)}</span>
					<span class="when">{prettyDate(t.pass.date)}</span>
					<span class="said">{said(t.pass.result)}</span>
				</p>
				<p class="detail">
					{ui('reviewnote.readin', { langs: langList(t.pass) })}
					{#if t.pass.by}<span class="by">{t.pass.by}</span>{/if}
				</p>
				{#if t.pass.note}<p class="note">{t.pass.note}</p>{/if}
			</div>
		{/each}
		{#if !review?.manual}
			<p class="caveat">
				{ui(isSourced(review) ? 'reviewnote.caveat.sourced' : 'reviewnote.caveat.unsourced')}
			</p>
		{/if}
	{/if}
</section>

<style>
	.review {
		margin-top: 26px;
		padding: 10px 12px;
		border: 1px solid var(--rule);
		border-left: 3px solid var(--warn-rule);
		border-radius: var(--radius);
		background: var(--panel);
		max-width: 62ch;
	}
	h2 {
		font-size: 0.95rem;
		margin: 0 0 6px;
	}
	.track + .track {
		margin-top: 10px;
		padding-top: 10px;
		border-top: 1px solid var(--rule);
	}
	.line {
		margin: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 4px 10px;
		align-items: baseline;
		font-size: 0.88rem;
	}
	.what {
		font-weight: 600;
	}
	.when {
		font-family: var(--mono);
		font-size: 0.78rem;
		color: var(--ink-soft);
	}
	.said {
		color: var(--ink-soft);
	}
	.detail,
	.note,
	.none,
	.caveat {
		margin: 4px 0 0;
		font-size: 0.85rem;
		color: var(--ink-soft);
	}
	.by {
		font-style: italic;
	}
	.note {
		white-space: pre-line;
	}
	.caveat {
		margin-top: 10px;
		padding-top: 8px;
		border-top: 1px solid var(--rule);
	}
</style>
