import { api } from '$lib/api';

export async function load({ fetch }) {
	return { network: await api.network(fetch) };
}
