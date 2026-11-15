// One copy of the app shell per route, each with its own title, description and
// Open Graph tags, so a link pasted into a chat or a post previews as the page it
// points at rather than as the site.
//
// The app is client-rendered and the language lives in the reader's browser, not
// in the URL, so a page cannot be prerendered in "its" language: there is none. The
// shells carry the English text, the tags are all a link preview reads, and the
// app takes over in whichever language the reader chose. The layout removes the
// shell's tags once it has rendered its own (`data-shell`).
//
// Run after `vite build`. Reads the static API the build already contains.
//
// Every known route is now a real file, so the host can answer anything else with
// 404.html and a 404 status (`not_found_handling: "404-page"` in wrangler.jsonc).

import fs from 'node:fs';
import path from 'node:path';
import { STRINGS } from '../src/lib/strings.ts';

// The public origin, for the tags that must be absolute (og:url, og:image, canonical).
// Without it those are left out and the rest still work.
const SITE = (process.env.SITE_URL ?? '').replace(/\/$/, '');
const BUILD = path.resolve(import.meta.dirname, '..', 'build');
const API = path.join(BUILD, 'api');

const en = (key) => STRINGS[key].en;
const SITE_NAME = en('site.name');
const titled = (page) => en('page.title').replace('{page}', page).replace('{site}', SITE_NAME);

const esc = (s) =>
	s.replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');

/** Whitespace collapsed and cut at a word near `n` characters, as previews show it. */
function clip(text, n = 200) {
	const s = text.replace(/\s+/g, ' ').trim();
	if (s.length <= n) return s;
	const cut = s.slice(0, n - 1);
	return cut.slice(0, cut.lastIndexOf(' ')).replace(/[,;:.]$/, '') + '…';
}

function head({ title, description, route, type = 'website', noindex = false }) {
	const meta = [
		['name', 'description', description],
		['property', 'og:site_name', SITE_NAME],
		['property', 'og:title', title],
		['property', 'og:description', description],
		['property', 'og:type', type],
		['property', 'og:locale', 'en_GB'],
		['property', 'og:locale:alternate', 'el_GR'],
		['name', 'twitter:card', SITE ? 'summary_large_image' : 'summary']
	];
	if (SITE) {
		meta.push(['property', 'og:url', SITE + route]);
		meta.push(['property', 'og:image', `${SITE}/og.png`]);
		meta.push(['property', 'og:image:width', '1200']);
		meta.push(['property', 'og:image:height', '630']);
	}
	if (noindex) meta.push(['name', 'robots', 'noindex']);
	const tags = meta.map(([attr, key, value]) => `<meta ${attr}="${key}" content="${esc(value)}" data-shell>`);
	if (SITE && !noindex) tags.push(`<link rel="canonical" href="${SITE + route}" data-shell>`);
	// No data-shell on the title: the app sets document.title, which writes into it.
	return [`<title>${esc(title)}</title>`, ...tags].map((t) => `\t\t${t}`).join('\n');
}

const shell = fs.readFileSync(path.join(BUILD, 'index.html'), 'utf8');
if (shell.includes('data-shell')) throw new Error('build/index.html already has shell tags');

function write(route, file, tags) {
	const html = shell.replace('</head>', `${head({ route, ...tags })}\n\t</head>`);
	const out = path.join(BUILD, file);
	fs.mkdirSync(path.dirname(out), { recursive: true });
	fs.writeFileSync(out, html);
}

const read = (name) => JSON.parse(fs.readFileSync(path.join(API, `${name}.json`), 'utf8'));
let count = 0;

// The host serves /events from events.html without redirecting to /events/, which
// is what SvelteKit's links ask for (trailingSlash: 'never').
write('/', 'index.html', { title: SITE_NAME, description: en('site.description') });
count++;
for (const key of ['atlas', 'events', 'threads', 'figures', 'network', 'instruments', 'places', 'sources']) {
	const description = STRINGS[`${key}.description`]?.en ?? en('site.description');
	write(`/${key}`, `${key}.html`, { title: titled(en(`page.${key}`)), description });
	count++;
}

const details = [
	['events', (e) => e.title],
	['figures', (f) => f.name],
	['instruments', (i) => i.name],
	['threads', (t) => t.name]
];
for (const [kind, name] of details) {
	for (const entry of read(kind)) {
		write(`/${kind}/${entry.id}`, `${kind}/${entry.id}.html`, {
			title: titled(name(entry).en),
			description: clip(entry.summary.en),
			type: 'article'
		});
		count++;
	}
}

write('/404', '404.html', {
	title: titled(en('error.404.title')),
	description: en('site.description'),
	noindex: true
});

console.log(`shells: wrote ${count} pages and 404.html${SITE ? ` for ${SITE}` : ' (no SITE_URL)'}`);
