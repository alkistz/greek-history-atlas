<!--
	Every failed load lands here. The status decides the wording; the message
	SvelteKit carries (the API path that 404'd) stays in the console, where it is
	useful, rather than on the page, where it is noise.
-->
<script lang="ts">
	import { page } from '$app/state';
	import { ui } from '$lib/ui';

	const missing = $derived(page.status === 404);
</script>

<svelte:head>
	<title
		>{ui('page.title', {
			page: ui(missing ? 'error.404.title' : 'error.other.title'),
			site: ui('site.name')
		})}</title
	>
</svelte:head>

<section class="error">
	<p class="status">{page.status}</p>
	<h1>{ui(missing ? 'error.404.title' : 'error.other.title')}</h1>
	<p class="body">{ui(missing ? 'error.404.body' : 'error.other.body')}</p>
	<p class="links">
		<a href="/">{ui('error.back.atlas')} →</a>
		<a href="/events">{ui('error.back.events')} →</a>
	</p>
</section>

<style>
	.error {
		max-width: 60ch;
		padding-block: 24px 48px;
	}
	.status {
		margin: 0;
		font-family: var(--mono);
		font-size: 0.8rem;
		letter-spacing: 0.08em;
		color: var(--ink-soft);
	}
	h1 {
		margin: 4px 0 12px;
		font-size: 2rem;
	}
	.body {
		margin: 0 0 20px;
		color: var(--ink-soft);
	}
	.links {
		display: flex;
		flex-wrap: wrap;
		gap: 8px 24px;
		margin: 0;
	}
</style>
