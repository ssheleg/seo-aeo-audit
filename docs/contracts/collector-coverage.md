# Collector coverage migration contract

Status: B-9 migration emits `collector-coverage/1` from `page_audit.py`,
`url_inspection.py`, `sitemap_audit.py`, `agent_surface.py`, `gsc_pull.py`, `psi_pull.py` and `preflight.py` when collection
reaches report emission. All seven collection paths now emit records; early bootstrap boundaries keep B-9 open. This schema is
separate from the existing audit-track coverage vocabulary. The earlier FW06
provenance slice preserves its redirect and gzip evidence.

Every migrated collector coverage record declares its unit and scope before its
counts. URLs, response bodies, API rows and checks are different units and must not
be summed. Use `null` for an unknown quantity, with a reason. Zero requires a counted
empty set. A fetch failure, unvisited page window or missing field is not zero rows.

| Field | Meaning |
|---|---|
| `schema` | Fixed identifier `collector-coverage/1`. |
| `scope` | The invocation, input normalization and meaning of a usable return; never an implicit whole-site claim. |
| `unit` | What one item means, for example an input URL or returned API row. |
| `requested` | Known input items requested by the operator, before a local cap; null if the remote universe is not enumerable. |
| `attempted` | Known items actually attempted. Retries and redirect hops belong in transport evidence, not extra logical items. |
| `returned` | Items with usable responses for this collector's stated question. An HTTP 404 can answer a status probe while providing no usable page body. |
| `dropped` | Known input items deliberately omitted by a cap or filter. A remote long tail has unknown size, not a fabricated dropped count. |
| `state` | `complete`, `partial` or `unknown`, relative only to the declared scope. Complete requires an enumerable requested set, an accounted attempt per retained item and no hidden truncation. |
| `reasons` | Machine-readable reason plus bounded human explanation for each gap, failure or unknown count. |

Known counts are nonnegative integers; never silently coerce missing values to zero.
No known attempted, returned or dropped count may exceed a known requested
population, even when another quantity is null.
Where all counts share the same finite input set, attempted plus deliberately dropped
equals requested. Failed attempts remain attempted and reduce returned; they are not
counted a second time as dropped. A bounded successful response does not establish
sitewide or provider-dataset completeness.

For response provenance keep requested URL, observed redirect status/target pairs and
landing response status/URL distinct. On a failure after a redirect, earlier hops are
observed while the landing response is unknown. For gzip distinguish a complete
empty body from a corrupt or salvaged partial stream; counts over recovered text are
observations of that fragment, not totals for the whole page.

## Migration and evaluation order

1. Inventory each collector's current JSON, text, cap/filter and exit semantics before
   changing its envelope. Preserve standalone script installation and old consumers.
2. Add a common executable validator for the schema in the owner tests; fixture both
   missing/unknown and genuine empty results. Do not equate a schema pass with live
   provider acceptance.
3. Migrate URL-input collectors first, then sitemap traversal and agent-surface
   discovery. The latter's displayed check rows are not a count of all requests:
   alternate discovery probes can be unlisted. Instrument attempts before adding
   coverage totals.
4. Migrate GSC and PSI only with explicit row/window and field-versus-lab contracts.
   An API limit that was reached leaves the unseen tail unknown. Pagination/provider
   acceptance remains a separate packet with its own authority and fixtures.
5. Verify text/JSON agreement, partial and empty results, redirects, transport failure,
   truncation and a completeness-flag mutation in every migrated collector. Keep B-9
   open until all declared collector homes emit and validate the same contract.

Source: owner B-9 and FW06 code inspection at baseline
`fbb721b2d26b6cfe1a966b90b093d9ba6e452110`; executable current behavior is covered by
`test/test_page_audit.py`, `test/test_collectors.py`, `test/test_agent_surface.py`
and `test/audit_regressions/fw06_probe_provenance.py`. The later contract helpers below verify the migrated common schema with offline
and loopback fixtures; the baseline inventory is historical.

## First migration slice: invocation records

