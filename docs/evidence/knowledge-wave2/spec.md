# Bounded crawl and indexing doctrine correction

Frozen before reference edits, 2026-10-09. Base origin/main:
`3f2ffd846d525483f88d82b388fb3b840a1bf688` (0.26.2).

Requirements:

1. ROBOTS-PREFIX: distinguish a literal case-sensitive prefix, a trailing slash,
   wildcard and end anchor; no assertion that /account/ matches /account-settings/.
2. RESOURCE-SCOPE: blocked required resources can impair rendering; allowing a
   framework path does not by itself establish rendering or indexing success.
3. GSC-STATE: discovered/crawled statuses describe different observed stages;
   they do not identify one universal cause, prescribe opposite fixes or promise
   an indexing percentage/deadline from a latency/link recipe.

Primary sources read 2026-10-09:

- https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec — path
  matching, wildcards, rule precedence and crawl versus index distinction.
- https://support.google.com/webmasters/answer/7440203?hl=en — status definitions,
  URL Inspection and URL examples versus complete report coverage.
- https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
  — blocked resources and rendered content.

Frozen correctness cases (manual source/rubric comparison, no website mutation):

| Case | Expected artifact judgment | Static 0.26.2 baseline |
|---|---|---|
| /account/ tested against /account/profile and /account-settings/ | first matches, second does not; /account without trailing slash matches both | FAIL: explicitly claims second matches |
| /*print tested against /blueprints/ and /account/ | first matches, second does not; preserve wildcard distinction | PASS for the positive example; missing negative control |
| Required JS blocked, then robots rule allowed | inspect resulting render; no indexing guarantee | FAIL: says restores indexing |
| GSC discovered status without server/site evidence | found, not yet crawled; investigate without fixed cause or deadline | FAIL: budget exhausted plus fixed recipe/success range |
| GSC crawled status without causal evidence | crawled, not indexed; future inclusion uncertain; no automatic quality/authority diagnosis | FAIL: quality rejection and universal no-help assertion |

Home search found the same status recipe in technical-checks A2, architecture-and-equity,
experiments, growth-plays L10, the operational benchmark row and measurement J5.
Correct only those linked statements; preserve unrelated architecture and metrics.
Version metadata, standalone producer version literals, retro stamp, changelog and
verification ledger move together to candidate0.26.3. Public evidence only.

Validation: native npm test, both strict Claude manifest validators, make-skill house
conformance, source/rubric reread and independent root review. No new keyword-based
semantic guard will be presented as proof of Google behavior. Live with/without-skill
model trials, GSC property tests, crawling/indexing outcomes and release/install are
NOT_RUN here. Root owns review and delivery; author must not push, merge or tag.
