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

/** A named group of atoms: the grain a reader thinks in, above the grain the map is drawn at. */
export interface Region {
	id: string;
	name: LangText;
	atoms: string[];
	/** a viewport hint only; `atoms` is what defines the region */
	frame: FrameId | null;
	summary: LangText | null;
}

export type RegimeKind =
	| 'revolutionary'
	| 'absolute_monarchy'
	| 'constitutional_monarchy'
	| 'republic'
	| 'dictatorship'
	| 'occupation'
	| 'interregnum';

/**
 * What kind of state Greece was, over a half-open period [from, to).
 *
 * The rows are an unbroken chain, so a date inside it resolves to exactly one
 * regime. Nothing is stored per event; see `regimeOn` in `regimes.ts`.
 */
export interface Regime {
	id: string;
	kind: RegimeKind;
	name: LangText;
	polity: string;
	from: string;
	to: string | null;
	summary: LangText | null;
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

/** What an examination concluded. `unresolved` is the one a boolean would destroy. */
export type ReviewResult = 'clean' | 'corrected' | 'unresolved';

/** One examination of an entry, by a person or by a machine. */
export interface Pass {
	date: string;
	result: ReviewResult;
	/** which languages were read; `clean` is refused without all of them */
	langs: Lang[];
	by: string | null;
	note: string | null;
}

/**
 * Two tracks that never share a column: `auto` is a cheap machine pass, `manual`
 * is a person who has read the sources. Null throughout means nobody has looked.
 */
export interface Review {
	auto: Pass | null;
	manual: Pass | null;
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
	review: Review | null;
}

export interface Citation {
	id: string;
	kind: string;
	title: string;
	author: string | null;
	year: number | null;
	publisher: string | null;
	url: string | null;
	/** a URL rots; these do not */
	isbn: string | null;
	doi: string | null;
	accessed: string | null;
	locator: string | null;
}

/** What `/api/sources` returns: the work, plus every entry that cites it. */
export interface SourceEntry extends Omit<Citation, 'locator'> {
	cited_by: {
		events: { id: string; title: LangText }[];
		figures: { id: string; title: LangText }[];
		instruments: { id: string; title: LangText }[];
	};
}

/** A name in force over a half-open period. Both ends optional. */
export interface PlaceName {
	name: LangText;
	from: string | null;
	to: string | null;
}

/** What `/api/places` returns. A point on the map; names change, the point does not. */
export interface Place {
	id: string;
	kind: string;
	lon: number;
	lat: number;
	atom: string | null;
	names: PlaceName[];
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
/** An arc an event sits on, with the step either way along it. */
export interface EventThread {
	id: string;
	name: LangText;
	previous: EventRef | null;
	next: EventRef | null;
}

/** A narrative arc in the index: no events, but its length and span. */
export interface ThreadSummary {
	id: string;
	name: LangText;
	summary: LangText;
	/** event ids in reading order; enough to filter a ledger by arc */
	events: string[];
	count: number;
	span: [string, string];
}

export interface ThreadDetail {
	id: string;
	name: LangText;
	summary: LangText;
	events: (EventRef & { significance: number })[];
	span: [string, string];
}

export interface EventDetail extends Omit<AtlasEvent, 'place' | 'instrument'> {
	body_html: LangText | null;
	place: ResolvedPlace | null;
	instrument: { id: string; name: LangText } | null;
	figures: { id: string; name: LangText; role: string }[];
	sources: Citation[];
	related: EventRef[];
	threads: EventThread[];
}

export interface LifeEvent {
	date: string;
	precision: string;
	place: string | null;
	/** the date as a source gives it, when that is Old Style */
	as_written: AsWritten | null;
}

export interface FigureSummary {
	id: string;
	name: LangText;
	also_known_as: LangText[];
	born: LifeEvent | null;
	died: LifeEvent | null;
	roles: string[];
	summary: LangText;
	review: Review | null;
}

export interface FigureDetail extends Omit<FigureSummary, 'born' | 'died'> {
	body_html: LangText | null;
	born: (LifeEvent & { place: ResolvedPlace | null }) | null;
	died: (LifeEvent & { place: ResolvedPlace | null }) | null;
	sources: Citation[];
	events: (EventRef & { role: string })[];
}

/** What `/api/instruments` returns: the list, without the control rows. */
export interface InstrumentSummary {
	id: string;
	name: LangText;
	kind: string;
	signed: string;
	parties: string[];
	summary: LangText | null;
	/** the instrument's own text. Not a citation: a treaty is not a work about itself. */
	text_url: string | null;
	review: Review | null;
}

/** What `/api/instruments/{id}` returns. */
export interface InstrumentDetail extends InstrumentSummary {
	sources: Citation[];
	control: ControlRow[];
	events: EventRef[];
}

export interface Meta {
	polities: Polity[];
	atoms: { id: string; name: LangText; external: boolean }[];
	instruments: { id: string; name: LangText; signed: string }[];
	regions: Region[];
	regimes: Regime[];
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
