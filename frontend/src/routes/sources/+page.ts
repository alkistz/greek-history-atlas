import { api } from '$lib/api';

export async function load({ fetch }) {
	return { sources: await api.sources(fetch) };
}
