import { api } from '$lib/api';

export async function load({ fetch }) {
	// Places are referenced by id from events and from figures' births and deaths.
	// Both inverses are built here, because nothing stores them.
	const [places, events, figures] = await Promise.all([
		api.places(fetch),
		api.events(fetch),
		api.figures(fetch)
	]);
	return { places, events, figures };
}
