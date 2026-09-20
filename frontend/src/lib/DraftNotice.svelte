<!--
	What the corpus is, said once, on every page.

	Not dismissible. The claim it qualifies is on every event page, so a notice the
	reader can turn off would be off exactly where it matters. It is compact instead:
	one line always, the honest detail a click away.
-->
<aside class="notice">
	<span class="badge">AI draft</span>
	<details>
		<summary>
			The history in this atlas was researched and written by an AI model, not by a
			historian. Dates, figures and attributions may be wrong.
		</summary>
		<div class="more">
			<p>
				Every entry has been read in both English and Greek and checked for internal
				consistency — dates, arithmetic, and whether the instruments and people it names
				are the right ones. That is not the same as being verified. Only a small number of
				entries have been checked against published sources, and none has yet been reviewed
				by a person.
			</p>
			<p>
				Each event, figure and treaty cites its sources; follow them before relying on
				anything here. This is a prototype, and the corpus is a first draft.
			</p>
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
