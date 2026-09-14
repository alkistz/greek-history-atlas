<script lang="ts">
	import Atlas from '$lib/Atlas.svelte';
	import { buildPaths } from '$lib/projection';
	import { instrumentsOn, resolveOn } from '$lib/resolve';

	let { data } = $props();

	const DAY = 86_400_000;
	const START = Date.UTC(1821, 0, 1);
	const END = Date.UTC(1975, 0, 1);
	const MAX_DAY = Math.round((END - START) / DAY);

	const toISO = (day: number) => new Date(START + day * DAY).toISOString().slice(0, 10);
	const toDay = (iso: string) => Math.round((Date.parse(iso) - START) / DAY);

	// Path strings depend only on geometry, never on the date, so these recompute
	// only if the corpus itself changes. Scrubbing then costs a fill lookup per
	// atom and nothing more.
	const paths = $derived(buildPaths(data.atoms.features));
	const areaOf = $derived(
		new Map(data.atoms.features.map((f) => [f.properties.id, f.properties.area_km2]))
	);
	const epochDays = $derived(data.meta.epochs.map(toDay));

	let day = $state(toDay('1913-08-10'));
	let showOccupation = $state(true);
	let highlight = $state<string | null>(null);

	const date = $derived(toISO(day));
	const layered = $derived(resolveOn(data.control, date));

	const greekArea = $derived.by(() => {
		let km2 = 0;
		for (const [atom, polity] of layered.sovereign) {
			if (polity.startsWith('gr-')) km2 += areaOf.get(atom) ?? 0;
		}
		return km2;
	});

	const instruments = $derived(instrumentsOn(data.control, date));

	const activePolities = $derived.by(() => {
		const ids = new Set<string>([
			...layered.sovereign.values(),
			...layered.occupied.keys(),
			...layered.insurgent.keys(),
			...layered.administered.keys()
		]);
		return data.meta.polities.filter((p) => ids.has(p.id));
	});

	const roleOf = $derived.by(() => {
		const m = new Map<string, string>();
		for (const p of layered.sovereign.values()) m.set(p, 'sovereign');
		for (const p of layered.administered.keys()) m.set(p, 'administering');
		for (const p of layered.occupied.keys()) m.set(p, 'occupying');
		for (const p of layered.insurgent.keys()) m.set(p, 'in revolt');
		return m;
	});

	const sortedEvents = $derived(
		[...data.events].sort((a, b) => a.period[0].localeCompare(b.period[0]))
	);

	function step(dir: -1 | 1) {
		const next =
			dir === 1
				? epochDays.find((d) => d > day)
				: [...epochDays].reverse().find((d) => d < day);
		if (next !== undefined) day = next;
	}

	const fmt = new Intl.DateTimeFormat('en-GB', {
		day: 'numeric',
		month: 'long',
		year: 'numeric',
		timeZone: 'UTC'
	});
	const pretty = $derived(fmt.format(new Date(START + day * DAY)));
</script>

