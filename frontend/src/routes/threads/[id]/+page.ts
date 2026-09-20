import { api } from '$lib/api';

export async function load({ fetch, params }) {
	return { thread: await api.thread(fetch, params.id) };
}
