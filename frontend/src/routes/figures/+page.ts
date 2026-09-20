import { api } from '$lib/api';

export async function load({ fetch }) {
	return { figures: await api.figures(fetch) };
}
