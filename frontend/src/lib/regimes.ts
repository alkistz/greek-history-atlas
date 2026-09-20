import type { Regime } from './types';

/**
 * The regime in force on an ISO date.
 *
 * ISO-8601 strings compare lexicographically in date order, so the half-open
 * [from, to) test is a plain string comparison and needs no Date objects.
 *
 * `undefined` only before the chain begins: there was no Greek state to have a
 * form until the revolution made one. Such an event simply matches no regime
 * chip, exactly as an event with no atom matches no region chip.
 */
export function regimeOn(regimes: Regime[], iso: string): Regime | undefined {
	return regimes.find((r) => r.from <= iso && (r.to === null || iso < r.to));
}

/**
 * A chip label. Two regimes are both called "Crowned democracy" -- 1863 and
 * 1944 -- so the start year is part of the label rather than decoration.
 */
export function regimeLabel(r: Regime): string {
	return `${r.name.en} ${r.from.slice(0, 4)}`;
}
