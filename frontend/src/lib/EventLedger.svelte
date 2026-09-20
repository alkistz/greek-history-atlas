<script lang="ts">
	import { t } from './lang.svelte';
	import { ui } from './ui';
	import ReviewBadge from './ReviewBadge.svelte';
	import Significance from './Significance.svelte';
	import { within, year } from './time';
	import type { AtlasEvent } from './types';

	interface Props {
		events: AtlasEvent[];
		/** the whole corpus, so the count can read "n of all" under a region filter */
		total?: number;
		date: string;
		selectedId: string | null;
		onselect: (e: AtlasEvent) => void;
	}
	let { events, total, date, selectedId, onselect }: Props = $props();
	const all = $derived(total ?? events.length);

	let query = $state('');
	const uid = $props.id();

	// The same fields the /events page searches, so the two boxes cannot disagree
	// about what exists: a Greek title used to find an event there and not here.
	const shown = $derived.by(() => {
		const q = query.trim().toLowerCase();
		if (!q) return events;
		const hit = (s: string | null | undefined) => s != null && s.toLowerCase().includes(q);
		return events.filter(
			(e) =>
				hit(e.title.en) ||
				hit(e.title.el) ||
				hit(e.summary.en) ||
				hit(e.summary.el) ||
				e.period[0].includes(q)
		);
	});

	/** Decades, because a flat list of every event stops being readable well before a century. */
	const groups = $derived.by(() => {
		const out: { decade: string; events: AtlasEvent[] }[] = [];
		for (const e of shown) {
			const decade = `${e.period[0].slice(0, 3)}0s`;
			const last = out.at(-1);
			if (last?.decade === decade) last.events.push(e);
			else out.push({ decade, events: [e] });
		}
		return out;
	});

	/** The last event to have begun on or before the shown date: what the map is looking at. */
	const anchorId = $derived.by(() => {
		let id: string | null = null;
		for (const e of shown) if (e.period[0] <= date) id = e.id;
		return id;
	});

	const nodes = new Map<string, HTMLElement>();
	function register(node: HTMLElement, id: string) {
		nodes.set(id, node);
		return { destroy: () => nodes.delete(id) };
	}

	let box: HTMLDivElement | undefined = $state();

	// Scrolls the list, never the page: the map must not slide out of view while
	// the reader is scrubbing.
	function reveal(el: HTMLElement) {
		if (!box) return;
		const top = el.offsetTop - box.offsetTop;
		const bottom = top + el.offsetHeight;
		const behavior = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
		if (top < box.scrollTop + 28) box.scrollTo({ top: top - 34, behavior });
		else if (bottom > box.scrollTop + box.clientHeight)
			box.scrollTo({ top: bottom - box.clientHeight + 8, behavior });
	}
	$effect(() => {
		const id = selectedId ?? anchorId;
		if (!id) return;
		const el = nodes.get(id);
		if (el) reveal(el);
	});
</script>

<div class="head">
	<label class="search">
		<span class="sr">{ui('ledger.filter')}</span>
		<input
			id="{uid}-q"
			type="search"
			bind:value={query}
			placeholder={ui('ledger.placeholder')}
			autocomplete="off"
		/>
	</label>
	<p class="count" aria-live="polite">
		{#if query.trim() || shown.length !== all}{ui('ledger.shown', {
				shown: shown.length,
				total: all
			})}{:else}{ui('ledger.total', { total: all })}{/if}
	</p>
</div>

