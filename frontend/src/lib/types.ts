import type { FrameId } from './projection';

export type Lang = 'en' | 'el';
export type LangText = { en: string; el: string | null };

export type ControlKind =
	| 'sovereign'
	| 'occupied'
	| 'administered'
	| 'autonomous'
	| 'insurgent'
	| 'disputed'
	| 'claimed';

export interface Polity {
	id: string;
	name: LangText;
	short: LangText | null;
	kind: string;
	colour: string | null;
}

export interface ControlRow {
	atom: string;
	polity: string;
	kind: ControlKind;
	from: string;
	to: string | null;
	instrument: string | null;
	note: string | null;
}

export interface AsWritten {
	date: string;
	calendar: string;
}

/** What `/api/events` returns: enough for the ledger, no prose. */
export interface AtlasEvent {
	id: string;
	title: LangText;
	summary: LangText;
	period: [string, string];
	precision: string;
	atom: string | null;
	place: string | null;
	instrument: string | null;
	frame: FrameId;
	significance: number;
	as_written: AsWritten | null;
}

export interface Citation {
	id: string;
	kind: string;
	title: string;
	author: string | null;
	year: number | null;
	publisher: string | null;
	url: string | null;
	locator: string | null;
}

export interface ResolvedPlace {
	id: string;
	kind: string;
	lon: number;
	lat: number;
	atom: string | null;
	name: LangText;
}

export interface EventRef {
	id: string;
	title: LangText;
	period: [string, string];
}

/** What `/api/events/{id}` returns. */
export interface EventDetail extends Omit<AtlasEvent, 'place' | 'instrument'> {
	body_html: LangText | null;
	place: ResolvedPlace | null;
	instrument: { id: string; name: LangText } | null;
	figures: { id: string; name: LangText; role: string }[];
	sources: Citation[];
	related: EventRef[];
}

export interface LifeEvent {
	date: string;
	precision: string;
	place: string | null;
}

export interface FigureSummary {
	id: string;
	name: LangText;
	also_known_as: LangText[];
	born: LifeEvent | null;
	died: LifeEvent | null;
	roles: string[];
	summary: LangText;
}

export interface FigureDetail extends Omit<FigureSummary, 'born' | 'died'> {
	body_html: LangText | null;
	born: (LifeEvent & { place: ResolvedPlace | null }) | null;
	died: (LifeEvent & { place: ResolvedPlace | null }) | null;
	sources: Citation[];
	events: (EventRef & { role: string })[];
}

/** What `/api/instruments/{id}` returns. */
export interface InstrumentDetail {
	id: string;
	name: LangText;
	kind: string;
	signed: string;
	parties: string[];
	summary: LangText | null;
	sources: Citation[];
	control: ControlRow[];
	events: EventRef[];
}

export interface Meta {
	polities: Polity[];
	atoms: { id: string; name: LangText; external: boolean }[];
	instruments: { id: string; name: LangText; signed: string }[];
	epochs: string[];
	range: { from: string; to: string };
}

export interface AtomFeature {
	type: 'Feature';
	id: string;
	properties: {
		id: string;
		name: LangText;
		nuts3: string[];
		external: boolean;
		area_km2: number;
	};
	geometry: GeoJSON.MultiPolygon | GeoJSON.Polygon;
}

export interface AtomCollection {
	type: 'FeatureCollection';
	features: AtomFeature[];
}

export interface LandFeature {
	type: 'Feature';
	id: 'land';
	properties: { id: 'land'; countries: string[] };
	geometry: GeoJSON.MultiPolygon | GeoJSON.Polygon;
}

export interface ContextCollection {
	type: 'FeatureCollection';
	features: LandFeature[];
}

/** A point drawn on the map. */
export interface Pin {
	id: string;
	lon: number;
	lat: number;
	label: string;
}
