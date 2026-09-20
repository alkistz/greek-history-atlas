/** Dates are ISO strings, days are integers counted from an origin. Both are UTC. */

import { lang } from './lang.svelte';
import { ui } from './ui';

export const DAY = 86_400_000;

export function toDay(iso: string, origin: string): number {
	return Math.round((Date.parse(iso) - Date.parse(origin)) / DAY);
}

export function toISO(day: number, origin: string): string {
	return new Date(Date.parse(origin) + day * DAY).toISOString().slice(0, 10);
}

export function daysBetween(from: string, to: string): number {
	return toDay(to, from);
}

/** Half-open [from, to): a transfer date belongs to the new holder. `to === null` is open-ended. */
export function within(on: string, from: string, to: string | null): boolean {
	return from <= on && (to === null || on < to);
}

const formatters = new Map<string, Intl.DateTimeFormat>();

/** Built per locale and shape on first use: the month names are the reader's, not the corpus's. */
function fmt(shape: string, opts: Intl.DateTimeFormatOptions): Intl.DateTimeFormat {
	const key = `${lang.tag}:${shape}`;
	let f = formatters.get(key);
	if (!f) {
		formatters.set(key, (f = new Intl.DateTimeFormat(lang.tag, { ...opts, timeZone: 'UTC' })));
	}
	return f;
}

export function prettyDate(iso: string): string {
	return fmt('day', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(iso));
}

/** A month and a year, for the dates the corpus only knows to the month. */
export function prettyMonth(iso: string): string {
	return fmt('month', { month: 'long', year: 'numeric' }).format(new Date(iso));
}

export function year(iso: string): string {
	return iso.slice(0, 4);
}

/** A date range as prose: one day, or "from to to". */
export function prettyPeriod(period: [string, string], precision: string): string {
	if (precision === 'year' || precision === 'circa') return year(period[0]);
	const [from, to] = period;
	const oneDay = toDay(to, from) <= 1;
	if (oneDay) return prettyDate(from);
	// The stored end is exclusive; show the last day inclusive.
	return ui('date.range', { from: prettyDate(from), to: prettyDate(toISO(-1, to)) });
}
