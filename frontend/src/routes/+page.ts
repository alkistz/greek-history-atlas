import { redirect } from '@sveltejs/kit';
import { api } from '$lib/api';
import { ATLAS_PATH, VIEW_KEYS } from '$lib/viewstate';

export async function load({ fetch, url }) {
	// The atlas lived here until the front page took its place. A link shared
	// before then carries a view in its query string; send it on, view intact.
	if (VIEW_KEYS.some((k) => url.searchParams.has(k))) {
		redirect(308, `${ATLAS_PATH}${url.search}`);
	}

	// The lists are fetched for what the front page shows of them: the turning
	// points, the arcs and the size of each index. The atlas loads the events too,
	// so the second visit costs nothing.
	const [events, threads, figures, places, sources] = await Promise.all([
		api.events(fetch),
		api.threads(fetch),
		api.figures(fetch),
		api.places(fetch),
		api.sources(fetch)
	]);
	return {
		events,
		threads,
		counts: {
			events: events.length,
			threads: threads.length,
			figures: figures.length,
			places: places.length,
			sources: sources.length
		}
	};
}
