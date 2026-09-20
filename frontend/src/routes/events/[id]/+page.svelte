<script lang="ts">
	import Atlas from '$lib/Atlas.svelte';
	import Citation from '$lib/Citation.svelte';
	import Legend from '$lib/Legend.svelte';
	import { t } from '$lib/lang.svelte';
	import { term, ui } from '$lib/ui';
	import { visibleIn } from '$lib/projection';
	import { regimeOn } from '$lib/regimes';
	import { legendEntries, resolveOn } from '$lib/resolve';
	import ReviewNote from '$lib/ReviewNote.svelte';
	import Significance from '$lib/Significance.svelte';
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
		event.place ? [{ id: event.place.id, lon: event.place.lon, lat: event.place.lat, label: t(event.place.name) }] : []
	);

	// Derived from the date, not stored on the event -- the same bargain regions
	// strike with atoms. It is the axis the map above cannot draw.
	const regime = $derived(regimeOn(data.meta.regimes, date));
	const atomName = $derived(
		event.atom
			? (t(data.meta.atoms.find((a) => a.id === event.atom)?.name) || event.atom)
			: null
	);
	// A one-atom region carries the atom's own name, and "Peloponnese in the
	// Peloponnese" tells the reader nothing. Named only where it adds a level.
	const region = $derived.by(() => {
		if (!event.atom) return undefined;
		const found = data.meta.regions.find((r) => r.atoms.includes(event.atom!));
		return found && t(found.name) !== atomName ? found : undefined;
	});
</script>

<svelte:head>
	<title>{ui('page.title', { page: t(event.title), site: ui('site.name') })}</title>
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
					{ui('event.openday')}
				</a>
			</p>
		</figcaption>
	</figure>

	<div class="text">
		<p class="kicker">
			{prettyPeriod(event.period, event.precision)}
			{#if event.as_written}
				<span class="old">{ui('date.oldstyle', { date: event.as_written.date })}</span>
			{/if}
			{#if event.place}
				<span class="place">{t(event.place.name)}<span class="pkind">{term('kind.place', event.place.kind)}</span></span>
			{/if}
		</p>
		<h1>{t(event.title)}</h1>
		<p class="summary">{t(event.summary)}</p>

		<dl class="facts">
			<dt>{ui('facet.significance')}</dt>
			<dd><Significance significance={event.significance} /></dd>
			{#if regime}
				<dt>{ui('facet.regime')}</dt>
				<dd>
					<a href="/events?regimes={regime.id}">{t(regime.name)}</a>
					{#if regime.summary}<span class="gloss">{t(regime.summary)}</span>{/if}
				</dd>
			{/if}
			{#if atomName}
				<dt>{ui('event.territory')}</dt>
				<dd>
					{atomName}{#if region}<span class="gloss">
							{ui('event.inregion')}
							<a href="/events?regions={region.id}">{t(region.name)}</a>
						</span>{/if}
				</dd>
			{/if}
		</dl>

		{#if event.body_html}
			<div class="prose">{@html t(event.body_html)}</div>
		{/if}

		{#if event.figures.length}
			<h2>{ui('event.people')}</h2>
			<ul class="plain">
				{#each event.figures as f (f.id)}
					<li>
						<a href="/figures/{f.id}">{t(f.name)}</a>
						<span class="muted">{term('role.event', f.role)}</span>
					</li>
				{/each}
			</ul>
		{/if}

		{#if event.instrument}
			<h2>{ui('event.instrument')}</h2>
			<p><a href="/instruments/{event.instrument.id}">{t(event.instrument.name)}</a></p>
		{/if}

		{#if event.threads.length}
			<h2>{ui('page.threads')}</h2>
			<ul class="threads">
				{#each event.threads as thread (thread.id)}
					<li>
						<a class="arc" href="/threads/{thread.id}">{t(thread.name)}</a>
						<span class="step">
							{#if thread.previous}
								<a href="/events/{thread.previous.id}">← {t(thread.previous.title)}</a>
							{:else}
								<span class="muted">{ui('event.starts')}</span>
							{/if}
							{#if thread.next}
								<a href="/events/{thread.next.id}">{t(thread.next.title)} →</a>
							{:else}
								<span class="muted">{ui('event.ends')}</span>
							{/if}
						</span>
					</li>
				{/each}
			</ul>
		{/if}

		{#if event.related.length}
			<h2>{ui('event.nearby')}</h2>
			<ul class="plain">
				{#each event.related as r (r.id)}
					<li><span class="muted mono">{r.period[0].slice(0, 4)}</span> <a href="/events/{r.id}">{t(r.title)}</a></li>
				{/each}
			</ul>
		{/if}

		{#if event.sources.length}
			<h2>{ui('page.sources')}</h2>
			<ul class="plain sources">
				{#each event.sources as s (s.id)}
					<li><a href="/sources#{s.id}"><Citation source={s} /></a></li>
				{/each}
			</ul>
		{/if}

		<ReviewNote review={event.review} />
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
	.pkind {
		margin-left: 6px;
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		opacity: 0.75;
	}
	.facts {
		display: grid;
		grid-template-columns: 11ch 1fr;
		gap: 3px 12px;
		margin: 14px 0 4px;
		font-size: 0.9rem;
		max-width: 60ch;
	}
	.facts dt {
		color: var(--ink-soft);
		font-size: 0.76rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		padding-top: 2px;
	}
	.facts dd {
		margin: 0;
	}
	.gloss {
		color: var(--ink-soft);
		font-size: 0.85rem;
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
	.sources a {
		text-decoration: none;
	}
	.sources a:hover {
		text-decoration: underline;
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
