import { within } from './time';
import type { ControlRow, Polity } from './types';

export interface Layered {
	/** atom id -> polity id, the base fill */
	sovereign: Map<string, string>;
	/** polity id -> atom ids, drawn as hatch ON TOP of the sovereign fill */
	occupied: Map<string, string[]>;
	/** polity id -> atom ids, drawn as stipple. Never a flat fill. */
	insurgent: Map<string, string[]>;
	/** polity id -> atom ids, an administering power over someone else's sovereignty */
	administered: Map<string, string[]>;
}

export function covers(row: ControlRow, on: string): boolean {
	return within(on, row.from, row.to);
}

function push(map: Map<string, string[]>, key: string, value: string) {
	const list = map.get(key);
	if (list) list.push(value);
	else map.set(key, [value]);
}

/** The picture on one date. `autonomous`, `disputed` and `claimed` have no renderer yet. */
export function resolveOn(rows: ControlRow[], on: string): Layered {
	const out: Layered = {
		sovereign: new Map(),
		occupied: new Map(),
		insurgent: new Map(),
		administered: new Map()
	};
	for (const r of rows) {
		if (!covers(r, on)) continue;
		if (r.kind === 'sovereign') out.sovereign.set(r.atom, r.polity);
		else if (r.kind === 'occupied') push(out.occupied, r.polity, r.atom);
		else if (r.kind === 'insurgent') push(out.insurgent, r.polity, r.atom);
		else if (r.kind === 'administered') push(out.administered, r.polity, r.atom);
	}
	return out;
}

/** Every atom that has any row on the date, so an empty outline is never drawn. */
export function heldAtoms(layered: Layered): Set<string> {
	const held = new Set(layered.sovereign.keys());
	for (const map of [layered.occupied, layered.insurgent, layered.administered]) {
		for (const atoms of map.values()) for (const a of atoms) held.add(a);
	}
	return held;
}

/** Every row covering one atom on one date, sovereign first. For the tooltip. */
export function rowsFor(rows: ControlRow[], atomId: string, on: string): ControlRow[] {
	const order = ['sovereign', 'administered', 'occupied', 'insurgent'];
	return rows
		.filter((r) => r.atom === atomId && covers(r, on))
		.sort((a, b) => order.indexOf(a.kind) - order.indexOf(b.kind));
}

/** Instrument ids of rows that begin exactly on the date. */
export function instrumentsOn(rows: ControlRow[], on: string): string[] {
	const ids = new Set<string>();
	for (const r of rows) if (r.from === on && r.instrument) ids.add(r.instrument);
	return [...ids];
}

/** Atoms whose sovereign holder differs between two pictures. Used to flash changes. */
export function changedAtoms(before: Layered, after: Layered): Set<string> {
	const out = new Set<string>();
	for (const atom of new Set([...before.sovereign.keys(), ...after.sovereign.keys()])) {
		if (before.sovereign.get(atom) !== after.sovereign.get(atom)) out.add(atom);
	}
	return out;
}

export type Role = 'sovereign' | 'administering' | 'occupying' | 'in revolt';

export interface LegendEntry {
	polity: Polity;
	role: Role;
}

/**
 * One legend row per (polity, role) present on the date, in a fixed role order.
 * `visible` limits it to atoms inside the current frame, so a Cyprus row does not
 * appear under a map of the Aegean.
 */
export function legendEntries(
	layered: Layered,
	polities: Polity[],
	visible?: (atom: string) => boolean
): LegendEntry[] {
	const byId = new Map(polities.map((p) => [p.id, p]));
	const rolesOf = new Map<string, Set<Role>>();
	const add = (id: string, role: Role) => {
		const set = rolesOf.get(id) ?? new Set<Role>();
		set.add(role);
		rolesOf.set(id, set);
	};
	const shown = (atoms: string[]) => !visible || atoms.some(visible);
	for (const [atom, p] of layered.sovereign) if (shown([atom])) add(p, 'sovereign');
	for (const [p, atoms] of layered.administered) if (shown(atoms)) add(p, 'administering');
	for (const [p, atoms] of layered.occupied) if (shown(atoms)) add(p, 'occupying');
	for (const [p, atoms] of layered.insurgent) if (shown(atoms)) add(p, 'in revolt');

	const order: Role[] = ['sovereign', 'administering', 'occupying', 'in revolt'];
	const out: LegendEntry[] = [];
	for (const role of order) {
		for (const p of polities) {
			if (rolesOf.get(p.id)?.has(role)) out.push({ polity: byId.get(p.id)!, role });
		}
	}
	return out;
}
