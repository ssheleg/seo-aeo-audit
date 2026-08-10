# Standing instructions

Capped at ten. Each one binds the next run and carries the date it was written
and the date it last fired. An instruction that has not fired in a long time is a
candidate for retirement — that is what the stamps are for.

**Run stamps.** 2026-08-04 · 2026-08-05 (`v0.11.2`) · **2026-08-10 (`v0.11.3`,
commit on `audit/2026-08-10-fresh-eyes`)**. The stamp is what makes the
cold-retirement trigger computable, so it goes first.

**Prune log.**

- 2026-08-05: all five existing instructions checked against the three retirement
  triggers (became a check · its paths and commands are gone · no firing in five run
  stamps). None retired — four fired this run, and #5 is one run old. Nothing deleted.
- 2026-08-10: all eight checked. **#4 rewritten rather than retired** — it fired
  hardest of any instruction this run and its lesson had been half-learned, so the
  operative sentence now names the failure mode instead of the remedy. **#5 retired**
  (became a check). **#2, #6, #7, #8 fired** — #7 fired on this run's own edit to
  CONTRIBUTING. #1 and #3 did not fire this run and are one and two stamps old
  respectively; both stay. Eight instructions after the prune, cap is ten.

## 1. Verify a carried number before it enters a reference
*Written 2026-08-04. Last fired 2026-08-05.*

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

*2026-08-05: fired eleven times in one pass. Three figures dropped for having no
primary at all, one **field name refuted** — a documented diagnostic told the
auditor to compare `Last crawl` with `Last crawl rendered` in Search Console, and
the second field does not exist, so the step could never have been executed — one
claim narrowed to what its source actually scoped, one upgraded when the primary
turned out to be published research. Every one of them had already passed a
non-contradiction screen. The field name is the part worth remembering: this rule
is not only about numbers.*

## 2. Watch a guard fail before trusting it
*Written 2026-08-04. Last fired 2026-08-10.*

Every doctrine guard and negative self-test added this run was run against a
deliberately broken tree first, and each was confirmed to fail. A guard nobody
has seen fail is indistinguishable from a guard that cannot.

*2026-08-05: three new guards, six failure modes watched. One of them earned its
keep immediately — the myth-count check fired on the real tree and turned out to
be reporting a genuine defect nobody would have seen by eye.*

*2026-08-10: twelve new guards, every one watched failing **on the real repository**
before the fact was corrected, then again against a planted defect in CI. Eleven of
the twelve reported a genuine defect on their first run — which is the same signal as
2026-08-05, one order of magnitude louder. Also: all twelve pre-existing negative
self-tests were re-run after the code changes, because a changed line silently
disables one and a disabled self-test looks exactly like a passing one.*

## 3. When a rule has been violated twice, promote it off the page
*Written 2026-08-04. Last fired 2026-08-05.*

Non-negotiable #7 already forbade blending measured with assumed, and two
instruments did it anyway — because the doctrine governs what the auditor writes,
not what the tools hand them. The second occurrence is the signal to move the
rule into `validate.py` or CI. One occurrence is a fix; two is a class.

*2026-08-05: applied to prose counts. "Nineteen references" against twenty-one
enforced was the first; the README's myth count going stale two rows later was
the second. It is a check now — and the check found a split table on its first
run.*

## 4. A fact with two homes needs a reconciler
*Written 2026-08-04. Last fired 2026-08-10. Rewritten 2026-08-10.*

The Cursor channel shipped five non-negotiables where SKILL.md had seven, and
CONTRIBUTING said nineteen references where the validator enforced twenty-one.
Both were duplicated facts with nothing comparing the copies. Either give the
fact one home, or add the check that compares them — and record which in the
propagation matrix (`docs/DOCMAP.md`).

*2026-08-05: fired twice, the second time on itself. The evidence-tier vocabulary
had drifted between the reference and CONTRIBUTING on the tier that gates the most
admissions, so a reconciler was added — and the acceptance walk then found the
vocabulary actually lives in **four** places, not two.*

*2026-08-10: fired on eight facts at once, and the lesson from 2026-08-05 had been
written down without being applied. The myth-count guard added that day read **one**
sentence in **one** file while the count lived in four; the repository was green
while README's closing pitch said 29, SKILL.md said 30 and the Cursor rule said 29
against 32 rows. Same shape for the play count, the Prowl tool count, the gate
commands, the CWV thresholds, the freshness stamp, the two short lists and the
slash command's doctrine — a fourth doctrine channel nothing had ever compared.*

**The operative form, since the remedy was never the hard part:** before writing a
reconciler, `grep` the repository for the fact and count what comes back. Write the
home list into the guard as data, not into the prose around it. A guard that names
its homes can be audited; one that matches a sentence cannot be distinguished from
one that matches the wrong sentence — and it stays green while it does.

## 5. ~~Refuse the plausible wrong feature, in code and in a test~~ — retired 2026-08-10

*Written 2026-08-04. Last fired 2026-08-04. Retired: it became a check.*

