import { error } from '@sveltejs/kit';
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
	Meta
} from './types';

type Fetch = typeof fetch;

/**
 * Every call takes SvelteKit's `fetch` from `load`, so one relative path works
 * both ways: in production `.json` is a real file written by `make export`, and
 * in dev the Vite proxy strips the suffix and forwards to FastAPI.
 */
async function get<T>(fetch: Fetch, path: string): Promise<T> {
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
	figure: (f: Fetch, id: string) => get<FigureDetail>(f, `/api/figures/${id}`),
	instruments: (f: Fetch) => get<InstrumentSummary[]>(f, '/api/instruments'),
	instrument: (f: Fetch, id: string) => get<InstrumentDetail>(f, `/api/instruments/${id}`)
};