<div class="shell">
	<header>
		<h1>after1821</h1>
		<p class="tagline">
			An atlas of Greek history. The map redraws as control of territory changes.
		</p>
	</header>

	<main>
		<section class="mapcol">
			<div class="mapframe">
				<Atlas
					features={data.atoms.features}
					{paths}
					polities={data.meta.polities}
					control={data.control}
					{date}
					{showOccupation}
					{highlight}
				/>
			</div>

			<div class="caption">
				<div class="date">{pretty}</div>
				<div class="figures">
					<span class="km2">{greekArea.toLocaleString('en-GB', { maximumFractionDigits: 0 })} km²</span>
					<span class="km2-label">Greek sovereign territory</span>
				</div>
			</div>

			{#if instruments.length}
				<p class="instrument">In force from today: {instruments.join('; ')}</p>
			{/if}

			<div class="scrubber">
				<button onclick={() => step(-1)} title="Previous change" aria-label="Previous change">
					&#8592;
				</button>
				<input
					type="range"
					min="0"
					max={MAX_DAY}
					bind:value={day}
					aria-label="Date"
					list="epochs"
				/>
				<datalist id="epochs">
					{#each epochDays as d (d)}<option value={d}></option>{/each}
				</datalist>
				<button onclick={() => step(1)} title="Next change" aria-label="Next change">
					&#8594;
				</button>
				<span class="year">{date.slice(0, 4)}</span>
			</div>

			<div class="controls">
				<label>
					<input type="checkbox" bind:checked={showOccupation} />
					Show occupation
				</label>
			</div>

			<ul class="legend">
				{#each activePolities as p (p.id)}
					<li>
						<span class="swatch" style:background={p.colour}></span>
						<span class="pname">{p.name.en}</span>
						<span class="prole">{roleOf.get(p.id)}</span>
					</li>
				{/each}
			</ul>

			{#if layered.insurgent.size}
				<p class="note">Stippled areas are in armed revolt. There was no recognised frontier.</p>
			{/if}
			{#if layered.occupied.size}
				<p class="note">
					Hatching marks occupation layered over sovereignty, not replacing it. The Greek state
					remained sovereign throughout.
				</p>
			{/if}
		</section>

		<aside class="ledger">
			<h2>Events</h2>
			<ol>
				{#each sortedEvents as e (e.id)}
					{@const active = e.period[0] <= date && date < e.period[1]}
					{@const past = e.period[1] <= date}
					<li class:active class:past>
						<button
							onclick={() => {
								day = toDay(e.period[0]);
								highlight = e.atom;
							}}
						>
							<span class="etime">{e.period[0].slice(0, 4)}</span>
							<span class="etitle">{e.title.en}</span>
						</button>
						{#if active}
							<p class="esummary">{e.summary.en}</p>
							{#if e.as_written}
								<p class="eold">
									Old Style: {e.as_written.date}
								</p>
							{/if}
						{/if}
					</li>
				{/each}
			</ol>
		</aside>
	</main>

	<footer>
		<p>
			Boundaries from Eurostat Nuts2json (2021, 03M), dissolved into atoms. v0 uses whole NUTS3
			units, so several historical frontiers are approximated. See README for the list.
		</p>
	</footer>
</div>

<style>
	.shell {
		max-width: 1320px;
		margin: 0 auto;
		padding-block: 28px 48px;
		padding-inline: 20px;
	}

	header h1 {
		font-family: var(--serif);
		font-size: 2.1rem;
		font-weight: 600;
		margin: 0;
		letter-spacing: -0.01em;
	}
	.tagline {
		margin: 4px 0 0;
		color: var(--ink-soft);
		max-width: 60ch;
	}

	main {
		display: grid;
		grid-template-columns: minmax(0, 1.9fr) minmax(0, 1fr);
		gap: 28px;
		margin-top: 24px;
		align-items: start;
	}

	.mapframe {
		background: var(--panel);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 8px;
	}

	.caption {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 16px;
		flex-wrap: wrap;
		margin-top: 14px;
	}
	.date {
		font-family: var(--serif);
		font-size: 1.4rem;
	}
	.figures {
		display: flex;
		align-items: baseline;
		gap: 8px;
	}
	.km2 {
		font-family: var(--mono);
		font-size: 1.05rem;
	}
	.km2-label {
		color: var(--ink-soft);
		font-size: 0.85rem;
	}

	.instrument {
		margin: 6px 0 0;
		color: var(--accent);
		font-size: 0.9rem;
	}

	.scrubber {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-top: 14px;
	}
	.scrubber input[type='range'] {
		flex: 1;
		accent-color: var(--accent);
		min-width: 0;
	}
	.scrubber button {
		font: inherit;
		background: var(--panel);
		color: var(--ink);
		border: 1px solid var(--rule);
		border-radius: var(--radius);
		padding: 2px 10px;
		cursor: pointer;
	}
	.scrubber button:hover {
		border-color: var(--accent);
	}
	.year {
		font-family: var(--mono);
		min-width: 4ch;
	}

	.controls {
		margin-top: 8px;
		color: var(--ink-soft);
		font-size: 0.88rem;
	}
	.controls label {
		display: inline-flex;
		gap: 6px;
		align-items: center;
		cursor: pointer;
	}

	.legend {
		list-style: none;
		padding: 0;
		margin: 16px 0 0;
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
		gap: 4px 14px;
	}
	.legend li {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 0.86rem;
	}
	.swatch {
		width: 13px;
		height: 13px;
		border-radius: 2px;
		flex: none;
		border: 1px solid #0002;
	}
	.prole {
		color: var(--ink-soft);
		font-size: 0.78rem;
	}

	.note {
		margin: 10px 0 0;
		color: var(--ink-soft);
		font-size: 0.84rem;
		max-width: 68ch;
	}

	.ledger h2 {
		font-family: var(--serif);
		font-size: 1.15rem;
		font-weight: 600;
		margin: 0 0 8px;
	}
	.ledger ol {
		list-style: none;
		margin: 0;
		padding: 0;
		border-top: 1px solid var(--rule);
	}
	.ledger li {
		border-bottom: 1px solid var(--rule);
	}
	.ledger button {
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
	.ledger button:hover .etitle {
		color: var(--accent);
	}
	.ledger .past button {
		color: var(--ink);
	}
	.ledger .active button {
		color: var(--ink);
		font-weight: 600;
	}
	.etime {
		font-family: var(--mono);
		font-size: 0.82rem;
		flex: none;
		padding-top: 1px;
	}
	.esummary {
		margin: 0 0 10px;
		padding-left: 46px;
		font-size: 0.88rem;
		color: var(--ink-soft);
	}
	.eold {
		margin: -6px 0 10px;
		padding-left: 46px;
		font-size: 0.78rem;
		font-family: var(--mono);
		color: var(--ink-soft);
	}

	footer {
		margin-top: 36px;
		padding-top: 14px;
		border-top: 1px solid var(--rule);
		color: var(--ink-soft);
		font-size: 0.8rem;
	}
	footer p {
		margin: 0;
		max-width: 80ch;
	}

	@media (max-width: 900px) {
		main {
			grid-template-columns: 1fr;
		}
	}
</style>
