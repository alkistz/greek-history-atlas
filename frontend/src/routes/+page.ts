import type { AtomCollection, AtlasEvent, ControlRow, Meta } from '$lib/types';

// v0 renders in the browser only. SSR and prerendering are deliberately deferred:
// the question this version exists to answer is whether the map reads correctly,
// not how it is delivered.
export const ssr = false;

export async function load({ fetch }) {
	const [atoms, meta, control, events] = await Promise.all([
		fetch('/api/atoms').then((r) => r.json() as Promise<AtomCollection>),
		fetch('/api/meta').then((r) => r.json() as Promise<Meta>),
		fetch('/api/control').then((r) => r.json() as Promise<ControlRow[]>),
		fetch('/api/events').then((r) => r.json() as Promise<AtlasEvent[]>)
	]);
	return { atoms, meta, control, events };
}
