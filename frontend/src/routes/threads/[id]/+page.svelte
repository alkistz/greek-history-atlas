<script lang="ts">
	import Significance from '$lib/Significance.svelte';
	import Strip, { type StripMark } from '$lib/Strip.svelte';
	import { t } from '$lib/lang.svelte';
	import { daysBetween, toDay, year } from '$lib/time';
	import { ui } from '$lib/ui';
	import { atlasHref } from '$lib/viewstate';

	let { data } = $props();
	const thread = $derived(data.thread);
	const years = $derived(
		`${thread.span[0].slice(0, 4)}–${thread.span[1].slice(0, 4)}`
	);

	const origin = $derived(data.meta.range.from);
	const maxDay = $derived(daysBetween(origin, data.meta.range.to));
	const marks = $derived.by((): StripMark[] =>
		thread.events.map((e) => ({
			id: e.id,
			day: toDay(e.period[0], origin),
			title: `${year(e.period[0])} — ${t(e.title)}`,
			significance: e.significance,
			href: `/events/${e.id}`
		}))
	);
</script>

<svelte:head>
	<title>{ui('page.title', { page: t(thread.name), site: ui('site.name') })}</title>
	<meta name="description" content={t(thread.summary)} />
</svelte:head>

<article>
	<p class="crumb"><a href="/threads">{ui('page.threads')}</a> <span class="muted">{years}</span></p>
	<h1>{t(thread.name)}</h1>
	<p class="summary">{t(thread.summary)}</p>

	<!-- The arc on the ruler: how its events fall across the two centuries. -->
	<div class="strip">
		<p class="label">{ui('thread.strip')}</p>
		<Strip
			{origin}
			{maxDay}
			{marks}
			span={[toDay(thread.span[0], origin), toDay(thread.span[1], origin)]}
		/>
	</div>

	<p class="crumb">
		<a href="/events?threads={thread.id}">{ui('thread.see', { n: thread.events.length })}</a>
	</p>

	<ol class="arc">
		{#each thread.events as e, i (e.id)}
			<li>
				<span class="when">{e.period[0].slice(0, 4)}</span>
				<div>
					<a class="title" href="/events/{e.id}">{t(e.title)}</a>
					<p class="meta">
						<span class="muted">{ui('thread.step', { i: i + 1, n: thread.events.length })}</span>
						<Significance significance={e.significance} compact />
						<a href={atlasHref({ on: e.period[0], event: e.id })}>{ui('events.openatlas')}</a>
					</p>
				</div>
			</li>
		{/each}
	</ol>
</article>

<style>
	article {
		max-width: 76ch;
	}
	.crumb {
		font-size: 0.85rem;
		margin: 0 0 6px;
	}
	.muted {
		color: var(--ink-soft);
	}
	h1 {
		font-size: 1.9rem;
		margin: 0 0 6px;
	}
	.summary {
		color: var(--ink-soft);
		margin: 0 0 18px;
	}
	.strip {
		margin: 0 0 18px;
		padding: 10px 12px 6px;
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius-lg);
	}
	.label {
		margin: 0 0 4px;
		color: var(--ink-soft);
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
	}
	.arc {
		list-style: none;
		padding: 0;
		margin: 0;
		/* The steps are joined: a thin line runs down the years, as on a route map. */
		border-left: 2px solid var(--rule);
		margin-left: 2.5ch;
	}
	.arc li {
		position: relative;
		display: flex;
		gap: 14px;
		padding: 10px 0 10px 16px;
	}
	.arc li::before {
		content: '';
		position: absolute;
		left: -6px;
		top: 16px;
		width: 10px;
		height: 10px;
		border-radius: 50%;
		background: var(--accent);
		border: 2px solid var(--ground);
	}
	.when {
		flex: 0 0 5ch;
		color: var(--ink-soft);
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.85rem;
		padding-top: 2px;
	}
	.title {
		font-weight: 600;
	}
	.meta {
		display: flex;
		align-items: center;
		gap: 14px;
		flex-wrap: wrap;
		margin: 3px 0 0;
		font-size: 0.85rem;
	}
</style>
