<script lang="ts">
	import { angleFor, HATCH, STIPPLE } from './patterns';
	import type { Role } from './resolve';

	interface Props {
		colour: string;
		role: Role;
		polityId: string;
	}
	let { colour, role, polityId }: Props = $props();
	const uid = $props.id();
	const size = 14;
</script>

<!-- Draws its own tiny pattern rather than borrowing the map's, so the legend
     works without a map on the page and ignores the map's scale factor. -->
<svg class="swatch" width={size} height={size} viewBox="0 0 {size} {size}" aria-hidden="true">
	<defs>
		{#if role === 'occupying' || role === 'administering'}
			<pattern
				id="{uid}-p"
				patternUnits="userSpaceOnUse"
				width={HATCH.size}
				height={HATCH.size}
				patternTransform="rotate({angleFor(polityId)})"
			>
				<line x1="0" y1="0" x2="0" y2={HATCH.size} stroke={colour} stroke-width={HATCH.stroke} />
			</pattern>
		{:else if role === 'in revolt'}
			<pattern id="{uid}-p" patternUnits="userSpaceOnUse" width={STIPPLE.size} height={STIPPLE.size}>
				<circle cx={STIPPLE.size * 0.28} cy={STIPPLE.size * 0.28} r={STIPPLE.r} fill={colour} />
				<circle cx={STIPPLE.size * 0.78} cy={STIPPLE.size * 0.78} r={STIPPLE.r} fill={colour} />
			</pattern>
		{/if}
	</defs>
	<rect width={size} height={size} class="base" />
	{#if role === 'sovereign'}
		<rect width={size} height={size} fill={colour} />
	{:else}
		<rect width={size} height={size} fill="url(#{uid}-p)" />
	{/if}
</svg>

<style>
	.swatch {
		display: block;
		border-radius: 2px;
		border: 1px solid #0002;
		flex: none;
	}
	.base {
		fill: var(--land);
	}
</style>
