# FW06 next B-9 slice: sitemap traversal coverage

Status: implemented in candidate; checks/review/integration state belongs to
[the execution receipt](../runs/2026-10-13-fw06-sitemap.md). Original packet follows.
Planning snapshot: planned, not implemented. Source observed at
`4364c4867d34b05e9e2d0f5e00da53a9b5889106`; this branch is stacked on the B-33
candidate and must incorporate its accepted source before implementation. The
[common contract](../../contracts/collector-coverage.md) remains the single schema
home. No package version, source script, workflow or board status changes here.

## Reproduced baseline and read-only findings

- `sitemap_audit.py:169` reads up to the byte limit without a sentinel byte, then
  decompresses gzip without an output limit. A caught gzip error falls back to
  decoding compressed bytes. This path emits no transport-completeness evidence.
  This is a source observation; no oversized network response was fetched.
- A fully mocked root index containing the same child twice, child containing one
  page, and `--max-maps 2 --format json` returned exit 0 after exactly two fetches.
  `analysis.sitemaps_skipped` was **1**, while the unique unvisited set was empty.
  The cap check precedes removal of already-seen queue entries (`main:352`), so an
  already-read duplicate is counted as skipped. No provider/network call occurred.
- `--max-maps -1` was accepted, performed zero fetches, emitted no JSON and returned
  1. Nonpositive values must fail as usage before collection, consistent with the
  prior URL Inspection cap correction.
- Local sitemap indexes report nested references only on stderr (`main:346`). A
  valid empty URL set and any read/parse failure return before report emission.
  A future consumer must not infer complete coverage from an absent record.
- `agent_surface.py` has hidden fetches in alternative discovery at lines 923 and
  1176; displayed `checks` cannot be reused as its attempt denominator. It is the
  next separate migration, not an extension of sitemap URL counts.

## Implementation packet

1. Reconcile accepted B-33 source, read owner instructions/retro and acquire a
   unique lease before guarded docs. Preserve standalone script installation.
2. Pin unit `unique_sitemap_document` for this record. Document normalization as
   exact input/discovered URL identity, with a distinct local-file case. Retries,
   redirect hops, page URL entries and documents are separate units. Deduplicate
   queued and already-seen documents before counting cap omissions; count an
   attempted failed document once. Preserve the existing `analysis` page counts
   and qualify their fragment/cap scope instead of summing them into document counts.
3. Instrument traversal before emission. Requested population is only discovered
   document inputs, never the entire site. A capped/unread index may hide additional
   descendants: explicitly carry the unknown frontier and prevent a whole-site or
   fully traversed-tree claim. Decide and record whether that record's `requested`
   becomes null or a known bounded discovered-set count with an unknown-frontier
   reason; either must satisfy the common schema and the written scope. Do not
   invent a numerical dropped count for unseen descendants.
4. Bound both raw and decompressed body reads with sentinel detection. Preserve
   complete empty input versus incomplete/corrupt gzip distinctions. Record actual
   observed redirect/landing data if adding transport provenance; never reconstruct
   redirects from final URL comparison. XML parse failure is not a usable document.
5. Emit additive JSON `coverage` and one Markdown coverage block using the shared
   schema. Preserve existing keys and source/findings semantics. Make early
   bootstrap/empty/partial-failure report behavior an explicit compatibility
   decision with fixtures; current absence of output must not silently become a
   successful complete report. Preserve existing nonzero no-page/error semantics
   unless an owner contract and all consumers are changed in the same packet.
6. Add schema-copy parity with the two migrated scripts and independent reader
   cases. Add intended real-source mutations for omitted duplicate accounting,
   cap/incomplete-body reasons and a false complete state. Document standalone
   copied-script behavior from an unrelated working directory.
7. Update the one migration matrix, references/scripts.md, owner receipt/HANDOFF
   and B-9 state in the same change. B-9 remains open for agent-surface, GSC, PSI
   and preflight until each has its own measured unit and completeness boundary.

## Required local evidence before broad gates

Mock/loopback only: complete URL set; genuinely empty set; root index and nested
index; duplicate child before/at cap; cycle; cap 0/-1 refusal; failed root and failed
child after earlier success; local index that cannot follow nested maps; malformed
XML; full/empty/corrupt/cut gzip; raw and decompressed caps; retained page URL cap.
Read JSON and Markdown state/count agreement and exit behavior. A single visible
row cannot stand in for network-attempt coverage. Do not use provider credentials.

Run focused selector/schema/transport fixtures first. Request the serial broad
slot for owner gates, obtain independent review, and integrate a frozen candidate
through genuine checks. Publication/parent pins/installed/native acceptance remain
separate. No pre-authorization for payments or live providers is implied.

## Bounded implementation decisions (2026-10-13)

The [primary Sitemap protocol](https://www.sitemaps.org/protocol.html#sitemapIndex),
re-read on this date, limits each uncompressed sitemap/index to 52,428,800 bytes
and its entries to 50,000. These are document limits, not an assurance that the
site's whole URL universe is enumerated. The existing raw-input budget remains a
separate transport limit; gzip output gets its own bounded read.

For the next implementation, choose `unique_sitemap_document` for remote traversal
and `local_file` for a single offline input. Count exact URL identities once when
enqueued. `returned` means a fully read, complete and parseable XML document,
including a genuinely empty URL set; it does not mean page URLs or indexed pages.
An XML URL-entry cap remains a separate analysis limitation/reason.

When traversal completes without an unresolved document frontier, `requested` is
the discovered unique document count. When a capped, failed or unread offline index
can hide descendants, `requested` is null with `unknown_frontier`; attempted and
returned remain measured. `dropped` counts only known discovered unattempted
documents, never hypothetical descendants. Retain an explicit known-discovered
count in traversal evidence so null does not discard observed information.

Preserve the existing top-level keys and no-page/error nonzero exit. Emit an additive
report once collection is attempted, including partial earlier successes and an
errors list; absence of usable page URLs is not fabricated success. A valid empty
XML document may have complete document coverage and still return the existing
no-page exit 1, because collection completeness and having URLs to analyze answer
different questions. Usage failures remain parser errors before collection.

Do not add live-provider, browser, whole-site or sitemap-spec conformance claims.
This packet does not broaden supported XML formats or implement stdin merely
because the inherited module docstring mentions it. Correct that inaccurate
input-surface sentence while documenting the actual CLI in the same change.
