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
 * ONE projection, fitted to a fixed lon/lat box that holds every frame, never to
 * the geometry of the selected date. Fitting to the data would make the map
 * rescale as territory changes, which destroys the whole illusion the atlas
 * exists for.
 *
 * Every path is therefore drawn once, in "world" units. A frame is a rectangle
 * in that space, and the map shows a frame by pointing its viewBox at it; moving
 * between frames, or zooming into one, is a camera move over paths that never
 * change. The vocabulary is shared with the backend (`app/core/models.py`).
 */
export type FrameId = 'greece' | 'cyprus' | 'aegean-east' | 'epirus';

/** [west, south, east, north] in degrees. */
export const FRAMES: Record<FrameId, [number, number, number, number]> = {
	greece: [18.4, 34.2, 30.4, 42.4],
	cyprus: [31.6, 34.3, 35.2, 36.0],
	'aegean-east': [23.0, 36.2, 29.6, 42.2],
	epirus: [19.0, 38.6, 22.6, 41.2]
};

/** The box every frame sits inside. */
const WORLD_BBOX: [number, number, number, number] = [18.4, 34.2, 35.2, 42.4];

/** The world canvas, in the units every path and rect below is expressed in. */
export const REF_W = 1200;
export const REF_H = 760;

export interface Rect {
	x: number;
	y: number;
	w: number;
	h: number;
}

export const WORLD: Rect = { x: 0, y: 0, w: REF_W, h: REF_H };

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

let projection: GeoProjection | undefined;

export function worldProjection(): GeoProjection {
	if (!projection) {
		const [w, s, e, n] = WORLD_BBOX;
		projection = geoConicConformal()
			// d3's default parallels are [30, 30], wrong for this latitude band.
			.parallels([s + (n - s) * 0.2, n - (n - s) * 0.2])
			.rotate([-(w + e) / 2, 0])
			.fitExtent(
				[
					[0, 0],
					[REF_W, REF_H]
				],
				bboxPolygon(WORLD_BBOX)
			);
	}
	return projection;
}

let pathBuilder: GeoPath | undefined;

/**
 * `.digits(2)` rounds path output to 0.01 units. It trims the SVG substantially and,
 * once this renders server side, it is what makes the server and client strings
 * identical despite transcendental functions differing in the last bit.
 */
export function worldPath(): GeoPath {
	if (!pathBuilder) pathBuilder = geoPath(worldProjection()).digits(2);
	return pathBuilder;
}

const frameRects = new Map<FrameId, Rect>();

/** Where a frame's lon/lat box lands on the world canvas. */
export function frameRect(frame: FrameId): Rect {
	let r = frameRects.get(frame);
	if (!r) {
		const [[x0, y0], [x1, y1]] = worldPath().bounds({
			type: 'Feature',
			properties: {},
			geometry: bboxPolygon(FRAMES[frame])
		} as GeoJSON.Feature);
		r = { x: x0, y: y0, w: x1 - x0, h: y1 - y0 };
		frameRects.set(frame, r);
	}
	return r;
}

/**
 * The smallest rect of the given aspect ratio that contains `rect`, centred on it,
 * with a little breathing room. This is what the camera points at to "show a frame".
 */
export function fitRect(rect: Rect, aspect: number, pad = 0.03): Rect {
	const w0 = rect.w * (1 + pad * 2);
	const h0 = rect.h * (1 + pad * 2);
	const w = Math.max(w0, h0 * aspect);
	const h = w / aspect;
	return { x: rect.x + rect.w / 2 - w / 2, y: rect.y + rect.h / 2 - h / 2, w, h };
}

export interface Shape {
	/** SVG path data */
	d: string;
	/** projected centroid, in world units */
	centroid: [number, number];
}

/**
 * Path strings depend on the geometry alone, so build them once per feature array.
 * Scrubbing then costs a fill lookup per atom and nothing else, and a camera
 * move costs nothing at all.
 */
const shapeCache = new WeakMap<AtomFeature[], Map<string, Shape>>();

export function buildShapes(features: AtomFeature[]): Map<string, Shape> {
	let shapes = shapeCache.get(features);
	if (shapes) return shapes;

	const path = worldPath();
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
	shapeCache.set(features, shapes);
	return shapes;
}

/** Whether a world point lies inside a rect, with a small margin. */
export function inRect([x, y]: [number, number], r: Rect, margin = 0): boolean {
	return x >= r.x + margin && x <= r.x + r.w - margin && y >= r.y + margin && y <= r.y + r.h - margin;
}

/** Clamp a world point into a rect so a label near the edge stays legible. */
export function clampToRect([x, y]: [number, number], r: Rect, margin: number): [number, number] {
	return [
		Math.min(Math.max(x, r.x + margin), r.x + r.w - margin),
		Math.min(Math.max(y, r.y + margin), r.y + r.h - margin)
	];
}

/** One path string for a standalone feature such as the land backdrop. */
export function pathOf(geometry: GeoJSON.Polygon | GeoJSON.MultiPolygon): string {
	return (
		worldPath()({
			type: 'Feature',
			properties: {},
			geometry: reverseRings(geometry)
		} as GeoJSON.Feature) ?? ''
	);
}

/** Project a lon/lat point into world units, or null if it is outside the projection's domain. */
export function project(lon: number, lat: number): [number, number] | null {
	return worldProjection()([lon, lat]);
}

/** A predicate for atoms whose centroid falls inside a rect: a frame, or what the camera shows. */
export function visibleIn(features: AtomFeature[], rect: Rect): (atom: string) => boolean {
	const shapes = buildShapes(features);
	return (atom) => {
		const s = shapes.get(atom);
		return s !== undefined && inRect(s.centroid, rect);
	};
}
