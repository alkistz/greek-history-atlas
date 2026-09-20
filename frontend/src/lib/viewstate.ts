import { replaceState } from '$app/navigation';
import { FRAMES, type FrameId } from './projection';

/**
 * Everything the atlas page shows is a function of these four values, so they
 * live in the query string: a view can be linked to, and an event page can send
 * the reader back to the map on the day the event happened.
 */
export interface View {
	/** ISO date, or null to mean "the page's own default" */
	on: string | null;
	frame: FrameId;
	/** the event open in the ledger */
	event: string | null;
	occupation: boolean;
}

export const DEFAULTS: View = { on: null, frame: 'greece', event: null, occupation: true };

const ISO = /^\d{4}-\d{2}-\d{2}$/;
const isFrame = (s: string | null): s is FrameId => s !== null && s in FRAMES;

export function parseView(url: URL, fallback: string): View {
	const p = url.searchParams;
	const on = p.get('on');
	const frame = p.get('frame');
	return {
		on: on && ISO.test(on) ? on : fallback,
		frame: isFrame(frame) ? frame : 'greece',
		event: p.get('event'),
		occupation: p.get('occupation') !== '0'
	};
}

/** Only what differs from the default, so a plain view stays a plain URL. */
function toParams(v: View): string {
	const p = new URLSearchParams();
	if (v.on) p.set('on', v.on);
	if (v.frame !== DEFAULTS.frame) p.set('frame', v.frame);
	if (v.event) p.set('event', v.event);
	if (v.occupation !== DEFAULTS.occupation) p.set('occupation', '0');
	return p.toString();
}

/** A link into the atlas. Used by event pages and anything else off the map. */
export function atlasHref(v: Partial<View>): string {
	const q = toParams({ ...DEFAULTS, ...v });
	return q ? `/?${q}` : '/';
}

let pending: ReturnType<typeof setTimeout> | undefined;

/**
 * Mirrors the view into the address bar. `replaceState`, not `pushState`:
 * dragging the timeline would otherwise bury the previous page under hundreds
 * of history entries. Debounced because a drag emits a value per frame.
 */
export function writeView(v: View, wait = 150): void {
	clearTimeout(pending);
	pending = setTimeout(() => {
		const url = new URL(location.href);
		const next = toParams(v);
		if (url.searchParams.toString() === next) return;
		url.search = next;
		replaceState(url, {});
	}, wait);
}
