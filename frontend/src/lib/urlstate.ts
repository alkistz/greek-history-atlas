import { replaceState } from '$app/navigation';

let pending: ReturnType<typeof setTimeout> | undefined;

/**
 * Mirror state into the query string.
 *
 * `replaceState`, not `pushState`: typing in a search box would otherwise bury the
 * previous page under one history entry per keystroke. Debounced for the same reason.
 */
export function replaceParams(params: URLSearchParams, wait = 150): void {
	clearTimeout(pending);
	pending = setTimeout(() => {
		const url = new URL(location.href);
		const next = params.toString();
		if (url.searchParams.toString() === next) return;
		url.search = next;
		replaceState(url, {});
	}, wait);
}

/** Anything empty is dropped, so an unfiltered view stays a clean URL. */
export function params(entries: Record<string, string | string[]>): URLSearchParams {
	const p = new URLSearchParams();
	for (const [key, value] of Object.entries(entries)) {
		const s = Array.isArray(value) ? value.join(',') : value;
		if (s) p.set(key, s);
	}
	return p;
}

/** A comma-separated list parameter, e.g. `?roles=monarch,statesman`. */
export function list(url: URL, key: string): string[] {
	return (url.searchParams.get(key) ?? '').split(',').filter(Boolean);
}

/** Case-insensitive substring matching over several fields, ignoring empty ones. */
export function matches(query: string, ...fields: (string | null | undefined)[]): boolean {
	const q = query.trim().toLowerCase();
	if (!q) return true;
	return fields.some((f) => f != null && f.toLowerCase().includes(q));
}
