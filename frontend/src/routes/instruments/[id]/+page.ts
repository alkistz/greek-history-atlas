import { api } from '$lib/api';

export async function load({ fetch, params }) {
	return { instrument: await api.instrument(fetch, params.id) };
}
