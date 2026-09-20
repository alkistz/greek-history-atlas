<script lang="ts">
	import type { Citation } from './types';

	let { source }: { source: Citation } = $props();

	// Built as one string so the markup cannot swallow the spaces between parts.
	const text = $derived.by(() => {
		const parts: string[] = [];
		if (source.author) parts.push(`${source.author},`);
		return parts.join(' ');
	});
	const tail = $derived.by(() => {
		let t = source.year ? ` (${source.year})` : '';
		if (source.locator) t += `, ${source.locator}`;
		return t;
	});
</script>

<span class="cite">{text} <em>{source.title}</em>{tail}</span>

<style>
	.cite {
		font-size: 0.88rem;
		color: var(--ink-soft);
	}
</style>
