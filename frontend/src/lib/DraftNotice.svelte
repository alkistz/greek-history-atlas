<!--
	What the corpus is, said once, on every page.

	Not dismissible. The claim it qualifies is on every event page, so a notice the
	reader can turn off would be off exactly where it matters. It is compact instead:
	one line always, the honest detail a click away.
-->
<script lang="ts">
	import { ui } from './ui';
</script>

<aside class="notice">
	<span class="badge">{ui('draft.badge')}</span>
	<details>
		<summary>{ui('draft.summary')}</summary>
		<div class="more">
			<p>{ui('draft.checked')}</p>
			<p>{ui('draft.cite')}</p>
		</div>
	</details>
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
	details {
		min-width: 0;
	}
	summary {
		cursor: pointer;
		color: var(--ink);
		max-width: 78ch;
	}
	summary:focus-visible {
		outline: 2px solid var(--warn-ink);
		outline-offset: 2px;
		border-radius: var(--radius);
	}
	.more {
		color: var(--ink-soft);
		max-width: 78ch;
	}
	.more p {
		margin: 8px 0 0;
	}
</style>
