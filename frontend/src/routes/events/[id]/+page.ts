import { api } from '$lib/api';

export async function load({ fetch, params }) {
	return { event: await api.event(fetch, params.id) };
}
