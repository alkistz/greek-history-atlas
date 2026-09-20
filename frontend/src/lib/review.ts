import type { Pass, Review, ReviewResult } from './types';

/**
 * Reading the two review tracks for display.
 *
 * The rules here are the model's, not new ones: `auto` is a cheap machine pass
 * and `manual` is a person, they never merge, and absent means nobody has looked.
 */

/** Which track a shown pass came from. A person outranks the machine. */
export type Track = 'manual' | 'auto';

export interface Shown {
	track: Track;
	pass: Pass;
}

/** The strongest statement anyone has made about an entry, or null if nobody has. */
export function strongest(review: Review | null | undefined): Shown | null {
	if (!review) return null;
	if (review.manual) return { track: 'manual', pass: review.manual };
	if (review.auto) return { track: 'auto', pass: review.auto };
	return null;
}

/**
 * Whether a pass was checked against published sources rather than only read.
 *
 * `result` answers what was found and not how hard anyone looked, so depth is
 * carried informally in `by` -- see FOLLOWUPS.md §5, which proposes giving it a
 * field of its own. Until it has one, this matches the same marker the report
 * greps for, and nothing else is inferred from the prose.
 */
export const SOURCED_MARKER = 'verified against public sources';

export function isSourced(review: Review | null | undefined): boolean {
	const shown = strongest(review);
	return shown?.pass.by?.includes(SOURCED_MARKER) ?? false;
}

/**
 * Facet ids for one entry: its result, plus the two orthogonal claims that the
 * result enum cannot carry.
 */
export function reviewTags(review: Review | null | undefined): string[] {
	const shown = strongest(review);
	if (!shown) return ['none'];
	const tags: string[] = [shown.pass.result];
	if (isSourced(review)) tags.push('sourced');
	if (shown.track === 'manual') tags.push('manual');
	return tags;
}

/** In the order they should be offered, so the chip row reads from weakest claim to strongest. */
export const REVIEW_FACETS = ['none', 'unresolved', 'corrected', 'clean', 'sourced', 'manual'];

export const REVIEW_LABELS: Record<string, string> = {
	none: 'Not reviewed',
	unresolved: 'Unresolved',
	corrected: 'Corrected',
	clean: 'Read clean',
	sourced: 'Checked against sources',
	manual: 'Reviewed by a person'
};

export const REVIEW_HINTS: Record<string, string> = {
	none: 'Nobody has looked at this entry yet.',
	unresolved:
		'Someone looked hard and the sources do not agree. The note says what could not be settled.',
	corrected: 'A pass found something wrong and fixed it. The note says what.',
	clean: 'Read in every language the entry has, and they agree.',
	sourced: 'Checked against published sources, not only read for internal consistency.',
	manual: 'A person who has read the sources, rather than a machine pass.'
};

/** Tone drives the badge colour. Nothing here is "good": an unreviewed entry is the default. */
export type Tone = 'muted' | 'warn' | 'ok' | 'strong';

export function toneOf(review: Review | null | undefined): Tone {
	const shown = strongest(review);
	if (!shown) return 'muted';
	if (shown.pass.result === 'unresolved') return 'warn';
	if (shown.track === 'manual') return 'strong';
	if (isSourced(review)) return 'ok';
	return 'muted';
}

/** The short label for a badge: what was concluded, and by which kind of pass. */
export function badgeLabel(review: Review | null | undefined): string {
	const shown = strongest(review);
	if (!shown) return 'Not reviewed';
	const who = shown.track === 'manual' ? 'Reviewed' : 'Machine pass';
	if (shown.pass.result === 'unresolved') return `${who} · unresolved`;
	if (shown.pass.result === 'corrected') return `${who} · corrected`;
	return isSourced(review) ? `${who} · sourced` : who;
}

export const LANG_NAMES: Record<string, string> = { en: 'English', el: 'Greek' };

export function langList(pass: Pass): string {
	return pass.langs.map((l) => LANG_NAMES[l] ?? l).join(' and ');
}

/** Counts per facet across a list, so a chip can show how many it would leave. */
export function tally<T>(rows: T[], of: (row: T) => Review | null | undefined): Map<string, number> {
	const out = new Map<string, number>();
	for (const row of rows) {
		for (const tag of reviewTags(of(row))) out.set(tag, (out.get(tag) ?? 0) + 1);
	}
	return out;
}

export type { Review, ReviewResult };
