import { api } from '$lib/api';

export async function load({ fetch }) {
	// Places too: an event with a place is drawn as a dot on the map.
	const [events, places] = await Promise.all([api.events(fetch), api.places(fetch)]);
	return { events, places };
}
