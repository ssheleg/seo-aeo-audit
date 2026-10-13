# Shared helper header truth after 0.26.6

The family validator rejected two owner test files after the 0.26.6 pin: each
`diverges:` header described extraction history while the actual module-constant
divergence was empty. This is a declaration mismatch, not changed executable code.

The two comments now declare `diverges: none`; the previous explanation remains
verbatim under `extraction-note:`. No statement about supported Markdown, release
ancestry or UTF-8 refusal was removed. No package version, runtime, workflow or
published skill changed.

## Bounded evidence

- The actual hub `check_a_copied_mechanism_declares_its_divergence` function and
  its regex/threshold constants were extracted by Python AST into an owned
  two-copy fixture. [Before](red.json): two expected false-divergence refusals.
  [After](green.json): zero errors, both filenames actually compared above 0.90.
  This is the focused shared-header check, not a repeated whole-family suite.
- [Proof](proof.json): both full Python ASTs are identical to accepted main before
  this edit. Only the two comment headers changed; executable semantics are equal.
- `npm pack --json --ignore-scripts --pack-destination <owned-temp>` from this
  working tree was compared with the already verified immutable 0.26.6 manifest:
  all 46 files / 1,119,910 bytes match in paths, content hash, length and mode.
  Neither helper is part of the package. The temporary pack/cache was removed.

This correction needs normal source integration and the parent pin update, but no
new version or tag: the entire published payload is unchanged. Final family
composition validation remains the parent's gate. Source acceptance never implies
native/provider/model-quality observation.

Focused guard source: hub commit 2c4f099958269900cacc6a436c18e4b05b35ff12,
`test/validate.py`. Reproduce the current focused verdict with
`python3 docs/evidence/runs/2026-10-13-shared-header-truth/reproduce.py /path/to/hub/test/validate.py`
from the owner checkout; inspect the selected hub source before changing that input.
