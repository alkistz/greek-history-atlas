/**
 * The overlay textures. Shared by the map and the legend swatches so both draw
 * the same thing.
 *
 * Different ANGLES, not just different colours, so the three 1941-44 zones stay
 * distinguishable in greyscale, in print, and for every colour vision type.
 */
const HATCH_ANGLE: Record<string, number> = {
	germany: 45,
	italy: 135,
	bulgaria: 0,
	britain: 90,
	// Northern Cyprus from 1974. Never on the map with the others, but kept off their
	// angles anyway, so the legend swatches read as different things.
	turkey: 160
};

export function angleFor(polityId: string): number {
	return HATCH_ANGLE[polityId] ?? 22;
}

/** Tile size and stroke in screen pixels; the map scales them to viewBox units. */
export const HATCH = { size: 7, stroke: 2.2 };
export const STIPPLE = { size: 5, r: 1.1 };
