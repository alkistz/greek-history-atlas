<script lang="ts">
	import { FRAMES, type FrameId } from './projection';

	interface Props {
		frame: FrameId;
	}
	let { frame = $bindable() }: Props = $props();

	const LABELS: Record<FrameId, string> = {
		greece: 'Greece',
		'aegean-east': 'Eastern Aegean',
		epirus: 'Epirus',
		cyprus: 'Cyprus'
	};
	const order = Object.keys(LABELS).filter((f) => f in FRAMES) as FrameId[];
</script>

<div class="frames" role="group" aria-label="Map frame">
	<span class="caption">Frame</span>
	{#each order as f (f)}
		<button class:on={frame === f} aria-pressed={frame === f} onclick={() => (frame = f)}>
			{LABELS[f]}
		</button>
	{/each}
</div>

<style>
	.frames {
		display: flex;
		align-items: center;
		gap: 6px;
		flex-wrap: wrap;
	}
	.caption {
		color: var(--ink-soft);
		font-size: 0.78rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		margin-right: 2px;
	}
	button {
		font: inherit;
		font-size: 0.82rem;
		background: var(--panel);
		color: var(--ink-soft);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 2px 9px;
		cursor: pointer;
	}
	button:hover {
		color: var(--accent);
		border-color: var(--accent);
	}
	button.on {
		color: var(--accent);
		border-color: var(--accent);
		background: transparent;
	}
</style>
