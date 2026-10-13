# FW06 PSI input and component coverage

Objective: implement the [accepted packet](../plans/2026-10-13-fw06-psi-coverage.md)
without treating an empty API object, origin context or missing field percentile
as a direct URL measurement. Source is stacked on reviewed GSC de16b2b; reconcile
the combined accepted GSC/R30 successor before integration. Version remains 0.26.5.

## Source behavior and bounded evidence

`psi_pull.py` emits singular `collector-coverage/1` with unit `input_url_entry`.
Duplicates retain their order and each has one logical attempt. Returned means a
valid recognized URL-field percentile or lab score; unknown field metrics remain
null/unknown, origin aggregates remain context, and component limitations can make
coverage partial even with every entry returned. Empty/origin-only runs keep their
report and exit 1. Valid siblings survive malformed components. No new provider
or authorization path exists. The common block is byte-identical in six collectors.

An initial preimplementation fixture failed on empty-object false success and
missing coverage. The first implementation passed 43 controls; expanded fixtures
exposed and fixed empty-string error handling and the separate HTTPError-body read
failure path before freezing source. `python3 -B test/psi_coverage_contract.py`
now passes 67 controls: finite/zero versus malformed numeric values, component
absence, scalar/error envelopes, duplicates, unknown metrics, error echoes,
bootstrap boundaries, six-copy parity and a real false-success source mutation.
A copied standalone CLI makes eight total loopback requests across JSON/Markdown
runs with four inputs each: useful, HTTP429, invalid JSON and empty. It retains all
entries, returns one, marks partial, and redacts plain/URL-encoded fake-key echoes.
No provider key or remote PSI call was used.

The initial structural run after linking this receipt exited 1 because the file
was not yet written; that is a construction-order link failure, not source
acceptance. Final `python3 -B test/validate.py` and `python3 -B test/test_collectors.py`
exited 0. `python3 -B test/test_output_contracts.py` exited 0 with shared115,
sitemap127, agent73, GSC76 and PSI67 controls; its one owned tree was removed.
Independent review, owner full gate and normal PR admission remain pending.
The initial preimplementation failed fixture was removed after its red/green
evidence was recorded here; unrelated trees were preserved.

## Limits and exact next work

Live provider, installed skill/model and native-host acceptance are NOT_RUN.
No-URL and unreadable-list bootstrap branches remain pre-report boundaries.
Preflight retains its old broader field-presence heuristic and has not migrated;
the historical R-4 comparison is not current semantic equivalence. B-9 remains
open for preflight and bootstrap envelopes. No CrUX fallback, provider population
completeness, inferred absence cause or origin-to-URL substitution is claimed.

Next: finish focused/source review, merge accepted GSC/R30 into this branch,
then serialize the exact-source owner gate and normal eligible PR integration.
