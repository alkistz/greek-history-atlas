import { t } from './lang.svelte';
import { STRINGS } from './strings';
import type { LangText } from './types';

export type UiKey = keyof typeof STRINGS;

const TABLE: Record<string, LangText> = STRINGS;

function fill(text: string, vars?: Record<string, string | number>): string {
	if (!vars) return text;
	let out = text;
	for (const [name, value] of Object.entries(vars)) {
		out = out.replaceAll(`{${name}}`, String(value));
	}
	return out;
}

/** One interface string in the active language, with its placeholders filled. */
export function ui(key: UiKey, vars?: Record<string, string | number>): string {
	return fill(t(TABLE[key]), vars);
}

/**
 * A vocabulary that arrives as an id rather than as text: place kinds, figure
 * roles, the kinds of control.
 *
 * An unknown id falls back to itself, so a value added to the corpus before it
 * is added here shows up as its own name rather than as a blank. The ids are
 * English words, which is what makes that fallback readable at all.
 */
export function term(group: string, id: string | number | null | undefined): string {
	if (id === null || id === undefined || id === '') return '';
	const entry = TABLE[`${group}.${id}`];
	return entry ? t(entry) : String(id);
}

/** The same, with a capital: chip captions and the starts of sentences. */
export function Term(group: string, id: string | number | null | undefined): string {
	const s = term(group, id);
	return s ? s[0].toUpperCase() + s.slice(1) : s;
}
