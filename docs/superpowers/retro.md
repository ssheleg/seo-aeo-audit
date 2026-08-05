# Standing instructions

Capped at ten. Each one binds the next run and carries the date it was written
and the date it last fired. An instruction that has not fired in a long time is a
candidate for retirement — that is what the stamps are for.

**Prune log.** 2026-08-05: all five existing instructions checked against the
three retirement triggers (became a check · its paths and commands are gone · no
firing in five run stamps). None retired — four fired this run, and #5 is one run
old. Nothing deleted.

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
*Written 2026-08-04. Last fired 2026-08-05.*

Every doctrine guard and negative self-test added this run was run against a
deliberately broken tree first, and each was confirmed to fail. A guard nobody
has seen fail is indistinguishable from a guard that cannot.

*2026-08-05: three new guards, six failure modes watched. One of them earned its
keep immediately — the myth-count check fired on the real tree and turned out to
be reporting a genuine defect nobody would have seen by eye.*

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
*Written 2026-08-04. Last fired 2026-08-05.*

The Cursor channel shipped five non-negotiables where SKILL.md had seven, and
CONTRIBUTING said nineteen references where the validator enforced twenty-one.
Both were duplicated facts with nothing comparing the copies. Either give the
fact one home, or add the check that compares them — and record which in the
propagation matrix (`docs/DOCMAP.md`).

*2026-08-05: fired twice, the second time on itself. The evidence-tier vocabulary
had drifted between the reference and CONTRIBUTING on the tier that gates the most
admissions, so a reconciler was added — and the acceptance walk then found the
vocabulary actually lives in **four** places, not two. Count the homes before
writing the reconciler; a reconciler over a subset reads exactly like one over the
set.*

## 5. Refuse the plausible wrong feature, in code and in a test
*Written 2026-08-04. Last fired 2026-08-04.*

Orphan detection from a sitemap, a lab score standing in for absent field data, a
brand split guessed from query text: each is a feature a competitor ships and a
reviewer would accept. Each manufactures a finding out of missing data. When one
is refused, the refusal goes in the output **and** in a test, because the
useful-looking wrong feature is the one somebody adds back later.

## 6. A gate behind a pipe is not a gate
*Written 2026-08-05. Last fired 2026-08-05.*

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
*Written 2026-08-05. Last fired 2026-08-05.*

The acceptance walk reported two requirements missing that were both present. One
search string contained `**`, which `grep` read as a repetition operator; the
other phrase was wrapped across a line break, and the check was line-oriented.
Both were false reds, which cost a re-check — but the same harness produces a
false **green** the moment the chosen token also appears somewhere else, and that
one ships an absence as coverage.

Presence checks over prose use fixed-string matching (`grep -F`), pick a token
that cannot wrap, and are read as evidence only after one deliberate miss has been
observed. A verification harness is a guard, so instruction #2 applies to it too.

## 8. Verify every number in the diff, not every number on the list
*Written 2026-08-05. Last fired 2026-08-05.*

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
