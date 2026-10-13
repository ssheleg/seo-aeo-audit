# FW06 preflight readiness coverage

The [accepted packet](../plans/2026-10-13-fw06-preflight-coverage.md) at
8879a667d3357336bca18eace8f8e67bec44344c owns the scope and source-bound baseline.
Parent accepted the distinct local-outcome/network-status return semantics before
implementation. This remains a bounded successor to reviewed PSI, not all B-9.

`preflight.py` now journals logical operations separately from visible probe rows.
`coverage_by_unit` is additive beside the unchanged track-list `coverage` carrier.
Missing ADC is one known excluded network input; a returned local prerequisite
outcome is not credential success, and observed HTTP status is not provider-data
success. Incomplete/capped bodies, malformed JSON and non-success access remain
explicit partial reasons. Known status survives body-read failure. GSC valid rows
survive malformed siblings, but absence cannot be established from an incomplete
list. PSI data types/finite measurements are qualified independently of lab/origin.

The original probe reproduced scalar PSI/GSC row exceptions, invented lab-only
classification, absent common carrier and the separately open Unicode list error.
The initial common-carrier regression ran red before source changes. The first
structural run correctly rejected SECURITY.md's old 34-line I/O claim after GSC
transport moved to the common bounded fetch: the published regex now measures 33
lines (13 urllib), and its total/category/subtotal and source pointer were updated.
No validator floor or workflow trigger was weakened.

`python3 -B test/preflight_coverage_contract.py` passes 78 controls, including an
actual standalone copy with loopback transport and fake ADC. JSON, Markdown and
coverage modes perform five network operations and display eight probe rows;
provenance does neither network nor ADC. It checks malformed/empty GSC/PSI,
retained matches, valid zero versus invalid/nonfinite measurements, body caps and
incomplete gzip/error responses, raw/encoded token echo redaction, seven identical
common blocks and a source mutation of excluded-input accounting. The one owned
fixture is removed on success. `test/test_collectors.py` also exited 0.

Structural validation and the combined output contracts exited 0 (115 shared,
127 sitemap, 73 agent, 76 GSC, 67 PSI and the initial 74 preflight controls).
Four further controls for deep JSON, invalid URL construction and malformed
HTTP200 Content-Length also passed in the final focused78 run. The initial
failed fixture was removed after preserving its red/green evidence here.
Independent source review and one serialized owner gate remain pending. No actual provider token, key, endpoint or installed agent was
used. No-input and per-collector bootstrap envelopes remain separate work;
preflight success exit still means a report was produced, not universal readiness.
Next: finish focused review, reconcile accepted PSI/main, freeze the exact source,
then run the owner gate after the serial slot clears and use normal PR admission.
