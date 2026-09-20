<script lang="ts">
	import Citation from '$lib/Citation.svelte';
	import ReviewNote from '$lib/ReviewNote.svelte';
	import { prettyDate, year } from '$lib/time';
	import { atlasHref } from '$lib/viewstate';

	let { data } = $props();
	const inst = $derived(data.instrument);
	const polityName = $derived(new Map(data.meta.polities.map((p) => [p.id, p.name.en])));
	const atomName = $derived(new Map(data.meta.atoms.map((a) => [a.id, a.name.en])));
</script>

<svelte:head>
	<title>{inst.name.en} — Greek History Atlas</title>
</svelte:head>

<article class="instrument">
	<p class="kicker">{inst.kind} · signed {prettyDate(inst.signed)}</p>
	<h1>{inst.name.en}</h1>
	<p class="parties">{inst.parties.map((p) => polityName.get(p) ?? p).join(', ')}</p>
	<p class="open">
		<a href={atlasHref({ on: inst.signed })}>Open the atlas on this day →</a>
		{#if inst.text_url}
			<a class="text" href={inst.text_url} rel="noreferrer">Read the text of the {inst.kind} →</a>
		{/if}
	</p>
	{#if inst.summary}<p class="summary">{inst.summary.en}</p>{/if}
	{#if !inst.text_url}
		<p class="notext">
			This {inst.kind}'s own text is not linked yet. Nothing was linked that had not been
			opened, so the gap is deliberate rather than an oversight.
		</p>
	{/if}

	{#if inst.control.length}
		<h2>What it moved</h2>
		<ul class="plain">
			{#each inst.control as r, i (i)}
				<li>
					<a class="mono" href={atlasHref({ on: r.from })} title="Open the atlas on {prettyDate(r.from)}">
						{year(r.from)}
					</a>
					<span>
						{atomName.get(r.atom) ?? r.atom}: {polityName.get(r.polity) ?? r.polity}
						<span class="muted">{r.kind}</span>
						{#if r.note}<span class="note">{r.note}</span>{/if}
					</span>
				</li>
			{/each}
		</ul>
	{/if}

	{#if inst.events.length}
		<h2>Events</h2>
		<ul class="plain">
			{#each inst.events as e (e.id)}
				<li><span class="mono">{year(e.period[0])}</span> <a href="/events/{e.id}">{e.title.en}</a></li>
			{/each}
		</ul>
	{/if}

	{#if inst.sources.length}
		<h2>Sources</h2>
		<ul class="plain sources">
			{#each inst.sources as s (s.id)}
				<li><a href="/sources#{s.id}"><Citation source={s} /></a></li>
			{/each}
		</ul>
	{/if}

	<ReviewNote review={inst.review} />
</article>

<style>
	.instrument {
		max-width: 66ch;
	}
	.kicker {
		margin: 0;
		color: var(--ink-soft);
		font-size: 0.85rem;
	}
	h1 {
		font-size: 1.9rem;
		margin: 4px 0 4px;
	}
	.parties {
		margin: 0 0 4px;
		color: var(--ink-soft);
	}
	.open {
		margin: 0 0 14px;
		font-size: 0.85rem;
		display: flex;
		gap: 16px;
		flex-wrap: wrap;
	}
	.notext {
		margin: 8px 0 0;
		color: var(--ink-soft);
		font-size: 0.85rem;
	}
	.summary {
		font-size: 1.05rem;
	}
	h2 {
		font-size: 1.05rem;
		margin: 22px 0 6px;
	}
	.plain {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	.plain li {
		margin: 3px 0;
		display: flex;
		gap: 10px;
		align-items: baseline;
	}
	.sources li {
		display: list-item;
	}
	.mono {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.85rem;
		color: var(--ink-soft);
	}
	.muted {
		color: var(--ink-soft);
		font-size: 0.85rem;
	}
	/* Why a row is drawn the way it is: an atom-grained approximation, a partial
	   occupation, a frontier this model cannot cut. Fourteen rows carry one. */
	.note {
		display: block;
		color: var(--ink-soft);
		font-size: 0.82rem;
	}
	.sources {
		font-size: 0.88rem;
		color: var(--ink-soft);
	}
	.sources a {
		text-decoration: none;
	}
	.sources a:hover {
		text-decoration: underline;
	}
</style>
