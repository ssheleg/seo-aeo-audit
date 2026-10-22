## 0.30.0 pinned; the next change needs a split (2026-10-22)

- **State.** seo-aeo-audit 0.30.0 is pinned by the hub. The SKILL body sits at 4,745 of its 4,750-token limit, so the next addition first moves a section into a reference.
- **G7 measured as covered (2026-10-22).** The M2 plan's G7 asked for AI citation sources beyond the own site and LLM referrals as a channel. Both are already here: `references/demand-and-conversion.md:113` and `:116`, `references/measurement.md:30-33`, `references/aeo-geo.md:93-106`, `references/entity-and-brand.md:283-287`. No change is owed; the attribution half moves to super-ux.
- **Next task.** B-11 (priority 5.0, the board's highest): `agent_traffic.py`, which counts AI and agent user agents in a server-log export and drops spoofers by forward-confirmed reverse DNS. Any body addition still starts with a split.

## Short description, triggers in the body: 0.30.0 (2026-10-20)

Branch `desc-budget-1020`. The description went from 956 to 418 characters and the
command from 129 to 86, because the operator's skill listing was full and 81 skills
showed no description. Removed trigger phrases live verbatim under `## Triggers` in
SKILL.md. To keep the body inside 4,750 tokens, Step 0's access-testing paragraph moved
to `references/preflight.md` and the `llms.txt` boundary paragraph became a pointer to
`references/myths.md`. Version 0.29.0 to 0.30.0 in the manifests, SKILL-CARD and the
nine script constants. Gate: `bash scripts/check-docs.sh` alone, exit 0.

Next task: none here; the hub re-pins 0.30.0 in its own change. Note for whoever
edits the body next: it is at 4,745 of 4,750 tokens, so the next section is a split.

## AI answer panel, Bing Webmaster instrument, freshness loop: 0.29.0 (2026-10-19)

Branch `feat/0.29-freshness-instruments`. Objective: wave 3 part 2 of the 2026-10-19
SEO plan (board row B-38, now done). Done: `scripts/ai_panel.py` and
`scripts/bwt_pull.py` (nine scripts ship), preflight's Bing probe, `page_audit.py
--cache-parity` and `jsonld-double-escaped`, `agent_surface.py` Meta and AdsBot rows,
ten dated timeline rows with the weekly cadence, the timeline tier-word guard and the
21-day staleness warning, doctrine rows that have a primary-source sentence, evals s06
and s07. Decision recorded in `DECISIONS.md` (credentials on stdin; the panel only
scores). Version 0.28.0 to 0.29.0 in the manifests, SKILL-CARD and the nine script
constants; ledger section, retro stamp, CHANGELOG.

Checks run: `bash scripts/check-docs.sh` and `npm run test:all`; every new test and
guard watched failing on a mutant (verification ledger, v0.29.0 section).

Open: board row B-40 (rows with no allowed sentence yet). Next task: the umbrella pin
of 0.29.0 in the hub, then B-40 when the research feed supplies primary sentences.

## Brief mode, poisoned-SERP guard, per-URL sitemap truth: 0.28.0 candidate (2026-10-19)

Branch `feat/brief-mode-0.28`. Objective: wave 3 part 1 of the 2026-10-19 SEO plan.
Done: brief mode (`references/build-time.md` N1 to N19 with resolving Verified-by
links, `templates/brief.template.md`, SKILL.md Step 0, landing readiness linking
super-ux's readiness check by URL); the poisoned-SERP guard in measurement.md J2 and
tooling.md; `page_audit.py` `challenge-page` (fixture `test/fixtures/serp-challenge.html`);
`gsc_pull.py` `report-stale`; `sitemap_audit.py` `--sample`, `--robots`, nested index and
batch `lastmod`; pagination rules in technical-checks.md A3; baseline rows (engine host
and locale, direct baseline, index-mass ratio, analytics coverage of orders, `tool-zero`);
evals s04, s05, q13, q14. Factual sentences use only the wave 1 primary-source wording.
Decision recorded in `DECISIONS.md` (2026-10-19). Version 0.27.0 to 0.28.0 in the
manifests, SKILL-CARD and the seven script constants; ledger section and retro stamp.

Checks run: `bash scripts/check-docs.sh` and `npm run test:all` (results in the PR).
Brief-guard plants and the three behaviour plants were watched failing by name.

Open: part 2 is board row B-38. The coordinator owns review, merge, tag, publication
and the umbrella pin; the hub's routing (brief entry, B-08) and task-pipeline's
spec link belong to their owners. Next task: review the PR, then the family release.

## WebKit (Safari) first for rendering checks — 0.27.0 candidate (2026-10-16)

Branch `docs/safari-first` (family iteration ITER-1016, REQ R13): `references/tooling.md`
gains *Browser engine — WebKit (Safari) first*; Lighthouse, PSI, CrUX, the
`chrome-devtools` MCP and CDP traces stay as the stated Chromium exception (Chromium by
definition), labelled in tooling, measurement, experience-signals and scripts. Version
0.26.6 → 0.27.0 across manifests, SKILL-CARD and the seven script constants; ledger
section and retro stamp added. Regression `test/audit_regressions/safari-first.py`
(watched failing 8 of 8 first). Gate: `npm test` exit 0.

Open: none here. The coordinator owns review, the annotated tag, publication and the
umbrella pin. Next task: review the draft PR, then the family release sequence.

## FW07 shared scratch lock — active bounded port

[Owner entry](evidence/runs/2026-10-13-fw07-scratch-lock/README.md) binds the
accepted canonical mechanism, own source and pending tests. Exact next task:
port byte-identical helper and runner adapter, run owned-namespace focused checks,
independent review, then serial owner gate. No public scratch execution while the
coordinator owns the full-suite slot; no package version/release in this change.

## FW01 source-guard follow-up candidate

The [remaining source-guard packet](evidence/runs/2026-10-13-fw01-source-guard/README.md)
addresses the unclosed half of agent-stack B-159. Focused actual-validator negative
controls and independent review pass. Exact e31abf5 completed the serialized local
`npm run test:all` with exit0; normal integration remains pending. Package 0.26.6
and all 46 published file hashes remain unchanged.
The accepted publication cut below remains historical fact, not candidate acceptance.

## FW06 release accepted — 0.26.6

[Final owner receipt](evidence/runs/2026-10-13-fw06-release-readback/README.md):
normal merged source c5a32d23da41d7717942f33995228b36971d2657 passed exact-main
npm run test:all before annotated tag v0.26.6. All four release jobs passed;
immutable npm whole payload equals source (46 files, 1,119,910 bytes, hashes/modes).
This docs-only receipt branch does not change package version or shipped behavior.

Exact next task: parent updates the family pin and installed copies, then records
its own byte readback. Live provider, native-host and model-quality acceptance stay
separate. B-9 and B-33 closure scope remains the bounded source/helper contract
recorded in the backlog, not universal audit quality.

## Historical preparation handoff

## 0.26.6 release candidate — 2026-10-13

Read [the release receipt](evidence/runs/2026-10-13-fw06-release-0266.md).
[PR36](https://github.com/ssheleg/seo-aeo-audit/pull/36) merged normally as
`524e3552d03a865d4e061eac439d2f6c889cedcb` after genuine full validation
[38365449655](https://github.com/ssheleg/seo-aeo-audit/actions/runs/38365449655)
passed exact `058d2f7f8b5c9b6cb69cc9881622e8fe52f3a64d`. Both precursor leases
were released. B-9's bounded shared-source contract is accepted; B-33's helper
attribution was already accepted in PR31. Provider/native/model acceptance stays NOT_RUN.

Independent packaging review accepted `1a1667d` versus the final source candidate.
Accepted main is merged here. Exact next task: freeze focused metadata/provenance
checks and receipt, promote draft PR37 once, normal merge after genuine checks,
then annotated v0.26.6, publication and immutable payload readback. No tag or package
publication has occurred yet. The older handoffs below are historical source cuts.

## Historical implementation handoffs

## Transport/bootstrap next packet — 2026-10-13

Read [the source-aware completion packet](evidence/plans/2026-10-13-fw06-bootstrap-transport.md).
Twelve reproduced loopback/pure baseline cases cover framing, decoded budgets,
provider-body errors and URL Inspection answer admission. Preflight correction
9d9b166 received independent82 PASS. The parent accepted packet76818f2 for
implementation. T1 transport now has a [bounded source receipt](evidence/runs/2026-10-13-fw06-transport.md);
T2 now has a [typed-admission source receipt](evidence/runs/2026-10-13-fw06-inspection-payload.md).
Independent T1/T2 source reviews passed `6c3403d` (170 controls) and `ce6d4df` (75 controls).
B1 now has its [bootstrap receipt](evidence/runs/2026-10-13-fw06-bootstrap.md).
Independent B1 exact `5ab0436` review passed 87 controls. The first composed gate
found five superseded fixture expectations, preserved in the bootstrap receipt.
Both fixture corrections were independently accepted. Split local coverage passed:
complete structure/behavior, 30 unchanged negatives, corrected canonical negative
and nine audit regressions. Both full attempts remain FAILED as recorded.
Next: freeze/promote PR36 once for full genuine CI, normal integration, then
separately reviewed 0.26.6 packaging.
Do not claim complete B-9 or provider/native acceptance from this planning branch.

## Preflight integrated candidate — 2026-10-13

The [accepted contract](evidence/plans/2026-10-13-fw06-preflight-coverage.md) now
has bounded source and 82 focused controls. See the
[run receipt](evidence/runs/2026-10-13-fw06-preflight-coverage.md).
PSI and GSC/R30 were normally integrated; accepted main
`2de0d4042e1a312f4366ada325118b2a4413d760` is composed here. PSI genuine run
[38356315862](https://github.com/ssheleg/seo-aeo-audit/actions/runs/38356315862)
passed exact b57f9a4 before normal PR35 merge and lease release.

Next: independent preflight source review, then one serial owner gate after
TP/UX release the slot, frozen genuine PR checks and normal exact-head merge.
Bootstrap envelopes remain separate source-aware work; preserve page arrays and
unknown input populations. Package remains 0.26.5; no provider/native acceptance.

## Historical PSI handoff

## PSI coverage integrated candidate — 2026-10-13

PSI source 50e7c3e passed parent independent review and 67 focused controls,
including actual standalone loopback JSON/Markdown. Accepted GSC/R30 main
`3fac9d67e12c367b19d8f2cfcecaaed6badc2dd7` is now composed: PR34 genuine run
[38355003556](https://github.com/ssheleg/seo-aeo-audit/actions/runs/38355003556)
passed frozen 6172f3d; normal merge released both leases. Source version stays 0.26.5.

Integrated owner gate at d690b296164372c407fa7b65b2faa5d21146cd0b passed:
31 negative groups and 9 audit regression files. Next: freeze this receipt head,
promote one eligible candidate PR and watch normal exact-head integration. See the
[PSI receipt](evidence/runs/2026-10-13-fw06-psi-coverage.md) and
[contract](contracts/collector-coverage.md). Preflight/bootstrap contract is on
separate plan/fw06-preflight-coverage at 8879a66; no preflight code changed yet.
No live provider, native-host or complete B-9 claim.

## Historical GSC/R30 handoff

## GSC/R30 owner gate passed — 2026-10-13

Combined implementation and cache correction at `12ca7004fcebcf8b4197369002989e26fd72c4fc`
passed `npm run test:all`: 31 negative groups, 9 audit regression files. Source
and correction received independent parent review; receipts below retain failures.
Next: freeze this documentation head, open/promote one candidate PR, require genuine
checks, then normal exact-head merge. Release/version remain unchanged at 0.26.5.
PSI reviewed successor `50e7c3e898602ab221b53cccb66620354fce5aec` waits for accepted
composition before its own owner gate. Preflight/bootstrap packet remains open.

# Combined GSC and R30 candidate — 2026-10-13

GSC source de16b2baeb07b22a13af7662fa2ae56a1aa5db06 passed independent
76-control review after both aggregate overflow findings were repaired. R30 source
99653a0b211e737ad43a0884f2e801742666d0e5 passed independent 28 board/validator
and 27 local-Git release controls. See the separate
[GSC receipt](evidence/runs/2026-10-13-fw06-gsc-coverage.md) and
[R30 receipt](evidence/runs/2026-10-13-r30-owner-gates.md).

Next: run one exact combined owner `npm run test:all` after the serial slot clears,
then freeze/push the evidence, promote one genuine PR candidate and watch normal
integration. Package remains 0.26.5; provider/native acceptance remains NOT_RUN.
Agent-surface PR33 already landed normally at e8aa59e with genuine checks.
PSI implementation is on separate plan/fw06-psi-coverage, whose approved packet
is `docs/evidence/plans/2026-10-13-fw06-psi-coverage.md` at 29041dc.
Preflight and early bootstrap envelopes remain open. No complete FW06 claim.

## Historical task context

# B-9 agent-surface coverage candidate — 2026-10-13

Read [the execution receipt](evidence/runs/2026-10-13-fw06-agent-coverage.md) and
[the packet](evidence/plans/2026-10-13-fw06-agent-surface-coverage.md). Accepted
sitemap source is `dd5319a8935d60d0db7b3649b528d31d0b9ac45f` (PR32, genuine run
38348112306 passed both jobs). This candidate journals hidden probes and keeps
network/local units separate. Version remains 0.26.5. Next: focused independent
review, then one owner aggregate only after the serial/disk slot is released,
frozen genuine PR checks and normal integration. GSC, PSI and preflight remain
separate migrations with their own denominators/provider boundaries.

---

# B-9 sitemap candidate — 2026-10-13

Read the [bounded packet](evidence/plans/2026-10-13-fw06-sitemap-coverage.md).
Implementation and measured checks are in the [execution receipt](evidence/runs/2026-10-13-fw06-sitemap.md).
Accepted B-33 source is `b28269fe72752ac9dc6ff0c6df8eaae4b4ac0e0a`; the earlier
B-33 handoff below is historical. Version stays 0.26.5. Owner aggregate and independent bounded review passed at
`40c95d3c4d3267148e16e4767f28d28664ef3885`. Next: frozen genuine PR32 checks
and normal integration. Then
take agent-surface discovery coverage from the common migration contract; its
unlisted discovery requests need instrumenting before displayed rows can be counted.

---

# FW06 B-33 attribution implementation — 2026-10-13

The [execution receipt](evidence/runs/2026-10-13-fw06-attribution.md) owns current
status and exact checks; the [packet](evidence/plans/2026-10-13-fw06-guard-attribution.md)
owns baseline scope. All 63 helper identities name their intended diagnostic.
Final focused 93 controls and independent 19 extras pass at `22dc235`; corrected
real groups pass 53 structural and 10 behavioral calls. The earlier full
`npm run test:all` passed at `4364c48`, including all 31 negative groups.

Next: deliberately promote frozen PR31 once, observe genuine required checks,
then normal integration. Keep version 0.26.5 until separate combined coverage/
attribution packaging. Continue the separately pushed sitemap coverage packet
on accepted source without waiting for an unrelated release. Provider/native
acceptance and standalone negative-step attribution remain outside this packet.

---

# FW06 B-33 preparation, 2026-10-13

Plan-only branch `plan/fw06-guard-attribution` preserves the complete measured
helper-call population and the next implementation packet in
[the attribution plan](evidence/plans/2026-10-13-fw06-guard-attribution.md).
Current measurement: 33 anonymous structural, 20 named structural and 10 anonymous
behavioral calls. A table-row selector also matches unrelated input; not repaired
here. No workflow or guard implementation changes in this preparation.

Next: integrate accepted B-9 correction, claim the separate B-33 task, then execute
the packet's selector/attribution controls before broad suites or release work.

---

# FW06 common coverage first slice, 2026-10-13

Branch `fix/fw06-collector-coverage`, based on release candidate `6a443b4`,
implements common invocation coverage in page audit and URL Inspection. Read the
[task receipt](evidence/runs/2026-10-13-fw06-coverage.md) and
[schema/migration matrix](contracts/collector-coverage.md). No version or workflow
change; B-9 remains open for five collectors and pre-report bootstrap failures.
Baseline two missing-emission controls were red; restored focused controls pass
115/115 after the independent partial-unknown bound correction, with three
intended real-source mutation refusals. No live/provider or
native-host acceptance is claimed.

Accepted 0.26.5 main `bccb630e79730e2a7058b74a2130ddfe4f4662aa` was merged
without rewriting this published branch; its standard retro stamp is preserved.
Owner `npm test` passed at `7976831`, including coverage 115/115; see receipt.
Independent corrected-source review passed at `7976831` with replayed 115/115.
Next: freeze the candidate for genuine required checks and normal PR delivery.
Keep the parent release branch and manifests untouched.

---

# FW01/FW06 patch release candidate, 2026-10-13

Branch `release/fw06-0.26.5` prepares 0.26.5 from accepted main
`4f4b53026d556f405ec9dd6600ea5898f1e91786` (PR28), including FW01 PR27.
The [FW06 receipt](evidence/runs/2026-10-13-fw06-collectors.md) records
implementation, independent review and local source checks. Packaging changes
versions, changelog and evidence only; script SKILL_VERSION identifies output provenance.

Frozen f7d1dd50ff3e86654711b0efd7e4b9d109603166 passed `npm test` (exit 0).
Independent packaging review passed all 15 files, including byte comparison proving
the seven script changes are SKILL_VERSION constants only.
Exact next task: normal PR merge, then annotated v0.26.5 tag and genuine release/registry readback.
Publication, parent pin and installed update are pending. B-9 and remaining B-33
work retain their explicit scope; a patch release does not close the full board.

---

# FW06 collector provenance, 2026-10-13

Objective: distinguish observed redirects, landing responses and incomplete gzip
input. Baseline `fbb721b2d26b6cfe1a966b90b093d9ba6e452110`; branch
`fix/fw06-collector-provenance`. Read the
[FW06 receipt](evidence/runs/2026-10-13-fw06-collectors.md) for reproduced failures,
checks and residuals. B-7/B-22 have local implementation/fixture coverage; B-9's
[migration contract](contracts/collector-coverage.md) is defined but not uniformly
implemented. B-33 is still open beyond the one affected I/O plant.

Exact next task: independent frozen-source review, then parent-owned integration and
release. Follow with common coverage emission and guard-specific legacy plant
attribution, preserving unknown quantities. No provider credentials are needed for
the delivered slice; live/provider acceptance remains separate.

## Prior FW01 snapshot accounting, 2026-10-13

Objective: account for the negative-runner snapshot on success and failure.
Implementation and three bounded regression cases are complete on this branch.
Read the [receipt](evidence/runs/2026-10-13-fw01-snapshot.md) for the base revision,
checks, limitations, shared-runner seam and exact next task: independent review,
then coordinator-owned integration and aggregate validation. No release was made.
The make-skill guard half is a separate owner change. Other open work remains in
[evidence/backlog.md](evidence/backlog.md).
