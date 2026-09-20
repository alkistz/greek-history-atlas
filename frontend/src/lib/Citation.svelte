<script lang="ts">
	import type { Citation } from './types';

	interface Props {
		source: Citation;
		/** the full record, for a bibliography rather than a footnote */
		full?: boolean;
	}
	let { source, full = false }: Props = $props();

	// Built as one string so the markup cannot swallow the spaces between parts.
	const lead = $derived(source.author ? `${source.author},` : '');
	const tail = $derived.by(() => {
		let t = source.year ? ` (${source.year})` : '';
		if (full && source.publisher) t += `, ${source.publisher}`;
		if (source.locator) t += `, ${source.locator}`;
		return t;
	});
	// A URL rots; an ISBN or a DOI does not. Shown only where there is room for them.
	const stable = $derived(
		full
			? [
					source.isbn ? { label: `ISBN ${source.isbn}`, href: null } : null,
					source.doi ? { label: `doi:${source.doi}`, href: `https://doi.org/${source.doi}` } : null
				].filter((x) => x !== null)
			: []
	);
</script>

<span class="cite">
	{lead}
	<em>{source.title}</em>{tail}{#if full && source.kind !== 'book'}<span class="kind">{source.kind}</span>{/if}
	{#if full}
		{#each stable as s (s.label)}
			{#if s.href}
				<a class="id" href={s.href} rel="noreferrer">{s.label}</a>
			{:else}
				<span class="id">{s.label}</span>
			{/if}
		{/each}
		{#if source.url}
			<a class="id" href={source.url} rel="noreferrer">
				Online{#if source.accessed}<span class="acc"> · read {source.accessed}</span>{/if}
			</a>
		{/if}
	{/if}
</span>

<style>
	.cite {
		font-size: 0.88rem;
		color: var(--ink-soft);
	}
	.kind {
		margin-left: 6px;
		font-size: 0.74rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	.id {
		margin-left: 8px;
		font-family: var(--mono);
		font-size: 0.74rem;
		white-space: nowrap;
	}
	.acc {
		font-family: var(--sans);
	}
</style>