| Collector | Unit and input normalization | Usable return and carrier | Remaining boundary |
|---|---|---|---|
| `page_audit.py` | `input_url_entry`; duplicates retained exactly as input, or `local_file` for offline HTML | A complete readable HTML body, including a genuinely empty body. A cap or incomplete gzip stream is partial, even when recovered text can be analyzed. The existing JSON array is preserved; each element repeats the **same invocation coverage record**, like its producer block. Read it once; never sum the copies. Markdown prints it once. | Completeness excludes JavaScript rendering and sitewide discovery. Argument, input-list and local-file opening failures before report creation keep their existing stderr/exit behavior. |
| `url_inspection.py` | `unique_input_url`; exact-string duplicates removed before the cap | A nonempty index-status answer under the existing `answered_rows` predicate. The existing JSON object gains `coverage`; result fields and exit behavior remain. A response with no index-status data is an attempted input without a usable return. | Completeness is only for requested unique URLs, not every field or the property's universe. Credential bootstrap and input-file failures before collection keep existing stderr/exit behavior. Nonpositive caps are rejected before credential access. |
| `sitemap_audit.py` | `unique_sitemap_document`, exact discovered URL identity including root; or `local_file` offline | Complete parseable XML documents, including empty URL sets; page URL entries remain separate analysis counts. JSON keeps its existing object and adds `coverage`, `traversal`, `errors`; Markdown prints one coverage block. | Failed/capped documents and offline nested references can hide descendants: requested is null with `unknown_frontier`. `traversal.known_discovered` preserves measured discovery; dropped counts known unattempted documents only. No whole-site claim. |
| `agent_surface.py` | `network_probe` counts scheduled logical request invocations, including repeated/header variants; supplied offline JSON uses separate `local_file` | New `coverage_by_unit` map contains common records under their unit names; `network_probes` journals every fetch, including unselected alternatives and CLI-only OpenAPI/API probes. | No cross-unit sum. Discovery prerequisites with incomplete/no bodies keep requested unknown. Complete landing status/body is not a complete field analysis or site universe. |
| `gsc_pull.py` | Six logical `api_request` operations and four separate row populations (`date_row`, `query_row`, `page_row`, `query_page_row`) | Additive `coverage_by_unit`; usable typed API envelopes may be empty. Row populations remain unknown, while observed attempts/invalid/noise/display counts remain explicit. | Credential bootstrap and list-only paths keep their early boundaries. No provider-wide completeness, pagination or live acceptance claim. |
| `psi_pull.py` | `input_url_entry`, singular `coverage` | Supplied entries retain duplicates; return requires valid URL-field percentile or lab score. | Origin-only context is preserved but not a direct URL measurement; missing field/lab is partial. |
| `preflight.py` | `local_probe` and `network_probe` under additive `coverage_by_unit` | Local returns are determined prerequisite outcomes; network returns are observed landing HTTP statuses. Visible rows are not the denominator. | Existing track-list `coverage` stays intact. Non-success access, incomplete bodies and unavailable required payloads are limitations, even with observed status. |

For the first two collectors the finite inputs are accounted as requested =
attempted + dropped; network/API failures remain attempted. `returned` excludes
failures and unusable/incomplete responses rather than converting them into dropped
inputs. Machine reasons currently include `input_failed`, `incomplete_body`,
`input_cap` and `no_index_answer`. The shared builder supports null counts only with
an explicit reason and emits state `unknown`; zero is never its default. Early
bootstrap failures with no record are not complete coverage and remain a migration
boundary. A consumer must require an actual record, not infer success from its absence.

The small builder/Markdown block is duplicated intentionally in the seven migrated standalone
scripts. `test/collector_coverage_contract.py`, invoked by the existing
`test/test_output_contracts.py` gate, checks the first two copies and independently checks the schema.
`test/sitemap_coverage_contract.py`, called by the same gate, compares the first three
copies and adds traversal/transport acceptance cases. Its loopback cases cover redirect hops as one logical input, connection
failure, HTTP 404, an empty complete body, full/capped/incomplete/corrupt gzip, mixed
results and duplicates. Mocked URL Inspection cases cover caps, absent index data,
API failure and exact input deduplication without credentials or provider traffic.
Markdown and JSON counts/state agree in these fixtures. This does not establish live
provider, browser or native-host acceptance.


## Sitemap document population and failure envelope

The requested set is the root and exact unique sitemap URLs discovered through
complete XML documents. Deduplication happens when enqueuing, before the attempt
cap, so a repeated or cyclic reference does not create a skipped item. Successful
empty XML URL sets count as returned documents; a zero-byte body is not parseable
XML and does not. Redirect hops are not counted separately and this collector does
not claim a redirect-chain receipt.

