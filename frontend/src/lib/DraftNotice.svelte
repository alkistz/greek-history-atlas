<!--
	What the corpus is, said once, on every page.

	Not dismissible. The claim it qualifies is on every event page, so a notice the
	reader can turn off would be off exactly where it matters. It is one line instead.
-->
<script lang="ts">
	import { ui } from './ui';
</script>

<aside class="notice">
	<span class="badge">{ui('draft.badge')}</span>
	<p>{ui('draft.summary')}</p>
</aside>

<style>
	.notice {
		display: flex;
		align-items: baseline;
		gap: 10px;
		margin-bottom: 20px;
		padding: 8px 12px;
		background: var(--warn-bg);
		border: 1px solid var(--warn-rule);
		border-radius: var(--radius);
		font-size: 0.85rem;
		line-height: 1.5;
	}
	.badge {
		flex: none;
		font-family: var(--mono);
		font-size: 0.68rem;
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
		max-width: 78ch;
		color: var(--ink-soft);
	}
</style>
