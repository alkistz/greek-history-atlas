import { api } from '$lib/api';

export async function load({ fetch, params }) {
	return { figure: await api.figure(fetch, params.id) };
}