A failed or unvisited document may be an index hiding additional descendants.
`requested=null` and `unknown_frontier` preserve that uncertainty. The traversal
object also carries `known_discovered` and `offline_nested_references`. In local
mode the unit is the single file: nested URL references are separate observations,
not additional attempted/dropped local files. An offline index can leave the
reachable declaration unknown even though one local document was returned.

Raw and decompressed reads each use a bounded sentinel byte. Oversize, corrupt or
cut gzip and short declared HTTP bodies are excluded from returned documents and
reported as `incomplete_body`. Valid XML with more page entries than the existing
per-document URL cap counts as one returned document but adds `page_url_cap` and
partial coverage. The parser remains namespace-agnostic; this is no new claim of
full Sitemap protocol validation.

Once collection is attempted, error and no-page invocations now emit a report;
previously they could return before any JSON. Existing `producer`, `sources`,
`analysis` and `findings` remain; `sources`/`analysis.sitemaps_read` preserve their
legacy attempted-input meaning, while `coverage.returned` is the usable-document
count. Partial earlier page observations survive a later failure. Read/parse
errors and no-page runs still exit 1. A complete empty XML URL set therefore has
complete document coverage and exit 1: it yielded no page URLs to analyze.
Nonpositive `--max-maps` is parser usage failure (exit 2), before any fetch.

Evidence: `test/sitemap_coverage_contract.py` exercises actual loopback bodies,
mocked traversal, local files, JSON/Markdown/exit agreement, copied standalone
execution and three real-source mutants (duplicate accounting, omitted cap reason,
false complete state). Its execution receipt lives at
`docs/evidence/runs/2026-10-13-fw06-sitemap.md`. This is source/fixture acceptance,
not provider, whole-site or installed-host evidence.


A page `<loc>` that Python's URL parser rejects is excluded independently:
`page_errors` identifies its source, URL and diagnostic, `analysis.urls_invalid`
counts exclusions, and `invalid_page_url` makes coverage partial. Other page
observations survive; the fully parsed XML document remains returned. JSON and
Markdown still emit, with exit 1. This handles parser errors, not every possible
semantic URL or Sitemap protocol violation.


## Agent-surface carriers, attempts and usable responses

`agent_surface.py` adds `coverage_by_unit`, a named map. Its `network_probe` value
is one common record; `local_file` is present only when an offline OpenAPI input
was supplied. Existing `coverage` object/array carriers in the other collectors
are unchanged. Preflight's track-coverage object is a different vocabulary and is
not a collector record. The independent `coverage_records` reader in
`test/collector_coverage_contract.py` recognizes explicit common carriers,
collapses repeated page-array copies once and refuses ambiguous competing
collector records, including competing carriers inside a repeated page-array row.
It never sums units or interprets track rows as probe counts.

The network record counts scheduled logical invocations, not unique URLs or
rendered checks. Accept/User-Agent variants and repeated calls remain distinct;
physical redirect/retry hops do not add logical inputs. `network_probes` retains
requested URL, request variants, observed status/final URL/redirects and body
completeness/errors. A returned probe has a landing status and complete readable
body, including empty or 404 bodies. Observed status/headers remain evidence when
a cap, short body, malformed Content-Length, unsupported encoding or corrupt/cut gzip excludes a complete
return. Reads and gzip output use separate sentinel bounds. Existing analysis of
available fragments is qualified by coverage; this is no field-completeness claim.

The chosen finite conditional workflow defines the input population. A failed or
incomplete initial missing-path response, homepage, separate markup page, robots
file or parent sitemap can hide
inputs to the next discovery branch: requested is null with `unknown_discovery`.
Failed fixed inputs remain known attempts without returns. Alternatives made
unnecessary by successful selection do not become missing requests. Dropped is
currently zero; unknown descendants are not invented numerical omissions. The
scope excludes sitewide discovery and JavaScript rendering.

Remote OpenAPI and API-header probes in `main` participate in the same journal.
The local-file unit measures one supplied read and bounded analyzer acceptance of
a JSON object, not full OpenAPI validation. Read/parse/analyzer failures produce
`payload_errors`; other observations survive. Remote response collection and
OpenAPI payload usability are distinct: the latter can add `unusable_payload`
while the complete response remains observed.

