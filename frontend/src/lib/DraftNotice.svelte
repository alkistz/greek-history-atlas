<!--
	What the corpus is, said once, on every page.

	Not dismissible. The claim it qualifies is on every event page, so a notice the
	reader can turn off would be off exactly where it matters. It is one line instead,
	and on a phone the line folds to its short form with the sentence a tap away:
	folded is not dismissed, the badge and the warning stay.
-->
<script lang="ts">
	import { ui } from './ui';
</script>

<aside class="notice">
	<span class="badge">{ui('draft.badge')}</span>
	<p class="full">{ui('draft.summary')}</p>
	<details class="fold">
		<summary>{ui('draft.short')}</summary>
		<p>{ui('draft.summary')}</p>
	</details>
</aside>

<style>
	.notice {
		display: flex;
		align-items: baseline;
		gap: 10px;
		margin-bottom: 16px;
		padding: 5px 10px;
		background: var(--warn-bg);
		border: 1px solid var(--warn-rule);
		border-radius: var(--radius);
		font-size: 0.82rem;
		line-height: 1.45;
	}
	.badge {
		flex: none;
		font-family: var(--mono);
		font-size: 0.66rem;
		text-transform: uppercase;
		letter-spacing: 0.09em;
		color: var(--warn-ink);
		border: 1px solid currentColor;
		border-radius: var(--radius);
		padding: 1px 6px;
		white-space: nowrap;
	}
	p {
		margin: 0;
		min-width: 0;
		color: var(--ink-soft);
	}
	.fold {
		display: none;
		min-width: 0;
		color: var(--ink-soft);
	}
	summary {
		cursor: pointer;
	}
	.fold p {
		margin-top: 4px;
	}
	@media (max-width: 560px) {
		.full {
			display: none;
		}
		.fold {
			display: block;
		}
	}
</style>
