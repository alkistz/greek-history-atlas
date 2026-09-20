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
	instrument: (f: Fetch, id: string) => get<InstrumentDetail>(f, `/api/instruments/${id}`)
};
