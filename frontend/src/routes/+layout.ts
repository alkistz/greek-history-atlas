import { api } from '$lib/api';

// Rendered in the browser only. SSR and prerendering are deliberately deferred.
export const ssr = false;

/** Geometry, polities and control rows are loaded once and shared by every page. */
export async function load({ fetch }) {
	const [atoms, context, meta, control] = await Promise.all([
		api.atoms(fetch),
		api.context(fetch),
		api.meta(fetch),
		api.control(fetch)
	]);
	return { atoms, land: context.features[0], meta, control };
}
