import { api } from '$lib/api';

export async function load({ fetch }) {
	// Threads and places are what the ledger payload refers to by id only. Both are
	// small, and having them here is what lets the arc facet and the place search
	// work without a request per event.
	const [events, threads, places] = await Promise.all([
		api.events(fetch),
		api.threads(fetch),
		api.places(fetch)
	]);
	return { events, threads, places };
}
