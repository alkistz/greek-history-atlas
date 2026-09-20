# Follow-ups

Open items left by the review sweep of 20 September 2026, which put a recorded pass on
all 237 entries: 127 events, 78 figures, 32 instruments.

Run `make review` for the live picture of what is reviewed, what has gone stale and where
the English and Greek disagree numerically. This file holds what that report cannot say.

## Read the coverage honestly first

Every entry carries a pass, and that is not the same as every entry being verified.

| | clean | corrected | unresolved | verified against sources |
|---|---|---|---|---|
| events | 114 | 10 | 3 | 4 |
| figures | 67 | 2 | 9 | 2 |
| instruments | 28 | 4 | 0 | 9 |

Fifteen of 237 entries were checked against public sources. The rest were read in both
languages with dates, arithmetic and cross-references checked, but their individual
figures were not independently sourced. Which is which is recorded per entry in
`review.auto.by`, so it can be filtered:

```sh
grep -L "verified against public sources" content/events/*.yaml
```

Nothing here has had a `manual` pass. That column is yours and is still at zero.

## 1. Twelve entries left unresolved

These are the ones where something could not be settled, not the ones nobody looked at.

**Nine figures at year precision where the sources probably give a day** — `deligiannis`,
`kallergis`, `kountouriotis`, `makriyannis`, `melas`, `papoulas`, `siantos`, `stergiadis`,
`vassos`. This is now a lookup rather than a judgment, because the calendar rule below is
settled and `as_written` exists to hold the Julian date. `melas` is the exception: see §2.

**`great-famine`** — the corpus attributed roughly 250,000 famine deaths to Violetta
Hionidou. That figure could not be substantiated anywhere reachable, and she was not
cited by the event at all. The text now gives the 200,000–450,000 range and explains that
the spread is a disagreement about method, and she has been added to `sources.yaml` with
her ISBN. Settling her actual figure needs the book.

**`refugee-settlement-commission`** — its headline totals, 578,824 settled in 2,085 rural
settlements and some 27,600 urban dwellings, could not be confirmed. They appear to come
from the Commission's own final report, which is the right source and not one reachable
from here. They stand unverified rather than doubted.

**`ankara-rapprochement-1930`** — see §3; it is a schema problem, not a content one.

## 2. The Old Style rule, and where it does not apply

Greek sources of the period give Julian dates; this corpus stores the Gregorian, twelve
days on in the nineteenth century and thirteen in the twentieth.

Derived from the corpus itself rather than asserted: Greek biographies give Trikoupis's
death as 30 March 1896 where the corpus already stored 1896-04-11, the same day twelve on.
Melas's 13 October 1904 against the stored 1904-10-26 confirmed it thirteen on for the
next century. Danglis then confirmed it from a third direction, his sources carrying both
styles explicitly: 17 November 1853 Old Style, 29 November New.

**The rule follows where the event happened, not the person's nationality.** Melas was
born in Marseille, registered on the Gregorian calendar whatever a Greek biography later
printed, so his 29 March 1870 may already be the date this corpus wants or may be twelve
days short of it. That is why he is still unresolved.

All 50 events carrying an `as_written` Julian date were checked arithmetically and all 50
convert correctly. That error class is clean.

## 3. `Event.instrument` should probably be a list

`ankara-rapprochement-1930` spans both 1930 instruments — the June convention on
exchangeable property and the October treaty of friendship — and its prose is right about
both. The field holds one, and points at the October treaty while the event's own start
date is the June convention. The link cannot express what the text says.

Found by checking every event's date against the signing date of the instrument it links
to. Eight other events differ from their instrument's date legitimately, because an
occupation or a handover is not the treaty that regularised it.

## 4. Twenty-three treaties still have no `text_url`

Nine of 32 are linked: Lausanne, Sèvres, Neuilly, Bucharest 1913, the Population Exchange
Convention, Berlin 1878, both Nicosia treaties of 1960, and Prespa.

The other 23 were left empty deliberately. Nothing was linked that had not been opened,
because a plausible-looking unchecked URL is the same failure as the Hionidou figure.

This is the cheapest large win still available: the treaty layer is the spine of the map,
and a treaty's own text is the most authoritative thing the atlas can point at.

## 5. The `result` enum conflates outcome with depth

`clean | corrected | unresolved` answers *what was found*. It does not answer *how hard
anyone looked*, which is currently carried informally in `by`.

At eight reviewed entries that was fine. At 237 it is strained: a `clean` from a reading
pass and a `clean` from a sourced pass are not the same claim, and only a string
comparison tells them apart. If you want to filter reliably on "actually verified", depth
probably wants its own field.

## 6. Two figures are thinly anchored

- **`vassos`** had no dates at all before this sweep. Born 1836 in Athens, died there in
  October 1929 is all that was recoverable, so the precisions are year and month rather
  than a day invented to look tidy.
- **`melas`**'s birthplace, Marseille, is not in `places.yaml`, so it cannot be recorded.

## 7. Thirteen one-sided parity anomalies

`make review` reports these under **one-sided**. All thirteen are English spelling a
number that Greek writes in digits — "on the twenty-third" against "στις 23", "Fourth of
August" against "4ης Αυγούστου", "XXVIII Olympiad" against "28ης Ολυμπιάδας". They are
benign and will stay in the report unless the convention is normalised one way.

The **mismatched** tier, where each language carries a *different* figure, is at zero.
That tier is the one worth watching: it is how both Old Style / New Style splits were
found.

## What was tried and did not work

Recorded so it is not attempted again.

- **Normalising English number words** in the parity check, so "twenty-third" would match
  "23". English prose uses "one", "first" and "a second" as words rather than quantities,
  and the report went from 10 anomalies to 352. Reverted.
- **Automating the "stated components do not sum" check**, generalising two real errors of
  that shape. It produced 23 hits of which every one was coincidence — dates, seat counts
  and percentages that happen to nearly add. Most number triples in prose are not sums,
  and whether a sentence asserts one needs reading.

## The shape of what was wrong

Useful for aiming the manual pass: across ten corrected events, **not one told a wrong
story**. Every error was arithmetic or attribution.

- A number presented as settled when the literature is divided (Sakarya casualties, the
  Thessaloniki totals).
- A figure derived wrongly from correct components (the 1974 referendum percentage; the
  IMF share that made 80 + 20 = 110).
- A fact attributed to the wrong instrument or the wrong person (Crete at Bucharest;
  Hionidou).
- A significant omission that changed the meaning (the Yassıada finding of state orders;
  the 15,000 prisoners that made Sakarya decisive).

Prose and narrative judgment held up throughout. Numbers, attributions and omissions are
where the manual pass will earn its time.
