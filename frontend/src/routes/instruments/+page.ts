import { api } from '$lib/api';

export async function load({ fetch }) {
	return { instruments: await api.instruments(fetch) };
}
