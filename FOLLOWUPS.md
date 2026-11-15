# Follow-ups

Open items left by the review sweep of 20 September 2026, which put a recorded pass on
all 237 entries then in the corpus. On 14 November 2026 the atlas was cut at 1975 and 15 of
them moved to `content/archive/after-1975/`; the numbers below are for the 222 that remain:
118 events, 74 figures, 30 instruments.

Run `make review` for the live picture of what is reviewed, what has gone stale and where
the English and Greek disagree numerically. This file holds what that report cannot say.

## Read the coverage honestly first

Every entry carries a pass, and that is not the same as every entry being verified.

| | clean | corrected | unresolved | verified against sources |
|---|---|---|---|---|
| events | 106 | 9 | 3 | 3 |
| figures | 63 | 2 | 9 | 2 |
| instruments | 27 | 3 | 0 | 8 |

Thirteen of 222 entries were checked against public sources. The rest were read in both
languages with dates, arithmetic and cross-references checked, but their individual
figures were not independently sourced. Which is which is recorded per entry in
`review.auto.by`, so it can be filtered:

```sh
grep -L "verified against public sources" content/events/*.yaml
```

Nothing here has had a `manual` pass. That column is yours and is still at zero.

## 1. Twelve entries left unresolved

These are the ones where something could not be settled, not the ones nobody looked at.

**Figures at year precision.** Nine were listed here; the lookup was done on 15 November
2026 against Greek and English Wikipedia, and only one could be upgraded.

- `kountouriotis`: born on Hydra on 9 April 1855 (Old Style), now stored as 21 April.
- `deligiannis`: 19 May is given, but the year is disputed between 1820 and 1824, so the
  day cannot be attached to a year with any confidence.
- `kallergis`, `makriyannis`, `papoulas`, `siantos`, `stergiadis`: the sources give a
  year only. Makriyannis's year itself varies between 1796 and 1797.
- `vassos`: Greek Wikipedia gives 2 September 1836, but the earlier pass found the sources
  disagreeing on the day, and one page is not enough to overrule that.
- `melas`: see §2.

Two death dates disagree with a source and want a person to settle them. `kallergis` is
stored as 8 April 1867, which both Wikipedias give without a calendar, while the Greek
infobox gives 24 April Old Style, 6 May New. `stergiadis` is stored as 22 June 1949; the
Greek article gives both 22 and 23 June.

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

## 4. Fifteen treaties still have no `text_url`

Fifteen of 30 are linked. Seven were added on 15 November 2026, each opened and checked
first: the Ionian Islands treaty of 1815, the Cyprus Convention of 1878, Ouchy 1912 and
London 1913 on Wikisource, and the peace with Italy of 1947, the Treaty of Ankara of
October 1930 and the Balkan Pact of 1934 in the United Nations' scans of the UN and League
of Nations treaty series (whole volumes: No. 747 in vol. 49, No. 2841 in LNTS vol. 125,
No. 3514 in LNTS vol. 153).

Still empty, with nothing reliable found: the London Protocol of 1830 (a Greek transcript
exists at imoph.org; the French original is said to be on the Foreign Ministry's site),
Constantinople 1832 and 1881, London 1864, Halepa 1878, Tatarna and Constantinople 1897,
Thessaloniki, the Albanian decision and Athens 1913, Mudanya 1922, the Ankara convention
of June 1930, Salonika 1938 (cited as LNTS vol. 195, p. 371, but not in that volume), the
Bulgarian decree of 1941 and Zürich–London 1959.

Nothing was linked that had not been opened, because a plausible-looking unchecked URL is
the same failure as the Hionidou figure.

## 5. The `result` enum conflates outcome with depth

`clean | corrected | unresolved` answers *what was found*. It does not answer *how hard
anyone looked*, which is currently carried informally in `by`.

At eight reviewed entries that was fine. At 222 it is strained: a `clean` from a reading
pass and a `clean` from a sourced pass are not the same claim, and only a string
comparison tells them apart. If you want to filter reliably on "actually verified", depth
probably wants its own field.

This now has a second reader. The app's **Checked against sources** filter is that same
string comparison, against the same `verified against public sources` marker this file
greps for, in `frontend/src/lib/review.ts`. So the marker is load-bearing in two places
and is still only prose. Giving depth a field would let both stop guessing; until then,
changing the wording of `review.auto.by` silently changes what that filter returns.

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

## 8. Northern Cyprus after August 1974 — done

Fixed on 15 November 2026. `cyprus-north` is cut from CY000 along the ceasefire line
(`content/cuts.yaml`) and carries a Turkish `occupied` row from 16 August 1974 over the
Republic's sovereignty. The same mechanism cut the 1832 line through Fthiotida, Evrytania
and Magnesia and the 1881 line through Larisa, Trikala and Arta-Preveza.

The Cyprus line comes from an OpenHistoricalMap relation that is flagged there as needing
a source for its lines. It follows the present Green Line, which is the ceasefire line, so
it is right at the scale of this map; a cited source for it would still be better.

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