The documented exit rule now counts observed landing responses across the actual
journal, including hidden near-miss requests. Previously `_answered` counted
selected display rows and could say every probe failed when an unlisted one had
a landing response. Exit 0 still means at least one response or usable offline
spec, not that every probe or field succeeded. Markdown and JSON emit all present
unit records. `test/agent_coverage_contract.py` verifies this through mocked
requests, actual loopback transport, copied CLI runs and executable mutations;
its receipt is `docs/evidence/runs/2026-10-13-fw06-agent-coverage.md`.


## GSC request and row accounting

The full-report branch runs six independent logical API operations after credential
bootstrap: properties, date/query/page/query-page Search Analytics and sitemaps.
`api_operations` records them; `collection_errors` preserves bounded diagnostics
with the credential value redacted before JSON/text rendering. A returned API
operation has a typed collection envelope; an empty list counts as observed.
Malformed envelopes and failures do not erase earlier dimensions. Auxiliary row
shape failures are separate diagnostics; their valid siblings remain available.

Four row records keep `requested=null`: a single page cannot enumerate the
provider population, including when fewer than the configured cap arrive.
`attempted` counts received rows after valid noise rows are deliberately excluded;
invalid rows remain attempted without usable returns. `returned` counts individually usable rows admitted to analysis, and `dropped` counts known noise only. An unavailable row envelope
leaves all row counts null. An actually empty list permits measured zero counts.
`row_observations` reports received, invalid, noise and analyzed counts separately.
The aggregate noise count is null when either noise-bearing dimension is unknown.

All four row limits are named, including date's 25,000. Reaching a limit adds an
uncertainty reason, never a numeric unseen tail or proof that more rows exist.
JSON top-query/page lists show 100 rows and pair lists 5,000 after analysis;
`display_omitted_json` records that presentation cut without reducing analyzed
returns. Text top-query/page lists show 30; their separate omission count is
measured. Date and query-page text sections are transformed summaries, so their
raw-row display omission is null, not a claim that all raw rows were displayed.
Failed/empty dimensions carry observation state beside legacy derived keys and
cannot render an unqualified clean collapse/cannibalization/sitemap conclusion.
The existing useful-row exit predicate remains: valid empty responses are observed
but a report with no usable rows exits 1.

`test/gsc_coverage_contract.py` verifies mocked failures in every request position,
invalid versus zero rows, noise/display arithmetic, cap/unknown distinctions,
redaction, early branches and real loopback transport through copied standalone
CLI invocations. Provider behavior and pagination performance remain NOT_RUN.
Primary-source interpretation is recorded in
`docs/evidence/plans/2026-10-13-fw06-provider-coverage.md`.


Finite individual values can still overflow an aggregate. Each GSC derivation is
isolated, and sums refuse nonfinite results without imposing a traffic ceiling.
A failed calculation has a null derived value and a named `derivation_errors`
entry; its row observation and coverage reasons qualify that failure. Other
calculations and raw usable rows survive. `analyzed` counts individually usable
input rows admitted to the analysis, not successfully computed aggregates.
JSON never uses Infinity/NaN to represent an unavailable aggregate, and text names
the failed calculation instead of reporting a clean negative. Monthly, cliff,
position, brand and cannibalization aggregate paths have explicit controls.

## PSI entry and component accounting

`psi_pull.py` retains its JSON object and adds singular `coverage`. The unit
`input_url_entry` counts supplied entries, including duplicates, once each. A
return requires a finite nonnegative recognized URL-field percentile or a valid
Lighthouse performance score in [0,1]. Zero is data; strings, booleans, negative
and nonfinite numbers are not. Origin aggregates remain context, do not make a
URL returned, and never replace URL-field observations. The same useful predicate
owns exit status: all-empty/origin-only invocations emit reports and exit 1.

`component_status` separates URL field, origin context and lab. URL field is
observed only when all three recognized percentiles exist, partial with a subset,
unavailable with none. Any missing URL-field percentile or lab score makes the
invocation partial even when every entry returned something useful. Origin is
optional context; its absence alone does not make direct measurement partial.
This is input/component accounting, not provider population or field eligibility
certification. The report does not infer a cause from absent field data.

