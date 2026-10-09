<sub>ssheleg skills — task-pipeline · agent-sync · make-skill</sub>

# Robots matching and indexing-status correction

Candidate0.26.3 corrects bounded doctrine defects in the existing technical
reference and the linked copies of its indexing recipe. The [spec](spec.md) was
committed before reference edits at `4662879`; source baseline was0.26.2 at
`3f2ffd846d525483f88d82b388fb3b840a1bf688`.

## Evidence and resulting behavior

- [Google robots specification](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec),
  read2026-10-09: literal prefixes retain their trailing slash and case; wildcard
  and end-anchor examples include non-matches and complete-file precedence limits.
- [Google JavaScript processing guide](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics),
  read2026-10-09: an allowed resource does not prove an indexing outcome. Inspect
  the resources required by the content and the resulting render.
- [Google Page indexing report help](https://support.google.com/webmasters/answer/7440203?hl=en),
  read2026-10-09: discovered and crawled labels describe different stages.
  Site-specific causes need additional evidence; no fixed indexing rate/deadline
  or universal quality/authority diagnosis follows from either status alone.

The investigation/cohort guidance is an engineering interpretation, not an
additional Google requirement. The old undated success-rate claim is retained
only as an explicitly unsupported historical claim in benchmarks.md; it is removed
from operational acceptance. A patent also does not establish current capacity,
weights or inevitable dilution from publishing more URLs.

Changed knowledge: technical-checks A1/A2 and the matching statements in
architecture-and-equity, experiments, growth-plays L10, benchmarks and measurement
J5. No new reference was added; existing SKILL.md routing continues to load these
references. Metadata and the seven standalone producer-version literals move to
the same candidate version; no script behavior changed.

## Review extension

Google's [locale-adaptive guidance](https://developers.google.com/search/docs/specialty/international/locale-adaptive-pages)
was read2026-10-09: absent Accept-Language is now included in the test conditions,
with geo-distributed crawling acknowledged. [Peec's primary observation](https://peec.ai/blog/how-chatgpt-deep-research-reads-your-site-what-the-logs-reveal)
was also re-read: an explicit robots-denial accompanies the recorded empty result;
empty output alone cannot establish that cause. Corrected A1, growth-plays B9 and
added a dated correction alongside the original source-distillation shorthand.
The two additional frozen cases in spec.md pass manual artifact/source comparison;
no live request or model-outcome claim follows.

Final duplicate-home review corrected measurement's index-health row, the matching
quality-diagnosis clause in myths.md, the rendering-cause claim in technical-checks,
and canonical-acceptance assertions in technical-checks, growth-plays L13 and myths.
The same status alone proves neither a cause nor canonical acceptance. A second
licensed-publisher-whitelist assertion in aeo-geo's licensing paragraph now follows
its existing RESONEO source scope. Searches covered discovered/crawled with quality,
budget, rejection, authority, rendering and canonical terms, plus labrador/licensed
publisher variants across all references. The remaining matching cases were read;
historical observations and explicit uncertainties were not turned into guarantees.
The native gate was rerun after these corrections.

## Checks and limits

- Frozen source/rubric cases: all five expected judgments are now supported by the
  edited artifact. This is a manual correctness review, not a live agent trial.
- `npm test`: final exit0, full output in [npm-test.log](npm-test.log).
- `claude plugin validate . --strict` and
  `claude plugin validate plugins/seo-aeo-audit --strict`: both passed, exit0.
- make-skill0.29.0 `audit_skill.py <skill-dir> --house`: exit0,0GAP/19PASS;
  body4685/4750 working tokens measured with tiktoken:cl100k_base, description959/970.
- `git diff --check`: passed.

The first structural run rejected the ledger's release count36 after the candidate
made it37; the count was corrected and the full gate rerun. The review extension
also reduced reference lines across the README rounding boundary; the native guard
required its rounded total to follow the measured count: the earlier6050-line
draft rounded to ~6,000; the final6052-line reference set rounds to ~6,100. Standalone routed-trigger
checking reports `unlooked` because this checkout has no umbrella above it. No
routing effectiveness claim is made from that warning or the conformance checks.

Live with/without-skill model trials, an authenticated GSC property, real crawler
outcomes and measured indexing improvement are NOT_RUN. No site robots file,
Search Console account or provider configuration was changed. No publication,
merge, tag or installed-host update was performed by the author.

## Handoff

Independent root review requested one adjacent A2 correction about patent/capacity
inference; it is included in this candidate. Root owns the final independent review,
commit/remote integration, release and umbrella/install receipts. Next: review the
frozen final diff, then follow the normal member delivery policy. Coordination used
an explicit local advisory claim and an UNGATED author run; it provides no
cross-machine exclusion claim.

---

**Made with [ssheleg skills](https://github.com/ssheleg/sshlg-skills)**

- [`task-pipeline`](https://github.com/ssheleg/task-pipeline) — bounded implementation and review handoff
- [`agent-sync`](https://github.com/ssheleg/agent-sync) — local advisory file claims
- [`make-skill`](https://github.com/ssheleg/make-skill) — skill conformance and outcome limits
