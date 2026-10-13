# Collector coverage migration contract

Status: first B-9 migration slice emits `collector-coverage/1` from
`page_audit.py` and `url_inspection.py` when collection reaches report emission.
The remaining five scripts are not migrated; B-9 remains open. This schema is
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
and `test/audit_regressions/fw06_probe_provenance.py`. These tests do not yet verify
the proposed common schema.

## First migration slice: invocation records

| Collector | Unit and input normalization | Usable return and carrier | Remaining boundary |
|---|---|---|---|
| `page_audit.py` | `input_url_entry`; duplicates retained exactly as input, or `local_file` for offline HTML | A complete readable HTML body, including a genuinely empty body. A cap or incomplete gzip stream is partial, even when recovered text can be analyzed. The existing JSON array is preserved; each element repeats the **same invocation coverage record**, like its producer block. Read it once; never sum the copies. Markdown prints it once. | Completeness excludes JavaScript rendering and sitewide discovery. Argument, input-list and local-file opening failures before report creation keep their existing stderr/exit behavior. |
| `url_inspection.py` | `unique_input_url`; exact-string duplicates removed before the cap | A nonempty index-status answer under the existing `answered_rows` predicate. The existing JSON object gains `coverage`; result fields and exit behavior remain. A response with no index-status data is an attempted input without a usable return. | Completeness is only for requested unique URLs, not every field or the property's universe. Credential bootstrap and input-file failures before collection keep existing stderr/exit behavior. Nonpositive caps are rejected before credential access. |
| `sitemap_audit.py` | Migration pending | Sitemap traversal, indexes and samples need their own universe boundary. | No common coverage claim. |
| `agent_surface.py` | Migration pending | Instrument hidden discovery attempts before counting requests. | Displayed checks are not all network attempts. |
| `gsc_pull.py` | Migration pending | Distinguish API rows, windows and unobserved tails. | No inference of missing rows as zero. |
| `psi_pull.py` | Migration pending | Define field-data absence separately from lab-response success. | No provider completeness claim. |
| `preflight.py` | Migration pending | Keep readiness probes separate from track coverage and collection. | Existing track status vocabulary is unchanged. |

For the first two collectors the finite inputs are accounted as requested =
attempted + dropped; network/API failures remain attempted. `returned` excludes
failures and unusable/incomplete responses rather than converting them into dropped
inputs. Machine reasons currently include `input_failed`, `incomplete_body`,
`input_cap` and `no_index_answer`. The shared builder supports null counts only with
an explicit reason and emits state `unknown`; zero is never its default. Early
bootstrap failures with no record are not complete coverage and remain a migration
boundary. A consumer must require an actual record, not infer success from its absence.

The small builder/Markdown block is duplicated intentionally in the two standalone
scripts. `test/collector_coverage_contract.py`, invoked by the existing
`test/test_output_contracts.py` gate, compares those copies and independently checks
the schema. Its loopback cases cover redirect hops as one logical input, connection
failure, HTTP 404, an empty complete body, full/capped/incomplete/corrupt gzip, mixed
results and duplicates. Mocked URL Inspection cases cover caps, absent index data,
API failure and exact input deduplication without credentials or provider traffic.
Markdown and JSON counts/state agree in these fixtures. This does not establish live
provider, browser or native-host acceptance.