<div class="box" bind:this={box}>
	{#each groups as g (g.decade)}
		<h3 class="decade">{g.decade}</h3>
		<ol class="ledger">
			{#each g.events as e (e.id)}
				{@const active = within(date, e.period[0], e.period[1])}
				{@const past = e.period[1] <= date}
				<li
					use:register={e.id}
					class:active
					class:past
					class:selected={selectedId === e.id}
					class:anchor={selectedId === null && anchorId === e.id}
				>
					<button onclick={() => onselect(e)} aria-current={selectedId === e.id ? 'true' : undefined}>
						<span class="etime">{year(e.period[0])}</span>
						<span class="etitle">{t(e.title)}</span>
					</button>
					{#if active || selectedId === e.id}
						<p class="esummary">{t(e.summary)}</p>
						<p class="emarks">
							<Significance significance={e.significance} compact />
							<ReviewBadge review={e.review} compact />
						</p>
						<p class="emore">
							{#if e.as_written}<span class="eold"
									>{ui('date.oldstyle.label', { date: e.as_written.date })}</span
								>{/if}
							<a href="/events/{e.id}">{ui('ledger.readmore')}</a>
						</p>
					{/if}
				</li>
			{/each}
		</ol>
	{:else}
		<p class="empty">{ui('ledger.empty', { query })}</p>
	{/each}
</div>

<style>
	.sr {
		position: absolute;
		width: 1px;
		height: 1px;
		overflow: hidden;
		clip-path: inset(50%);
	}
	.head {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-bottom: 8px;
	}
	.search {
		flex: 1;
		min-width: 0;
	}
	input[type='search'] {
		width: 100%;
		box-sizing: border-box;
		font: inherit;
		font-size: 0.88rem;
		background: var(--panel);
		color: var(--ink);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 5px 9px;
	}
	input[type='search']:focus-visible {
		outline: 2px solid var(--accent);
		outline-offset: -1px;
		border-color: transparent;
	}
	.count {
		flex: none;
		margin: 0;
		color: var(--ink-soft);
		font-size: 0.78rem;
		font-variant-numeric: tabular-nums;
	}

	.box {
		position: relative;
		overflow-y: auto;
		max-height: min(72vh, 760px);
		border-top: 1px solid var(--rule);
		overscroll-behavior: contain;
	}
	.decade {
		position: sticky;
		top: 0;
		z-index: 1;
		margin: 0;
		padding: 5px 2px 3px;
		background: var(--ground);
		color: var(--ink-soft);
		font-family: var(--mono);
		font-size: 0.74rem;
		letter-spacing: 0.08em;
		border-bottom: 1px solid var(--rule);
	}
	.ledger {
		list-style: none;
		margin: 0;
		padding: 0;
	}
	li {
		border-bottom: 1px solid var(--rule);
	}
	li.anchor,
	li.selected {
		background: var(--panel);
	}
	li.active {
		box-shadow: inset 2px 0 0 var(--accent);
	}
	button {
		display: flex;
		gap: 10px;
		width: 100%;
		text-align: left;
		font: inherit;
		background: none;
		border: 0;
		color: var(--ink-soft);
		padding: 7px 2px 7px 8px;
		cursor: pointer;
	}
	button:hover .etitle {
		color: var(--accent);
	}
	.past button {
		color: var(--ink);
	}
	.active button,
	.selected button {
		color: var(--ink);
		font-weight: 600;
	}
	.etime {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.82rem;
		flex: none;
		padding-top: 1px;
	}
	.esummary {
		margin: 0 0 6px;
		padding-left: 52px;
		font-size: 0.88rem;
		color: var(--ink-soft);
	}
	.emarks {
		display: flex;
		align-items: center;
		gap: 10px;
		margin: 0 0 4px;
		padding-left: 52px;
	}
	.emore {
		margin: 0 0 10px;
		padding-left: 52px;
		font-size: 0.78rem;
		display: flex;
		gap: 12px;
	}
	.eold {
		font-family: var(--mono);
		color: var(--ink-soft);
	}
	.empty {
		color: var(--ink-soft);
		font-size: 0.9rem;
		padding: 12px 2px;
	}
	a {
		color: var(--accent);
	}

	/* Stacked under the map, the list is the page's own tail; a nested scroller
	   there is a trap on touch. */
	@media (max-width: 900px) {
		.box {
			max-height: none;
			overflow: visible;
		}
	}
</style>
