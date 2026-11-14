import { error } from '@sveltejs/kit';
import { dev } from '$app/environment';
import type {
	AtlasEvent,
	AtomCollection,
	ContextCollection,
	ControlRow,
	EventDetail,
	FigureDetail,
	FigureSummary,
	InstrumentDetail,
	InstrumentSummary,
	Meta,
	Place,
	Regime,
	Region,
	SourceEntry,
	ThreadDetail,
	ThreadSummary
} from './types';

type Fetch = typeof fetch;

/**
 * Every call takes SvelteKit's `fetch` from `load`, so one relative path works
 * both ways: in production `.json` is a real file written by `make export`, and
 * in dev the Vite proxy strips the suffix and forwards to FastAPI.
 */
/**
 * The deployed corpus is a set of static files that cannot change while a tab is
 * open, so each is fetched and parsed once per visit; moving between pages then
 * waits on nothing. In dev the API is live and the YAML is being edited, so
 * nothing is kept.
 */
const cache = new Map<string, Promise<unknown>>();

function get<T>(fetch: Fetch, path: string): Promise<T> {
	if (dev) return load<T>(fetch, path);
	let hit = cache.get(path) as Promise<T> | undefined;
	if (!hit) {
		hit = load<T>(fetch, path);
		cache.set(path, hit);
		// A failure is not kept: the next navigation tries again.
		hit.catch(() => cache.delete(path));
	}
	return hit;
}

async function load<T>(fetch: Fetch, path: string): Promise<T> {
	const r = await fetch(`${path}.json`);
	if (!r.ok) error(r.status, `${path}: ${r.statusText}`);
	// A static host answers an unknown path with the app shell rather than a 404,
	// so an id that does not exist arrives here as HTML with a 200. Without this
	// it would surface as a JSON parse error instead of a not-found page.
	if (!r.headers.get('content-type')?.includes('application/json')) {
		error(404, `${path}: not found`);
	}
	return r.json() as Promise<T>;
}

export const api = {
	atoms: (f: Fetch) => get<AtomCollection>(f, '/api/atoms'),
	context: (f: Fetch) => get<ContextCollection>(f, '/api/context'),
	meta: (f: Fetch) => get<Meta>(f, '/api/meta'),
	control: (f: Fetch) => get<ControlRow[]>(f, '/api/control'),
	events: (f: Fetch) => get<AtlasEvent[]>(f, '/api/events'),
	event: (f: Fetch, id: string) => get<EventDetail>(f, `/api/events/${id}`),
	figures: (f: Fetch) => get<FigureSummary[]>(f, '/api/figures'),
	regions: (f: Fetch) => get<Region[]>(f, '/api/regions'),
	regimes: (f: Fetch) => get<Regime[]>(f, '/api/regimes'),
	threads: (f: Fetch) => get<ThreadSummary[]>(f, '/api/threads'),
	thread: (f: Fetch, id: string) => get<ThreadDetail>(f, `/api/threads/${id}`),
	figure: (f: Fetch, id: string) => get<FigureDetail>(f, `/api/figures/${id}`),
	instruments: (f: Fetch) => get<InstrumentSummary[]>(f, '/api/instruments'),
	instrument: (f: Fetch, id: string) => get<InstrumentDetail>(f, `/api/instruments/${id}`),
	places: (f: Fetch) => get<Place[]>(f, '/api/places'),
	sources: (f: Fetch) => get<SourceEntry[]>(f, '/api/sources')
};
