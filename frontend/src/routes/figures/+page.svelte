<script lang="ts">
	import { year } from '$lib/time';

	let { data } = $props();
</script>

<svelte:head>
	<title>Figures — after1821</title>
</svelte:head>

<h1>Figures</h1>
<p class="lead">The people behind the events, in order of birth.</p>

<ol class="figures">
	{#each data.figures as f (f.id)}
		<li>
			<span class="dates">
				{f.born ? year(f.born.date) : '?'}–{f.died ? year(f.died.date) : ''}
			</span>
			<div>
				<a href="/figures/{f.id}">{f.name.en}</a>
				<span class="roles">{f.roles.join(', ')}</span>
				<p>{f.summary.en}</p>
			</div>
		</li>
	{/each}
</ol>

<style>
	h1 {
		font-size: 1.9rem;
		margin: 0 0 4px;
	}
	.lead {
		color: var(--ink-soft);
		margin: 0 0 20px;
	}
	.figures {
		list-style: none;
		padding: 0;
		margin: 0;
		max-width: 76ch;
		border-top: 1px solid var(--rule);
	}
	.figures li {
		display: grid;
		grid-template-columns: 9ch 1fr;
		gap: 12px;
		padding: 12px 0;
		border-bottom: 1px solid var(--rule);
	}
	.dates {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
		font-size: 0.85rem;
		color: var(--ink-soft);
		padding-top: 3px;
	}
	.figures a {
		font-family: var(--serif);
		font-size: 1.1rem;
		font-weight: 600;
		text-decoration: none;
		color: var(--ink);
	}
	.figures a:hover {
		color: var(--accent);
	}
	.roles {
		margin-left: 8px;
		color: var(--ink-soft);
		font-size: 0.82rem;
	}
	.figures p {
		margin: 4px 0 0;
		color: var(--ink-soft);
		font-size: 0.92rem;
	}
</style>
