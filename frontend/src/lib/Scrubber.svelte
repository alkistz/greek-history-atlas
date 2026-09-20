<script lang="ts">
	interface Props {
		/** days from the origin */
		day: number;
		maxDay: number;
		/** days on which the map changes, for snapping and tick marks */
		epochDays: number[];
		year: string;
	}
	let { day = $bindable(), maxDay, epochDays, year }: Props = $props();
	const uid = $props.id();

	function step(dir: -1 | 1) {
		const next =
			dir === 1 ? epochDays.find((d) => d > day) : [...epochDays].reverse().find((d) => d < day);
		if (next !== undefined) day = next;
	}
</script>

<div class="scrubber">
	<button onclick={() => step(-1)} title="Previous change" aria-label="Previous change">&#8592;</button>
	<input type="range" min="0" max={maxDay} bind:value={day} aria-label="Date" list="{uid}-epochs" />
	<datalist id="{uid}-epochs">
		{#each epochDays as d (d)}<option value={d}></option>{/each}
	</datalist>
	<button onclick={() => step(1)} title="Next change" aria-label="Next change">&#8594;</button>
	<span class="year">{year}</span>
</div>

<style>
	.scrubber {
		display: flex;
		align-items: center;
		gap: 10px;
	}
	input[type='range'] {
		flex: 1;
		accent-color: var(--accent);
		min-width: 0;
	}
	button {
		font: inherit;
		background: var(--panel);
		color: var(--ink);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 2px 10px;
		cursor: pointer;
	}
	button:hover {
		border-color: var(--accent);
	}
	.year {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		min-width: 4ch;
	}
</style>
