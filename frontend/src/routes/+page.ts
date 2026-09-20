import { api } from '$lib/api';

export async function load({ fetch }) {
	return { events: await api.events(fetch) };
}
