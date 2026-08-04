# Standing instructions

Capped at ten. Each one binds the next run and carries the date it was written
and the date it last fired. An instruction that has not fired in a long time is a
candidate for retirement — that is what the stamps are for.

## 1. Verify a carried number before it enters a reference
*Written 2026-08-04. Last fired 2026-08-04.*

Three figures carried in from other people's skills failed verification in a
single run: `userDeclaredCanonical` (the API returns `userCanonical`, so the
declared canonical would always have read as absent), "+41% for Quotation
Addition" (the paper groups three methods and quotes >40%; secondary write-ups
disagree about which one peaks), and "~9% of post-recommendation visits arrive as
AI referrals" (absent from the source, which reports channel composition
instead). All three would have shipped as fact.

The rule: a number or field name that arrived from anywhere other than a primary
source is a **lead**, not a finding, until the primary source is read. Failing
that, it goes to carry-over — never into a reference with a hedge attached.

## 2. Watch a guard fail before trusting it
*Written 2026-08-04. Last fired 2026-08-04.*

Every doctrine guard and negative self-test added this run was run against a
deliberately broken tree first, and each was confirmed to fail. A guard nobody
has seen fail is indistinguishable from a guard that cannot.

## 3. When a rule has been violated twice, promote it off the page
*Written 2026-08-04. Last fired 2026-08-04.*

Non-negotiable #7 already forbade blending measured with assumed, and two
instruments did it anyway — because the doctrine governs what the auditor writes,
not what the tools hand them. The second occurrence is the signal to move the
rule into `validate.py` or CI. One occurrence is a fix; two is a class.

## 4. A fact with two homes needs a reconciler
*Written 2026-08-04. Last fired 2026-08-04.*

The Cursor channel shipped five non-negotiables where SKILL.md had seven, and
CONTRIBUTING said nineteen references where the validator enforced twenty-one.
Both were duplicated facts with nothing comparing the copies. Either give the
fact one home, or add the check that compares them — and record which in the
propagation matrix (`docs/DOCMAP.md`).

## 5. Refuse the plausible wrong feature, in code and in a test
*Written 2026-08-04. Last fired 2026-08-04.*

Orphan detection from a sitemap, a lab score standing in for absent field data, a
brand split guessed from query text: each is a feature a competitor ships and a
reviewer would accept. Each manufactures a finding out of missing data. When one
is refused, the refusal goes in the output **and** in a test, because the
useful-looking wrong feature is the one somebody adds back later.
