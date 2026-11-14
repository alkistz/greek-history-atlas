import { getContext, setContext } from 'svelte';

/**
 * The heights of the header and the draft notice, measured by the layout.
 *
 * On the atlas both float over the map, so the page needs them twice: in CSS,
 * to place its own panels beneath them, and in script, to tell the map's
 * camera how much of the window they cover.
 */
export interface Chrome {
	header: number;
	notice: number;
}

const KEY = Symbol('chrome');

export function provideChrome(): Chrome {
	const chrome = $state<Chrome>({ header: 0, notice: 0 });
	setContext(KEY, chrome);
	return chrome;
}

export function useChrome(): Chrome {
	return getContext<Chrome>(KEY) ?? { header: 0, notice: 0 };
}