Malformed components carry `payload_errors`; usable siblings and later entries
survive. Unknown recognized metrics stay present with null p75/unknown band.
Transport/API errors preserve their entry; raw and URL-encoded supplied-key echoes
are redacted before diagnostic truncation. HTTP error-body read failure preserves
the status and reports an unavailable body. Default Markdown and JSON include the
same counts and component limitations. No-URL/unreadable-list bootstrap branches
still precede report creation and remain open boundaries. The following preflight slice aligns recognized finite measurement presence;
historical R-4 evidence alone does not prove the current predicate.

`test/psi_coverage_contract.py`, called by `test/test_output_contracts.py`, checks
these predicates, six standalone block copies, a false-success mutation and an
actual copied CLI against loopback. Live provider/installed-host evidence is
NOT_RUN. The frozen task packet is
`docs/evidence/plans/2026-10-13-fw06-psi-coverage.md`.

## Preflight readiness accounting

`preflight.py` preserves its JSON `coverage` track list and adds `coverage_by_unit`
with two common records. `probe_operations` records local prerequisite outcomes
and logical network attempts without credentials or provider bodies. Local scope
is Python plus optional ADC when `--site` is supplied. A local return means a
determined outcome, including unavailable credentials; the latter remains partial.
Network scope is one property-list request for `--site`, three public requests for
`--origin`, and PSI unless skipped. A missing ADC excludes exactly one known
network operation before attempt. The property-match display row is derived from
the same property-list response and never counts twice.

Here a network return means an observed landing HTTP status. It does not mean a
useful provider payload. Transport failure returns none; non-200, incomplete/capped
or undecodable body and unusable required JSON add explicit limitations. These
return semantics differ from full-body collectors and are stated in each record's
scope. Known scheduling by flags is not an unknown site population. Only the first
declared sitemap or fallback is requested; incomplete robots qualifies selection
without implying a full crawl. Gzip/raw caps and malformed length remain explicit.
Preflight admits equal normalized repeated Content-Length values, but marks
contradictory repeated lengths and TE+CL combinations partial while retaining status.

Typed empty GSC property lists can establish absence. Malformed rows cannot: valid
matches survive, but unmatched property access stays unattempted/unknown while
other probes continue. PSI scalar/wrong JSON and nested components never erase
previous results. Finite recognized URL-field percentiles, origin context and lab
score remain distinct; no field absence cause or synthetic score is invented.
Known token echoes are redacted before truncation and failed ADC stderr is withheld.

JSON/default Markdown show common records; `--format coverage` still performs
probes and prints the track seed, then the common records. `--format provenance`
remains a no-probe seed, without invented collection records. Exit 0 means a
preflight report was produced, not that every prerequisite/source succeeded.
No-input usage and other collector bootstrap failures remain open.

`test/preflight_coverage_contract.py`, integrated into output contracts, exercises
the flags, measured versus inferred states, seven byte-identical builder copies,
an actual accounting mutation and a standalone copy with loopback/fake ADC. No
provider keys, live service acceptance or native-host evidence are involved.

### Shared bounded transport admission

All seven standalone collectors carry the same byte reader; they retain their
own return units. `test/transport_contract.py` compares the copies and exercises
actual loopback responses, copied scripts and false-completeness/uncapped-read
mutations. Equal normalized repeated/comma-separated Content-Length values are
admitted. Malformed or conflicting values, Transfer-Encoding combined with
Content-Length, unsupported transfer codings and repeated/unsupported content
encodings cannot certify a complete body. Supported chunked framing is decoded
by urllib. Identity and gzip are the supported content encodings.

The reader limits raw bytes and gzip output independently, requesting one sentinel
byte beyond each budget. Page audit uses `--max-bytes` for **both** budgets; a small
compressed representation does not authorize a larger decoded report. A recoverable
HTML prefix remains partial and supports only existing fragment findings; an
incomplete body with no recovered bytes is a failed fetch. Sitemap XML requires a
complete body. Agent-surface/preflight retain observed status while naming body
limitations. Their different returned-unit definitions above still apply.

PSI, GSC and URL Inspection use `MAX_RESPONSE_BYTES = 8_000_000` for both raw and
decoded provider JSON. This bounds one response, not provider population or traffic.
An incomplete body supplies no usable JSON envelope and no typed empty row set.
HTTPError bodies use the same bounds; read failures do not escape to erase other
operations, and known credential echoes are redacted before diagnostic truncation.
The preflight JSON budget remains caller-selected. No provider access or universal
HTTP protocol validation is established by these local transport controls.
