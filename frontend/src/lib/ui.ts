import { t } from './lang.svelte';
import type { LangText } from './types';

/**
 * Every word of the interface, in both languages.
 *
 * The corpus carries its own translations in `LangText`; this is the chrome
 * around it -- headings, labels, empty states -- which has nowhere else to live.
 * The two languages sit side by side in one entry for the same reason the corpus
 * puts them in one file: a missing translation is then visible while the English
 * is being written, rather than discovered later as a gap in a parallel table.
 *
 * `{name}` in a value is a placeholder filled by `ui`'s second argument. Whole
 * sentences are one entry rather than assembled from fragments, because word
 * order is not shared between the two languages.
 *
 * Counts are never singular here: the smallest thread has five events, the
 * fold opens past eight, and the totals are corpus-wide, so no entry needs a
 * plural rule. Add one with the first string that can say "1".
 */
const STRINGS = {
	// The site itself
	'site.name': { en: 'Greek History Atlas', el: 'Άτλας Ελληνικής Ιστορίας' },
	'site.description': {
		en: 'An interactive atlas of Greek history from 1821, where the map redraws as territorial control changes.',
		el: 'Ένας διαδραστικός άτλας της ελληνικής ιστορίας από το 1821, όπου ο χάρτης ξαναχαράσσεται καθώς αλλάζει ο έλεγχος του εδάφους.'
	},
	'site.footer': {
		en: 'Boundaries from Eurostat Nuts2json (2021, 03M), dissolved into atoms. Neighbouring land is drawn at present-day extent and uncoloured. Several historical frontiers are approximated; see the README for the list.',
		el: 'Τα όρια προέρχονται από το Eurostat Nuts2json (2021, 03M), συγχωνευμένα σε άτομα. Τα γειτονικά εδάφη σχεδιάζονται στη σημερινή τους έκταση και χωρίς χρώμα. Αρκετά ιστορικά σύνορα αποδίδονται κατά προσέγγιση· ο κατάλογος βρίσκεται στο README.'
	},

	// Section names, used in the nav, the page titles and the source index alike
	'page.atlas': { en: 'Atlas', el: 'Άτλας' },
	'page.events': { en: 'Events', el: 'Γεγονότα' },
	'page.threads': { en: 'Threads', el: 'Νήματα' },
	'page.figures': { en: 'Figures', el: 'Πρόσωπα' },
	'page.instruments': { en: 'Instruments', el: 'Πράξεις' },
	'page.places': { en: 'Places', el: 'Τόποι' },
	'page.sources': { en: 'Sources', el: 'Πηγές' },
	'page.title': { en: '{page} — {site}', el: '{page} — {site}' },

	// The two switches in the header
	'theme.light': { en: 'Light', el: 'Φωτεινό' },
	'theme.dark': { en: 'Dark', el: 'Σκοτεινό' },
	'theme.current': { en: 'Theme: {name}', el: 'Θέμα: {name}' },
	'theme.switch': { en: 'Theme: {name}. Switch to {other}.', el: 'Θέμα: {name}. Αλλαγή σε {other}.' },
	'lang.current': { en: 'Language: {name}', el: 'Γλώσσα: {name}' },
	'lang.switch': {
		en: 'Language: {name}. Switch to {other}.',
		el: 'Γλώσσα: {name}. Αλλαγή σε {other}.'
	},

	// The standing notice. Not dismissible, so it is worth saying well in both.
	'draft.badge': { en: 'AI draft', el: 'Προσχέδιο AI' },
	'draft.summary': {
		en: 'The history in this atlas was researched and written by an AI model, not by a historian. Dates, figures and attributions may be wrong.',
		el: 'Η ιστορία σε αυτόν τον άτλαντα ερευνήθηκε και γράφτηκε από μοντέλο τεχνητής νοημοσύνης, όχι από ιστορικό. Ημερομηνίες, αριθμοί και αποδόσεις μπορεί να είναι λανθασμένα.'
	},
	'draft.checked': {
		en: 'Every entry has been read in both English and Greek and checked for internal consistency — dates, arithmetic, and whether the instruments and people it names are the right ones. That is not the same as being verified. Only a small number of entries have been checked against published sources, and none has yet been reviewed by a person.',
		el: 'Κάθε καταχώριση έχει διαβαστεί στα αγγλικά και στα ελληνικά και έχει ελεγχθεί ως προς την εσωτερική της συνέπεια — ημερομηνίες, αριθμητικά και το αν οι πράξεις και τα πρόσωπα που αναφέρει είναι τα σωστά. Αυτό δεν ισοδυναμεί με επαλήθευση. Μόνο λίγες καταχωρίσεις έχουν ελεγχθεί έναντι δημοσιευμένων πηγών, και καμία δεν έχει ελεγχθεί ακόμη από άνθρωπο.'
	},
	'draft.cite': {
		en: 'Each event, figure and treaty cites its sources; follow them before relying on anything here. This is a prototype, and the corpus is a first draft.',
		el: 'Κάθε γεγονός, πρόσωπο και συνθήκη παραπέμπει στις πηγές του· ανατρέξτε σε αυτές πριν βασιστείτε σε οτιδήποτε εδώ. Πρόκειται για πρωτότυπο, και το σώμα κειμένων είναι πρώτη γραφή.'
	},

	// Filtering, shared by every index
	'filter.placeholder': { en: 'Search…', el: 'Αναζήτηση…' },
	'filter.clear': { en: 'Clear', el: 'Καθαρισμός' },
	'filter.filters': { en: 'Filters', el: 'Φίλτρα' },
	'filter.searchAria': { en: 'Search {noun}', el: 'Αναζήτηση: {noun}' },
	'filter.shown': { en: '{shown} of {total} {noun}', el: '{shown} από {total} {noun}' },
	'filter.total': { en: '{total} {noun}', el: '{total} {noun}' },
	'noun.events': { en: 'events', el: 'γεγονότα' },
	'noun.threads': { en: 'threads', el: 'νήματα' },
	'noun.figures': { en: 'figures', el: 'πρόσωπα' },
	'noun.instruments': { en: 'instruments', el: 'πράξεις' },
	'noun.places': { en: 'places', el: 'τόποι' },
	'noun.works': { en: 'works', el: 'έργα' },

	// Facet group captions
	'facet.region': { en: 'Region', el: 'Περιοχή' },
	'facet.thread': { en: 'Thread', el: 'Νήμα' },
	'facet.regime': { en: 'Regime', el: 'Πολίτευμα' },
	'facet.significance': { en: 'Significance', el: 'Βαρύτητα' },
	'facet.review': { en: 'Review', el: 'Έλεγχος' },
	'facet.role': { en: 'Role', el: 'Ιδιότητα' },
	'facet.born': { en: 'Born', el: 'Γέννηση' },
	'facet.kind': { en: 'Kind', el: 'Είδος' },
	'facet.party': { en: 'Party', el: 'Μέρη' },
	'facet.text': { en: 'Own text', el: 'Πρωτότυπο κείμενο' },
	'facet.frame': { en: 'Frame', el: 'Πλαίσιο' },
	'facet.count': { en: '{label} ({n})', el: '{label} ({n})' },

	// What an event changed
	'sig.1': { en: 'Minor', el: 'Ήσσονος σημασίας' },
	'sig.2': { en: 'Notable', el: 'Αξιοσημείωτο' },
	'sig.3': { en: 'Consequential', el: 'Με συνέπειες' },
	'sig.4': { en: 'Major', el: 'Μείζον' },
	'sig.5': { en: 'Changed the state', el: 'Άλλαξε το κράτος' },
	'sig.title': { en: 'Significance {n} of 5 — {label}', el: 'Βαρύτητα {n} στα 5 — {label}' },
	'sig.sr': { en: 'Significance {n} of 5, {label}', el: 'Βαρύτητα {n} στα 5, {label}' },

	// The review tracks
	'review.none': { en: 'Not reviewed', el: 'Χωρίς έλεγχο' },
	'review.unresolved': { en: 'Unresolved', el: 'Ανεπίλυτο' },
	'review.corrected': { en: 'Corrected', el: 'Διορθωμένο' },
	'review.clean': { en: 'Read clean', el: 'Διαβάστηκε καθαρό' },
	'review.sourced': { en: 'Checked against sources', el: 'Ελεγμένο έναντι πηγών' },
	'review.manual': { en: 'Reviewed by a person', el: 'Ελεγμένο από άνθρωπο' },
	'review.hint.none': {
		en: 'Nobody has looked at this entry yet.',
		el: 'Κανείς δεν έχει εξετάσει ακόμη αυτή την καταχώριση.'
	},
	'review.hint.unresolved': {
		en: 'Someone looked hard and the sources do not agree. The note says what could not be settled.',
		el: 'Κάποιος εξέτασε προσεκτικά και οι πηγές δεν συμφωνούν. Η σημείωση λέει τι δεν μπόρεσε να κριθεί.'
	},
	'review.hint.corrected': {
		en: 'A pass found something wrong and fixed it. The note says what.',
		el: 'Ένας έλεγχος βρήκε κάτι λάθος και το διόρθωσε. Η σημείωση λέει τι.'
	},
	'review.hint.clean': {
		en: 'Read in every language the entry has, and they agree.',
		el: 'Διαβάστηκε σε κάθε γλώσσα που έχει η καταχώριση, και συμφωνούν.'
	},
	'review.hint.sourced': {
		en: 'Checked against published sources, not only read for internal consistency.',
		el: 'Ελέγχθηκε έναντι δημοσιευμένων πηγών, όχι μόνο ως προς την εσωτερική συνέπεια.'
	},
	'review.hint.manual': {
		en: 'A person who has read the sources, rather than a machine pass.',
		el: 'Άνθρωπος που έχει διαβάσει τις πηγές, όχι μηχανικός έλεγχος.'
	},
	'review.by.manual': { en: 'Reviewed', el: 'Ελεγμένο' },
	'review.by.auto': { en: 'Machine pass', el: 'Μηχανικός έλεγχος' },
	'review.suffix.unresolved': { en: '{who} · unresolved', el: '{who} · ανεπίλυτο' },
	'review.suffix.corrected': { en: '{who} · corrected', el: '{who} · διορθωμένο' },
	'review.suffix.sourced': { en: '{who} · sourced', el: '{who} · με πηγές' },
	'review.compact.none': { en: 'unreviewed', el: 'ανέλεγκτο' },
	'review.tip': { en: '{who}, {date}', el: '{who}, {date}' },
	'review.tip.by': { en: '{who}, {date} — {by}', el: '{who}, {date} — {by}' },

	// The per-entry review note
	'reviewnote.heading': {
		en: 'How this entry was checked',
		el: 'Πώς ελέγχθηκε αυτή η καταχώριση'
	},
	'reviewnote.none': {
		en: 'Nobody has looked at this entry yet. It is machine-written and unverified; follow the sources before relying on it.',
		el: 'Κανείς δεν έχει εξετάσει ακόμη αυτή την καταχώριση. Είναι γραμμένη από μηχανή και ανεπαλήθευτη· ανατρέξτε στις πηγές πριν βασιστείτε σε αυτήν.'
	},
	'reviewnote.track.manual': { en: 'Read by a person', el: 'Διαβάστηκε από άνθρωπο' },
	'reviewnote.track.auto': { en: 'Machine pass', el: 'Μηχανικός έλεγχος' },
	'reviewnote.said.clean': {
		en: 'read in full, and the languages agree',
		el: 'διαβάστηκε ολόκληρη, και οι γλώσσες συμφωνούν'
	},
	'reviewnote.said.corrected': {
		en: 'something was wrong and has been fixed',
		el: 'κάτι ήταν λάθος και έχει διορθωθεί'
	},
	'reviewnote.said.unresolved': {
		en: 'could not be settled from the sources reached',
		el: 'δεν μπόρεσε να κριθεί από τις πηγές που εξετάστηκαν'
	},
	'reviewnote.readin': { en: 'Read in {langs}.', el: 'Διαβάστηκε στα {langs}.' },
	'reviewnote.caveat.sourced': {
		en: 'Checked against published sources, but still by a machine: no person has reviewed this entry.',
		el: 'Ελέγχθηκε έναντι δημοσιευμένων πηγών, αλλά και πάλι από μηχανή: κανένας άνθρωπος δεν έχει ελέγξει αυτή την καταχώριση.'
	},
	'reviewnote.caveat.unsourced': {
		en: 'This pass read the text for internal consistency — dates, arithmetic and cross-references. It did not check the claims against published sources, and no person has reviewed it.',
		el: 'Αυτός ο έλεγχος διάβασε το κείμενο ως προς την εσωτερική του συνέπεια — ημερομηνίες, αριθμητικά και παραπομπές. Δεν έλεγξε τους ισχυρισμούς έναντι δημοσιευμένων πηγών, και κανένας άνθρωπος δεν το έχει ελέγξει.'
	},
	'langname.en': { en: 'English', el: 'Αγγλικά' },
	'langname.el': { en: 'Greek', el: 'Ελληνικά' },
	'langname.join': { en: ' and ', el: ' και ' },

	// Citations
	'cite.online': { en: 'Online', el: 'Στο διαδίκτυο' },
	'cite.read': { en: ' · read {date}', el: ' · ανάγνωση {date}' },

	// The atlas page and its map
	'atlas.tagline': {
		en: 'An atlas of Greek history. The map redraws as control of territory changes.',
		el: 'Ένας άτλας της ελληνικής ιστορίας. Ο χάρτης ξαναχαράσσεται καθώς αλλάζει ο έλεγχος του εδάφους.'
	},
	'atlas.occupation': { en: 'Show occupation', el: 'Εμφάνιση κατοχής' },
	'atlas.note.insurgent': {
		en: 'Stippled areas are in armed revolt. There was no recognised frontier.',
		el: 'Οι διάστικτες περιοχές βρίσκονται σε ένοπλη εξέγερση. Δεν υπήρχε αναγνωρισμένο σύνορο.'
	},
	'atlas.note.occupied': {
		en: 'Hatching marks occupation layered over sovereignty, not replacing it. The Greek state remained sovereign throughout.',
		el: 'Η διαγράμμιση δηλώνει κατοχή που επικάθεται στην κυριαρχία, χωρίς να την αντικαθιστά. Το ελληνικό κράτος παρέμεινε κυρίαρχο σε όλη τη διάρκεια.'
	},
	'map.title': {
		en: 'Map of territorial control on {date}',
		el: 'Χάρτης του εδαφικού ελέγχου στις {date}'
	},
	'map.territories': { en: 'Territories', el: 'Εδάφη' },
	'map.sovereignty': { en: 'Sovereignty held by {polities}', el: 'Κυριαρχία: {polities}' },
	'map.occupied': { en: 'Occupied by {polities}', el: 'Υπό κατοχή: {polities}' },
	'map.revolt': { en: '{polity} in armed revolt', el: '{polity} σε ένοπλη εξέγερση' },
	'caption.territory': { en: 'Greek sovereign territory', el: 'Ελληνικό κυρίαρχο έδαφος' },
	'caption.inforce': { en: 'In force from today:', el: 'Σε ισχύ από σήμερα:' },
	'trend.aria': {
		en: 'Greek sovereign territory over the whole period, peaking at {n} square kilometres',
		el: 'Το ελληνικό κυρίαρχο έδαφος σε όλη την περίοδο, με ανώτατη τιμή {n} τετραγωνικά χιλιόμετρα'
	},

	// The map tooltip
	'tip.notmodelled': {
		en: 'Not modelled on this date',
		el: 'Δεν έχει μοντελοποιηθεί για αυτή την ημερομηνία'
	},
	'tip.external': {
		en: ' · outside the modern state, not counted in the total',
		el: ' · εκτός του σύγχρονου κράτους, δεν προσμετράται στο σύνολο'
	},
	'tip.since': { en: 'since {date}', el: 'από {date}' },

	// The timeline
	'timeline.prev': { en: 'Previous change', el: 'Προηγούμενη μεταβολή' },
	'timeline.next': { en: 'Next change', el: 'Επόμενη μεταβολή' },
	'timeline.play': { en: 'Play through the changes', el: 'Αναπαραγωγή των μεταβολών' },
	'timeline.pause': { en: 'Pause', el: 'Παύση' },
	'timeline.date': { en: 'Date', el: 'Ημερομηνία' },

	// The map frames
	'frame.greece': { en: 'Greece', el: 'Ελλάδα' },
	'frame.aegean-east': { en: 'Eastern Aegean', el: 'Ανατολικό Αιγαίο' },
	'frame.epirus': { en: 'Epirus', el: 'Ήπειρος' },
	'frame.cyprus': { en: 'Cyprus', el: 'Κύπρος' },

	// The ledger beside the map
	'ledger.filter': { en: 'Filter events', el: 'Φιλτράρισμα γεγονότων' },
	'ledger.placeholder': { en: 'Filter events…', el: 'Φιλτράρισμα γεγονότων…' },
	'ledger.shown': { en: '{shown} of {total}', el: '{shown} από {total}' },
	'ledger.total': { en: '{total} events', el: '{total} γεγονότα' },
	'ledger.readmore': { en: 'Read more', el: 'Περισσότερα' },
	'ledger.empty': { en: 'Nothing matches “{query}”.', el: 'Τίποτα δεν ταιριάζει με «{query}».' },

	// Old Style dates, which the corpus carries as written
	'date.oldstyle': { en: 'Old Style {date}', el: 'Παλαιό ημερολόγιο {date}' },
	'date.oldstyle.label': { en: 'Old Style: {date}', el: 'Παλαιό ημερολόγιο: {date}' },
	'date.circa': { en: 'c. {year}', el: 'π. {year}' },
	'date.range': { en: '{from} to {to}', el: '{from} έως {to}' },

	// The events index
	'events.description': {
		en: 'Every event in the atlas, in order.',
		el: 'Κάθε γεγονός του άτλαντα, με τη σειρά.'
	},
	'events.lead': {
		en: 'In order. Each one opens the map on the day it happened. Search reaches the English and the Greek, the places, the treaties and the arcs.',
		el: 'Με χρονολογική σειρά. Καθένα ανοίγει τον χάρτη στην ημέρα που συνέβη. Η αναζήτηση φτάνει στα αγγλικά και στα ελληνικά, στους τόπους, στις συνθήκες και στα νήματα.'
	},
	'events.placeholder': {
		en: 'Search events, places, treaties, threads…',
		el: 'Αναζήτηση σε γεγονότα, τόπους, συνθήκες, νήματα…'
	},
	'events.empty': { en: 'No event matches that.', el: 'Κανένα γεγονός δεν ταιριάζει.' },
	'events.openatlas': { en: 'Open on the atlas', el: 'Άνοιγμα στον άτλαντα' },

	// One event
	'event.openday': {
		en: 'Open this day on the atlas →',
		el: 'Άνοιγμα αυτής της ημέρας στον άτλαντα →'
	},
	'event.territory': { en: 'Territory', el: 'Έδαφος' },
	// A preposition would have to agree with the region's gender, so the Greek
	// names the relation instead of inflecting around the name.
	'event.inregion': { en: 'in', el: 'στην περιοχή' },
	'event.people': { en: 'People', el: 'Πρόσωπα' },
	'event.instrument': { en: 'Instrument', el: 'Πράξη' },
	'event.nearby': { en: 'Nearby', el: 'Κοντινά' },
	'event.starts': { en: '← starts here', el: '← αρχίζει εδώ' },
	'event.ends': { en: 'ends here →', el: 'τελειώνει εδώ →' },

	// The figures index and one figure
	'figures.description': { en: 'The people behind the events.', el: 'Τα πρόσωπα πίσω από τα γεγονότα.' },
	'figures.lead': {
		en: 'The people behind the events, in order of birth. Search reaches both languages, other spellings and the dates.',
		el: 'Τα πρόσωπα πίσω από τα γεγονότα, κατά σειρά γέννησης. Η αναζήτηση φτάνει και στις δύο γλώσσες, σε άλλες γραφές και στις χρονολογίες.'
	},
	'figures.placeholder': {
		en: 'Search names, roles, other spellings, years…',
		el: 'Αναζήτηση σε ονόματα, ιδιότητες, άλλες γραφές, χρονολογίες…'
	},
	'figures.empty': { en: 'No figure matches that.', el: 'Κανένα πρόσωπο δεν ταιριάζει.' },
	'figure.born': { en: 'Born', el: 'Γεννήθηκε' },
	'figure.died': { en: 'Died', el: 'Πέθανε' },

	// The instruments index and one instrument
	'instruments.description': {
		en: 'The treaties, protocols and conventions that moved the frontier.',
		el: 'Οι συνθήκες, τα πρωτόκολλα και οι συμβάσεις που μετακίνησαν τα σύνορα.'
	},
	'instruments.lead': {
		en: 'The treaties, protocols and conventions that moved the frontier. Each one links to the map on the day it took effect.',
		el: 'Οι συνθήκες, τα πρωτόκολλα και οι συμβάσεις που μετακίνησαν τα σύνορα. Καθεμία παραπέμπει στον χάρτη της ημέρας που τέθηκε σε ισχύ.'
	},
	'instruments.placeholder': {
		en: 'Search treaties, parties, years…',
		el: 'Αναζήτηση σε συνθήκες, συμβαλλόμενους, χρονολογίες…'
	},
	'instruments.empty': { en: 'No instrument matches that.', el: 'Καμία πράξη δεν ταιριάζει.' },
	'instruments.textyes': { en: 'Text linked ({n})', el: 'Με κείμενο ({n})' },
	'instruments.textno': { en: 'No text yet ({n})', el: 'Χωρίς κείμενο ακόμη ({n})' },
	'instruments.signed': { en: 'Signed {date}', el: 'Υπογράφηκε {date}' },
	'instruments.readtext': { en: 'Read the text', el: 'Διαβάστε το κείμενο' },
	'instrument.kicker': { en: '{kind} · signed {date}', el: '{kind} · υπογράφηκε {date}' },
	'instrument.openday': {
		en: 'Open the atlas on this day →',
		el: 'Άνοιγμα του άτλαντα σε αυτή την ημέρα →'
	},
	// The English names the kind inline; in Greek the article would have to agree
	// with it, so the Greek says "the original text" and lets the kicker say which.
	'instrument.readoriginal': {
		en: 'Read the text of the {kind} →',
		el: 'Διαβάστε το πρωτότυπο κείμενο →'
	},
	'instrument.notext': {
		en: "This {kind}'s own text is not linked yet. Nothing was linked that had not been opened, so the gap is deliberate rather than an oversight.",
		el: 'Το πρωτότυπο κείμενο δεν έχει συνδεθεί ακόμη. Δεν συνδέθηκε τίποτα που να μην έχει ανοιχτεί, οπότε το κενό είναι σκόπιμο και όχι παράλειψη.'
	},
	'instrument.moved': { en: 'What it moved', el: 'Τι μετακίνησε' },
	'instrument.openon': {
		en: 'Open the atlas on {date}',
		el: 'Άνοιγμα του άτλαντα στις {date}'
	},

	// The places index
	'places.description': {
		en: 'Every place the atlas names, and what happened there.',
		el: 'Κάθε τόπος που κατονομάζει ο άτλας, και τι συνέβη εκεί.'
	},
	'places.lead': {
		en: 'Every point the atlas names. Names change and the point does not, so a place carries all the names it has held and the dates each was in force — searching any of them finds it.',
		el: 'Κάθε σημείο που κατονομάζει ο άτλας. Τα ονόματα αλλάζουν, το σημείο όχι, οπότε κάθε τόπος φέρει όλα τα ονόματα που είχε και τις χρονολογίες που ίσχυε καθένα — η αναζήτηση οποιουδήποτε από αυτά τον βρίσκει.'
	},
	'places.placeholder': {
		en: 'Search places, old names, regions…',
		el: 'Αναζήτηση σε τόπους, παλιά ονόματα, περιοχές…'
	},
	'places.empty': { en: 'No place matches that.', el: 'Κανένας τόπος δεν ταιριάζει.' },
	'places.outside': {
		en: 'outside the mapped territory',
		el: 'εκτός του χαρτογραφημένου εδάφους'
	},
	// The compass letters are the Greek ones, and the decimal comma comes from
	// `num`, so the whole coordinate reads in the active language.
	'places.coords': { en: '{lat}°N {lon}°E', el: '{lat}°Β {lon}°Α' },
	'places.alsoknown': { en: 'Also known as', el: 'Γνωστός και ως' },
	'places.eventshere': { en: '{n} events here', el: '{n} γεγονότα εδώ' },
	'places.nothing': {
		en: 'Named by the corpus, but nothing is anchored here yet.',
		el: 'Αναφέρεται στο σώμα κειμένων, αλλά δεν έχει αγκυρωθεί ακόμη τίποτα εδώ.'
	},

	// The sources index
	'sources.description': {
		en: 'Every work the atlas cites, and what cites it.',
		el: 'Κάθε έργο που επικαλείται ο άτλας, και τι το επικαλείται.'
	},
	'sources.lead': {
		en: 'Every work the corpus cites, with the entries that cite it. Citations are authored on the entry, so this list is the inverse: the way to ask what one book is carrying.',
		el: 'Κάθε έργο που επικαλείται το σώμα κειμένων, με τις καταχωρίσεις που το επικαλούνται. Οι παραπομπές γράφονται στην καταχώριση, οπότε αυτός ο κατάλογος είναι το αντίστροφο: ο τρόπος να ρωτήσει κανείς τι σηκώνει ένα βιβλίο.'
	},
	'sources.placeholder': {
		en: 'Search authors, titles, publishers, what they support…',
		el: 'Αναζήτηση σε συγγραφείς, τίτλους, εκδότες, όσα τεκμηριώνουν…'
	},
	'sources.empty': { en: 'No work matches that.', el: 'Κανένα έργο δεν ταιριάζει.' },
	'sources.uncited': {
		en: '{n} of {total} are listed but not yet cited anywhere.',
		el: '{n} από {total} είναι καταχωρισμένα αλλά δεν τα επικαλείται ακόμη τίποτα.'
	},
	'sources.none': {
		en: 'Listed, but nothing cites it yet.',
		el: 'Καταχωρισμένο, αλλά δεν το επικαλείται ακόμη τίποτα.'
	},

	// The threads index and one thread
	'threads.description': {
		en: 'The narrative arcs the events belong to.',
		el: 'Οι αφηγηματικές γραμμές στις οποίες ανήκουν τα γεγονότα.'
	},
	'threads.lead': {
		en: 'The orders in which the events are worth reading. An event can sit on several arcs at once: 1922 belongs to the Great Idea, to the Asia Minor campaign and to the National Schism, and each tells it differently.',
		el: 'Οι σειρές με τις οποίες αξίζει να διαβαστούν τα γεγονότα. Ένα γεγονός μπορεί να ανήκει σε πολλά νήματα ταυτόχρονα: το 1922 ανήκει στη Μεγάλη Ιδέα, στη Μικρασιατική Εκστρατεία και στον Εθνικό Διχασμό, και καθένα το αφηγείται αλλιώς.'
	},
	'threads.placeholder': {
		en: 'Search threads and years…',
		el: 'Αναζήτηση σε νήματα και χρονολογίες…'
	},
	'threads.empty': { en: 'No thread matches that.', el: 'Κανένα νήμα δεν ταιριάζει.' },
	'threads.count': { en: '{n} events', el: '{n} γεγονότα' },
	'threads.filter': {
		en: 'Filter the ledger by this arc',
		el: 'Φιλτράρισμα του καταλόγου με αυτό το νήμα'
	},
	'thread.see': {
		en: 'See these {n} in the ledger →',
		el: 'Δείτε αυτά τα {n} στον κατάλογο →'
	},
	'thread.step': { en: '{i} of {n}', el: '{i} από {n}' },

	// Vocabularies that arrive as ids. Reached through `term`, never `ui`.
	'kind.place.battlefield': { en: 'battlefield', el: 'πεδίο μάχης' },
	'kind.place.building': { en: 'building', el: 'κτίριο' },
	'kind.place.city': { en: 'city', el: 'πόλη' },
	'kind.place.island': { en: 'island', el: 'νησί' },
	'kind.place.region': { en: 'region', el: 'περιοχή' },
	'kind.place.sea': { en: 'sea', el: 'θάλασσα' },
	'kind.place.town': { en: 'town', el: 'κωμόπολη' },
	'kind.place.village': { en: 'village', el: 'χωριό' },

	'kind.instrument.armistice': { en: 'armistice', el: 'ανακωχή' },
	'kind.instrument.convention': { en: 'convention', el: 'σύμβαση' },
	'kind.instrument.decree': { en: 'decree', el: 'διάταγμα' },
	'kind.instrument.protocol': { en: 'protocol', el: 'πρωτόκολλο' },
	'kind.instrument.treaty': { en: 'treaty', el: 'συνθήκη' },

	'kind.source.book': { en: 'book', el: 'βιβλίο' },
	'kind.source.article': { en: 'article', el: 'άρθρο' },
	'kind.source.chapter': { en: 'chapter', el: 'κεφάλαιο' },
	'kind.source.dataset': { en: 'dataset', el: 'σύνολο δεδομένων' },
	'kind.source.web': { en: 'web', el: 'ιστοσελίδα' },

	'kind.polity.autonomous': { en: 'autonomous', el: 'αυτόνομο' },
	'kind.polity.de_facto': { en: 'de facto', el: 'de facto' },
	'kind.polity.empire': { en: 'empire', el: 'αυτοκρατορία' },
	'kind.polity.protectorate': { en: 'protectorate', el: 'προτεκτοράτο' },
	'kind.polity.state': { en: 'state', el: 'κράτος' },

	'kind.regime.absolute_monarchy': { en: 'absolute monarchy', el: 'απόλυτη μοναρχία' },
	'kind.regime.constitutional_monarchy': {
		en: 'constitutional monarchy',
		el: 'συνταγματική μοναρχία'
	},
	'kind.regime.dictatorship': { en: 'dictatorship', el: 'δικτατορία' },
	'kind.regime.interregnum': { en: 'interregnum', el: 'μεσοβασιλεία' },
	'kind.regime.occupation': { en: 'occupation', el: 'κατοχή' },
	'kind.regime.republic': { en: 'republic', el: 'δημοκρατία' },
	'kind.regime.revolutionary': { en: 'revolutionary', el: 'επαναστατικό' },

	'kind.control.sovereign': { en: 'sovereign', el: 'κυριαρχία' },
	'kind.control.occupied': { en: 'occupied', el: 'κατοχή' },
	'kind.control.administered': { en: 'administered', el: 'διοίκηση' },
	'kind.control.insurgent': { en: 'insurgent', el: 'εξέγερση' },
	'kind.control.autonomous': { en: 'autonomous', el: 'αυτονομία' },
	'kind.control.disputed': { en: 'disputed', el: 'αμφισβητούμενο' },
	'kind.control.claimed': { en: 'claimed', el: 'διεκδικούμενο' },

	// How the tooltip says the same kinds, as a clause rather than a noun
	'verb.sovereign': { en: 'Sovereign', el: 'Κυρίαρχο' },
	'verb.administered': { en: 'Administered by', el: 'Υπό τη διοίκηση' },
	'verb.occupied': { en: 'Occupied by', el: 'Υπό την κατοχή' },
	'verb.insurgent': { en: 'In revolt', el: 'Σε εξέγερση' },

	// The legend's roles, which are their own vocabulary in `resolve.ts`
	'role.map.sovereign': { en: 'sovereign', el: 'κυρίαρχο' },
	'role.map.administering': { en: 'administering', el: 'διοικεί' },
	'role.map.occupying': { en: 'occupying', el: 'κατέχει' },
	'role.map.in revolt': { en: 'in revolt', el: 'σε εξέγερση' },

	'role.figure.athlete': { en: 'athlete', el: 'αθλητής' },
	'role.figure.benefactor': { en: 'benefactor', el: 'ευεργέτης' },
	'role.figure.cleric': { en: 'cleric', el: 'κληρικός' },
	'role.figure.diplomat': { en: 'diplomat', el: 'διπλωμάτης' },
	'role.figure.military': { en: 'military', el: 'στρατιωτικός' },
	'role.figure.monarch': { en: 'monarch', el: 'μονάρχης' },
	'role.figure.revolutionary': { en: 'revolutionary', el: 'επαναστάτης' },
	'role.figure.statesman': { en: 'statesman', el: 'πολιτικός' },
	'role.figure.writer': { en: 'writer', el: 'συγγραφέας' },

	'role.event.author': { en: 'author', el: 'συντάκτης' },
	'role.event.commander': { en: 'commander', el: 'διοικητής' },
	'role.event.leader': { en: 'leader', el: 'ηγέτης' },
	'role.event.participant': { en: 'participant', el: 'συμμετέχων' },
	'role.event.signatory': { en: 'signatory', el: 'υπογράφων' },
	'role.event.victim': { en: 'victim', el: 'θύμα' },
	'role.event.witness': { en: 'witness', el: 'μάρτυρας' },

	'what.born': { en: 'born here', el: 'γεννήθηκε εδώ' },
	'what.died': { en: 'died here', el: 'πέθανε εδώ' },

	'result.clean': { en: 'clean', el: 'καθαρό' },
	'result.corrected': { en: 'corrected', el: 'διορθωμένο' },
	'result.unresolved': { en: 'unresolved', el: 'ανεπίλυτο' },

	// The Greek ordinal carries its accent onto the numeral -- 20ός, not 20ος --
	// so these are written out rather than built from a pattern.
	'century.18': { en: '18th century', el: '18ος αιώνας' },
	'century.19': { en: '19th century', el: '19ος αιώνας' },
	'century.20': { en: '20th century', el: '20ός αιώνας' },
	'century.21': { en: '21st century', el: '21ος αιώνας' }
} satisfies Record<string, LangText>;

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
