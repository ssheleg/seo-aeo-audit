# R30 SEO owner board and release guard packet

Scope: preserve the board's unique declarations and the existing release guard.
Family peer reproduced duplicate B-35 and an added middle column passing the real
SEO validator at dd5319a8935d60d0db7b3649b528d31d0b9ac45f. This packet starts
from accepted agent coverage e8aa59eaec85c2bceed4a2680c2e9892b53ab7ed.

Use the reviewed family bounded table parser from agent-stack
792e3f6cb2e46517f0187066db55edc63ae7d12c, extracted as owner_board.py in
agent-sync 8fd93be6383a7da0459e9c01f41a4ad164969e29. Declarations need an ID
header and immediate matching separator, stable width and unique IDs. Escaped
pipes remain content; ordinary prose, fenced examples and non-ID summary tables
are not declarations. Preserve explicit reference semantics rather than counting
mentions as work. Integrate the same tokenizer into SEO's status lookup.

Read the current release workflow before changing it. It already requires an
annotated tag, a full-history checkout and ancestry to the actual default branch.
The work adds validator protection against removal of the existing ancestry/depth
checks, not a new publication path. Reuse owner_release.py from agent-sync
cb4f9cea2e6ade637090bbde1afdb969dda4f459 and the make-skill 2785f6c residue-ledger
variant of its focused controls. This grammar is bounded to the family's layout;
it is not an arbitrary Markdown, YAML or shell interpreter.

Acceptance: actual structural-validator duplicate/width negatives and escaped
positive; unique declarations across tables, malformed/orphan headers and rows,
fenced status shadow; ancestry deletion and shallow depth negatives; real local
Git annotated/lightweight/missing/unmerged tag and shallow-history controls.
No tag push, remote release, credentials or provider traffic. Preserve source and
receipt, obtain independent review, then combine with reviewed GSC changes for one
exact owner aggregate and genuine PR gate. PSI/preflight stay separate open work.
