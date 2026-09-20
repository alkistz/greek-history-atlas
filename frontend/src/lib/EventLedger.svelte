<script lang="ts">
	import { within, year } from './time';
	import type { AtlasEvent } from './types';

	interface Props {
		events: AtlasEvent[];
		date: string;
		selectedId: string | null;
		onselect: (e: AtlasEvent) => void;
	}
	let { events, date, selectedId, onselect }: Props = $props();
</script>

<ol class="ledger">
	{#each events as e (e.id)}
		{@const active = within(date, e.period[0], e.period[1])}
		{@const past = e.period[1] <= date}
		<li class:active class:past class:selected={selectedId === e.id}>
			<button onclick={() => onselect(e)}>
				<span class="etime">{year(e.period[0])}</span>
				<span class="etitle">{e.title.en}</span>
			</button>
			{#if active || selectedId === e.id}
				<p class="esummary">{e.summary.en}</p>
				<p class="emore">
					{#if e.as_written}<span class="eold">Old Style: {e.as_written.date}</span>{/if}
					<a href="/events/{e.id}">Read more</a>
				</p>
			{/if}
		</li>
	{/each}
</ol>

<style>
	.ledger {
		list-style: none;
		margin: 0;
		padding: 0;
		border-top: 1px solid var(--rule);
	}
	li {
		border-bottom: 1px solid var(--rule);
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
		padding: 7px 2px;
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
		padding-left: 46px;
		font-size: 0.88rem;
		color: var(--ink-soft);
	}
	.emore {
		margin: 0 0 10px;
		padding-left: 46px;
		font-size: 0.78rem;
		display: flex;
		gap: 12px;
	}
	.eold {
		font-family: var(--mono);
		color: var(--ink-soft);
	}
	a {
		color: var(--accent);
	}
</style>
