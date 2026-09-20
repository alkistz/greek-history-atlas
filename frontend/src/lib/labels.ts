import { clampToFrame, inFrame, type Shape } from './projection';
import type { Layered } from './resolve';
import type { AtomFeature, Polity } from './types';

export interface Label {
	polity: string;
	text: string;
	x: number;
	y: number;
	/** large for the main sovereign powers, small for the rest */
	tier: 'large' | 'small';
}

/**
 * Where to put a polity's name: the first of its preferred atoms it holds, else
 * its largest. Hand-picked so "Greece" sits in the mainland rather than drifting
 * to whichever atom happens to be biggest.
 */
const PREFERRED: Record<string, string[]> = {
	'gr-kingdom': ['thessaly', 'sterea', 'peloponnese'],
	ottoman: ['macedonia-central', 'thessaly', 'epirus']
};

const LARGE_KM2 = 20_000;

/** One label per sovereign polity. Sovereign atoms are disjoint, so nothing collides. */
export function polityLabels(
	layered: Layered,
	features: AtomFeature[],
	shapes: Map<string, Shape>,
	polities: Polity[]
): Label[] {
	const area = new Map(features.map((f) => [f.properties.id, f.properties.area_km2]));
	const held = new Map<string, string[]>();
	for (const [atom, polity] of layered.sovereign) {
		if (!shapes.has(atom)) continue;
		const list = held.get(polity) ?? [];
		list.push(atom);
		held.set(polity, list);
	}

	const out: Label[] = [];
	for (const p of polities) {
		const atoms = held.get(p.id);
		if (!atoms) continue;
		const anchor =
			PREFERRED[p.id]?.find((a) => atoms.includes(a)) ??
			[...atoms].sort((a, b) => (area.get(b) ?? 0) - (area.get(a) ?? 0))[0];
		const total = atoms.reduce((sum, a) => sum + (area.get(a) ?? 0), 0);
		const centroid = shapes.get(anchor)!.centroid;
		// Outside the frame entirely: no label. Near an edge: nudge it inward.
		if (!inFrame(centroid)) continue;
		const [x, y] = clampToFrame(centroid, 48);
		out.push({
			polity: p.id,
			text: p.short?.en ?? p.name.en,
			x,
			y,
			tier: total >= LARGE_KM2 ? 'large' : 'small'
		});
	}
	return out;
}