The three refusals it was written for are now held by named tests that a CI negative
self-test proves can fail: `sitemap_audit`'s orphan refusal, `psi_pull`'s
absent-CrUX honesty, and `gsc_pull`'s branded-split refusal. The 2026-08-10 audit
added the fourth and fifth of the same shape — a truncated read refuses to publish
counts, and `url_inspection` refuses to claim CONFIRMED for rows nobody answered —
and both arrived as tests without anyone needing the instruction. That is the
retirement trigger working as intended: the rule is in the harness, so the page does
not need to carry it.

## 6. A gate behind a pipe is not a gate
*Written 2026-08-05. Last fired 2026-08-10.*

A module was committed after `bash scripts/check-docs.sh 2>&1 | tail -2 && git
commit …`. The gate did not merely fail — it never ran, because a stray `cd` from
an earlier command had moved the working directory. The commit landed anyway,
because a shell pipeline exits with the status of its **last** command, and `tail`
had nothing to complain about. The gate was green in the transcript and absent in
reality.

Run a gate as its own command from an absolute path, and read its exit status:
`cd <repo> && bash scripts/check-docs.sh` — no pipe, or `set -o pipefail` if the
output has to be trimmed. The same applies to any check whose result is being used
to decide whether to proceed.

## 7. A presence check over prose needs fixed strings
*Written 2026-08-05. Last fired 2026-08-10.*

The acceptance walk reported two requirements missing that were both present. One
search string contained `**`, which `grep` read as a repetition operator; the
other phrase was wrapped across a line break, and the check was line-oriented.
Both were false reds, which cost a re-check — but the same harness produces a
false **green** the moment the chosen token also appears somewhere else, and that
one ships an absence as coverage.

Presence checks over prose use fixed-string matching (`grep -F`), pick a token
that cannot wrap, and are read as evidence only after one deliberate miss has been
observed. A verification harness is a guard, so instruction #2 applies to it too.

*2026-08-10: fired on this run's own edit. Rewriting the CONTRIBUTING paragraph that
lists the validator's guard families wrapped "table integrity" across a line break,
and the existing fixed-string check reported it absent — correctly. The lesson keeps
generalizing: the guard was right and the prose was wrong, which is the direction you
want, and the fix is to keep each checked token on one line rather than to loosen the
check.*

## 8. Verify every number in the diff, not every number on the list
*Written 2026-08-05. Last fired 2026-08-10.*

The primary-source rule (#1) was applied rigorously — to the eleven claims on the
requirement list. A self-audit afterwards found four more figures that had entered
references in passing: a sample size carried straight from a retelling, a range
stated without the word *median* that made it, enforcement figures written from
secondary coverage and confirmed against the paper only later, and an engine
statement from **2017** dated to the 2026 post that restated it.

None of them were on the list, which is exactly why they got through: the
discipline attached to the items being consciously verified, not to the act of
typing a number. The check is the diff, not the plan — before a module is
committed, every figure and every date it adds gets asked the same question, and a
date is a claim about a source, not decoration.

## 9. A green gate is evidence about the gate, not about the repository
*Written 2026-08-10. Last fired 2026-08-10.*

`bash scripts/check-docs.sh` exited 0 against forty-one defects, nine of which made
the skill emit or suppress findings in ordinary use: a fabricated indexation blocker
on any page carrying `max-image-preview:none`, a JS-gated-price finding on any page
using jQuery, a page silently analyzed as a fragment, and a run of 403s declaring its
own output CONFIRMED. Every one of those was inside a file the gate reads, in a
repository whose entire premise is evidence discipline.

The gate could not have caught them, and that is the point: a guard tests the
invariant somebody thought to write. What found these was reading each instrument's
output against its own doctrine, and running the tool on inputs nobody had chosen as
fixtures. `edge-page.html` exists specifically to prove the directive parser is not
fooled by substrings — and it uses `max-image-preview:large`, one word away from the
case that fires.

So: when a pass adds guards, it also has to spend time **outside** them. Pick the
three inputs an ordinary site would produce, run each script on them by hand, and
read the findings as a client would. The question is not "does the check pass" but
"would I sign this report".

## 10. Doctrine and instrument are two homes of one fact
*Written 2026-08-10. Last fired 2026-08-10.*

Three separate cases this run, all the same shape. `onpage-checks.md` says a
"multiple H1s" line "spends a finding on a non-finding", and `page_audit.py` emitted
exactly that line. `intent-and-content.md` E2 says "length barely matters", and the
`thin` finding fired at a bare 300-word floor **pointing at that section**.
`onpage-checks.md` scopes the subhead failure to a long page, and the check ignored
the qualifier.

Instruction #4 covers a fact duplicated across two documents. This is the same defect
with a script on one side, and no reconciler existed because nobody thought of code
as a home for a doctrine claim. It is one: a finding message is a sentence the
doctrine also states, and the anchor it points at is a promise about what the reader
will find there.

The check that exists now: every finding carries a tier from a declared mapping, and
the validator resolves every anchor. The check that does not: nothing compares a
finding's *message* to the section it cites. So when you add or change a finding,
open the section it points at and read it — if the section argues against the
finding, one of the two is wrong, and it is usually not the doctrine.
