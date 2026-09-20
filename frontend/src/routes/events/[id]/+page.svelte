<script lang="ts">
	import Atlas from '$lib/Atlas.svelte';
	import Citation from '$lib/Citation.svelte';
	import Legend from '$lib/Legend.svelte';
	import { visibleIn } from '$lib/projection';
	import { legendEntries, resolveOn } from '$lib/resolve';
	import { prettyPeriod } from '$lib/time';
	import type { Pin } from '$lib/types';
	import { atlasHref } from '$lib/viewstate';

	let { data } = $props();
	const event = $derived(data.event);
	const date = $derived(event.period[0]);
	const legend = $derived(
		legendEntries(
			resolveOn(data.control, date),
			data.meta.polities,
			visibleIn(data.atoms.features, event.frame)
		)
	);
	const pins = $derived.by((): Pin[] =>
		event.place ? [{ id: event.place.id, lon: event.place.lon, lat: event.place.lat, label: event.place.name.en }] : []
	);
</script>

<svelte:head>
	<title>{event.title.en} — Greek History Atlas</title>
</svelte:head>

<article class="event">
	<figure class="map">
		<Atlas
			atoms={data.atoms.features}
			land={data.land}
			meta={data.meta}
			control={data.control}
			{date}
			frame={event.frame}
			highlight={event.atom}
			{pins}
			showLabels={false}
			interactive={false}
		/>
		<figcaption>
			<Legend entries={legend} />
			<p class="open">
				<a href={atlasHref({ on: date, frame: event.frame, event: event.id })}>
					Open this day on the atlas →
				</a>
			</p>
		</figcaption>
	</figure>

	<div class="text">
		<p class="kicker">
			{prettyPeriod(event.period, event.precision)}
			{#if event.as_written}
				<span class="old">Old Style {event.as_written.date}</span>
			{/if}
			{#if event.place}
				<span class="place">{event.place.name.en}</span>
			{/if}
		</p>
		<h1>{event.title.en}</h1>
		<p class="summary">{event.summary.en}</p>

		{#if event.body_html}
			<div class="prose">{@html event.body_html.en}</div>
		{/if}

		{#if event.figures.length}
			<h2>People</h2>
			<ul class="plain">
				{#each event.figures as f (f.id)}
					<li><a href="/figures/{f.id}">{f.name.en}</a> <span class="muted">{f.role}</span></li>
				{/each}
			</ul>
		{/if}

		{#if event.instrument}
			<h2>Instrument</h2>
			<p><a href="/instruments/{event.instrument.id}">{event.instrument.name.en}</a></p>
		{/if}

		{#if event.threads.length}
			<h2>Threads</h2>
			<ul class="threads">
				{#each event.threads as t (t.id)}
					<li>
						<a class="arc" href="/threads/{t.id}">{t.name.en}</a>
						<span class="step">
							{#if t.previous}
								<a href="/events/{t.previous.id}">← {t.previous.title.en}</a>
							{:else}
								<span class="muted">← starts here</span>
							{/if}
							{#if t.next}
								<a href="/events/{t.next.id}">{t.next.title.en} →</a>
							{:else}
								<span class="muted">ends here →</span>
							{/if}
						</span>
					</li>
				{/each}
			</ul>
		{/if}

		{#if event.related.length}
			<h2>Nearby</h2>
			<ul class="plain">
				{#each event.related as r (r.id)}
					<li><span class="muted mono">{r.period[0].slice(0, 4)}</span> <a href="/events/{r.id}">{r.title.en}</a></li>
				{/each}
			</ul>
		{/if}

		{#if event.sources.length}
			<h2>Sources</h2>
			<ul class="plain sources">
				{#each event.sources as s (s.id)}
					<li><Citation source={s} /></li>
				{/each}
			</ul>
		{/if}
	</div>
</article>

<style>
	.threads {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	.threads li {
		padding: 6px 0;
		border-top: 1px solid var(--rule);
	}
	.threads li:first-child {
		border-top: none;
	}
	.arc {
		font-weight: 600;
	}
	/* The two steps sit under the arc's name: where you are, and the way out either side. */
	.step {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 4px 16px;
		font-size: 0.85rem;
		margin-top: 2px;
	}
	.event {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr);
		gap: 32px;
		align-items: start;
	}
	.map {
		margin: 0;
		position: sticky;
		top: 16px;
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 8px;
	}
	figcaption {
		margin-top: 10px;
	}
	.open {
		margin: 10px 0 0;
		font-size: 0.85rem;
	}
	.kicker {
		margin: 0;
		color: var(--ink-soft);
		font-size: 0.9rem;
		display: flex;
		gap: 14px;
		flex-wrap: wrap;
	}
	.old {
		font-family: var(--mono);
		font-size: 0.8rem;
	}
	h1 {
		font-size: 1.9rem;
		margin: 4px 0 10px;
	}
	h2 {
		font-size: 1.05rem;
		margin: 22px 0 6px;
	}
	.summary {
		font-size: 1.05rem;
		color: var(--ink-soft);
		max-width: 60ch;
	}
	.prose {
		max-width: 62ch;
	}
	.prose :global(p) {
		margin: 0 0 1em;
	}
	.plain {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	.plain li {
		margin: 2px 0;
	}
	.sources {
		font-size: 0.88rem;
		color: var(--ink-soft);
	}
	.muted {
		color: var(--ink-soft);
		font-size: 0.85rem;
	}
	.mono {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
	}
	@media (max-width: 900px) {
		.event {
			grid-template-columns: 1fr;
		}
		.map {
			position: static;
		}
	}
</style>
