import { api } from '$lib/api';

export async function load({ fetch }) {
	return { threads: await api.threads(fetch) };
}
