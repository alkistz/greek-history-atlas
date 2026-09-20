import { browser } from '$app/environment';
import type { Lang, LangText } from './types';

/**
 * Which language the corpus is read in.
 *
 * This is the content language. It chooses between the `en` and `el` halves of
 * every `LangText`, and nothing else: the two texts are translations of one
 * another, so switching never changes which entries exist or what they claim,
 * only which column of each one is shown.
 */

const STORAGE_KEY = 'lang';

/** Each language named in itself, which is how a reader looking for it will read it. */
export const ENDONYM: Record<Lang, string> = { en: 'English', el: 'Ελληνικά' };

/** BCP 47 tags for `Intl` and for the `lang` attribute, which are not the bare codes. */
const TAG: Record<Lang, string> = { en: 'en-GB', el: 'el-GR' };

/** A stored choice wins; otherwise take the browser's preference once and keep it. */
function initial(): Lang {
	if (!browser) return 'en';
	try {
		const v = localStorage.getItem(STORAGE_KEY);
		if (v === 'en' || v === 'el') return v;
	} catch {
		// private mode, blocked storage: fall through to the browser preference
	}
	const prefs = navigator.languages ?? [navigator.language];
	return prefs.some((l) => l.toLowerCase().startsWith('el')) ? 'el' : 'en';
}

class LangState {
	current = $state<Lang>(initial());

	/** There are two, so a toggle needs no list. */
	get other(): Lang {
		return this.current === 'en' ? 'el' : 'en';
	}

	get tag(): string {
		return TAG[this.current];
	}

	set(next: Lang): void {
		this.current = next;
		try {
			localStorage.setItem(STORAGE_KEY, next);
		} catch {
			// nothing to do; the choice simply will not survive a reload
		}
	}
}

export const lang = new LangState();

/**
 * The active language's text.
 *
 * Falls back to English rather than to nothing: `el` is optional on the model,
 * and a missing translation should cost the reader a sentence in the wrong
 * language rather than the sentence. Nullish in, empty string out, so an
 * optional field can be passed without a guard at every call site.
 */
export function t(text: LangText | null | undefined): string {
	if (!text) return '';
	return (lang.current === 'el' ? text.el : text.en) || text.en;
}

const collators = new Map<string, Intl.Collator>();

/**
 * Sorting by name is locale-dependent: Greek has its own alphabet, so an index
 * ordered with the English collator puts every Greek name in arrival order.
 */
export function collator(): Intl.Collator {
	const tag = lang.tag;
	let c = collators.get(tag);
	if (!c) collators.set(tag, (c = new Intl.Collator(tag)));
	return c;
}

/** Compare two `LangText` values as the reader sees them. */
export function byText(a: LangText, b: LangText): number {
	return collator().compare(t(a), t(b));
}

/**
 * A count or a measurement, grouped and pointed the way the active language
 * writes numbers: 11.878 km² in English, 11.878 km² with a comma in Greek.
 *
 * `digits` is exact rather than a maximum, so a column of coordinates stays a
 * column.
 */
export function num(n: number, digits = 0): string {
	return n.toLocaleString(lang.tag, {
		minimumFractionDigits: digits,
		maximumFractionDigits: digits
	});
}

/**
 * Both texts, for search.
 *
 * Search deliberately does not follow the switch: a reader should find Venizelos
 * by typing "Venizelos" while reading the Greek, and Σμύρνη while reading the
 * English. Spread into `matches`, which ignores the empty ones.
 */
export function both(text: LangText | null | undefined): (string | null)[] {
	return text ? [text.en, text.el] : [];
}

/**
 * The same text in the language that is not active, or '' when there is only one.
 *
 * For the few places that show a name in both at once -- Smyrna alongside
 * Σμύρνη -- where which one leads should still follow the switch.
 */
export function alt(text: LangText | null | undefined): string {
	if (!text) return '';
	const other = lang.current === 'el' ? text.en : text.el;
	return other && other !== t(text) ? other : '';
}
