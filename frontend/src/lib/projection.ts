import { geoConicConformal, geoPath, type GeoPath, type GeoProjection } from 'd3-geo';
import type { AtomFeature } from './types';

/**
 * d3-geo reads rings with the opposite winding to RFC 7946.
 *
 * GeoJSON says an exterior ring is counter-clockwise. d3 treats a counter-clockwise
 * ring as the COMPLEMENT of itself, so an RFC 7946 island becomes "the whole world
 * except this island". The symptom is a map filled edge to edge with one colour.
 *
 * data/atoms.geojson is deliberately standards compliant, because the geodesic area
 * calculation in the backend depends on that winding. So the adapter lives here.
 */
export function reverseRings<T extends GeoJSON.Polygon | GeoJSON.MultiPolygon>(geom: T): T {
	if (geom.type === 'Polygon') {
		return { ...geom, coordinates: geom.coordinates.map((r) => [...r].reverse()) };
	}
	return {
		...geom,
		coordinates: geom.coordinates.map((poly) => poly.map((r) => [...r].reverse()))
	};
}

/**
 * The projection is fitted to a FIXED lon/lat box, never to the geometry of the
 * currently selected date. Fitting to the data would make the map rescale as
 * territory changes, which destroys the whole illusion the atlas exists for.
 *
 * There are a few such boxes, called frames. `greece` is the default and contains
 * every atom except Cyprus. An event may name another frame; nothing else does.
 * The vocabulary is shared with the backend (`app/core/models.py`).
 */
export type FrameId = 'greece' | 'cyprus' | 'aegean-east' | 'epirus';

/** [west, south, east, north] in degrees. */
export const FRAMES: Record<FrameId, [number, number, number, number]> = {
	greece: [18.4, 34.2, 30.4, 42.4],
	cyprus: [31.6, 34.3, 35.2, 36.0],
	'aegean-east': [23.0, 36.2, 29.6, 42.2],
	epirus: [19.0, 38.6, 22.6, 41.2]
};

export const REF_W = 760;
export const REF_H = 680;
export const VIEWBOX = `0 0 ${REF_W} ${REF_H}`;
const INSET = 10;

/** A bbox as a clockwise polygon, for the winding reason above. */
function bboxPolygon([w, s, e, n]: [number, number, number, number]): GeoJSON.Polygon {
	return {
		type: 'Polygon',
		coordinates: [
			[
				[w, s],
				[w, n],
				[e, n],
				[e, s],
				[w, s]
			]
		]
	};
}

const projections = new Map<FrameId, GeoProjection>();

export function projectionFor(frame: FrameId): GeoProjection {
	let p = projections.get(frame);
	if (!p) {
		const [w, s, e, n] = FRAMES[frame];
		p = geoConicConformal()
			// d3's default parallels are [30, 30], wrong for this latitude band.
			.parallels([s + (n - s) * 0.2, n - (n - s) * 0.2])
			.rotate([-(w + e) / 2, 0])
			.fitExtent(
				[
					[INSET, INSET],
					[REF_W - INSET, REF_H - INSET]
				],
				bboxPolygon(FRAMES[frame])
			);
		projections.set(frame, p);
	}
	return p;
}

const paths = new Map<FrameId, GeoPath>();

/**
 * `.digits(2)` rounds path output to 0.01 units. It trims the SVG substantially and,
 * once this renders server side, it is what makes the server and client strings
 * identical despite transcendental functions differing in the last bit.
 */
export function pathFor(frame: FrameId): GeoPath {
	let p = paths.get(frame);
	if (!p) {
		p = geoPath(projectionFor(frame)).digits(2);
		paths.set(frame, p);
	}
	return p;
}

export interface Shape {
	/** SVG path data */
	d: string;
	/** projected centroid, in viewBox units */
	centroid: [number, number];
}

/**
 * Path strings do not depend on the date, only on the geometry and the frame, so
 * build them once per (features, frame). Scrubbing then costs a fill lookup per
 * atom and nothing else.
 */
const shapeCache = new WeakMap<AtomFeature[], Map<FrameId, Map<string, Shape>>>();

export function buildShapes(features: AtomFeature[], frame: FrameId): Map<string, Shape> {
	let perFrame = shapeCache.get(features);
	if (!perFrame) {
		perFrame = new Map();
		shapeCache.set(features, perFrame);
	}
	let shapes = perFrame.get(frame);
	if (shapes) return shapes;

	const path = pathFor(frame);
	shapes = new Map();
	for (const f of features) {
		const feature = {
			type: 'Feature',
			properties: {},
			geometry: reverseRings(f.geometry)
		} as GeoJSON.Feature;
		const d = path(feature);
		if (d) shapes.set(f.properties.id, { d, centroid: path.centroid(feature) });
	}
	perFrame.set(frame, shapes);
	return shapes;
}

/** Whether a projected point lies inside the drawn viewBox, with a small margin. */
export function inFrame([x, y]: [number, number], margin = 0): boolean {
	return x >= margin && x <= REF_W - margin && y >= margin && y <= REF_H - margin;
}

/** Clamp a projected point into the viewBox so a label near the edge stays legible. */
export function clampToFrame([x, y]: [number, number], margin: number): [number, number] {
	return [
		Math.min(Math.max(x, margin), REF_W - margin),
		Math.min(Math.max(y, margin), REF_H - margin)
	];
}

/** One path string for a standalone feature such as the land backdrop. */
export function pathOf(geometry: GeoJSON.Polygon | GeoJSON.MultiPolygon, frame: FrameId): string {
	return (
		pathFor(frame)({
			type: 'Feature',
			properties: {},
			geometry: reverseRings(geometry)
		} as GeoJSON.Feature) ?? ''
	);
}

/** Project a lon/lat point into viewBox units, or null if it is outside the frame's domain. */
export function project(lon: number, lat: number, frame: FrameId): [number, number] | null {
	return projectionFor(frame)([lon, lat]);
}

/** A predicate for atoms whose centroid falls inside the frame. */
export function visibleIn(features: AtomFeature[], frame: FrameId): (atom: string) => boolean {
	const shapes = buildShapes(features, frame);
	return (atom) => {
		const s = shapes.get(atom);
		return s !== undefined && inFrame(s.centroid);
	};
}
