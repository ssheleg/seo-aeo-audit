# Collector coverage migration contract

Status: defined for the next B-9 migration, **not emitted uniformly by the current
collectors**. The FW06 provenance slice changes redirect evidence and adds gzip
integration fixtures; it does not close B-9. This is the single proposed schema home
for that migration, separate from the existing audit-track coverage vocabulary.

Every future collector coverage record must declare its unit and scope before its
counts. URLs, response bodies, API rows and checks are different units and must not
be summed. Use `null` for an unknown quantity, with a reason. Zero requires a counted
empty set. A fetch failure, unvisited page window or missing field is not zero rows.

| Field | Meaning |
|---|---|
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
