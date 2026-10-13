# R30 SEO board and release contract receipt

Status: focused source checks passed; independent review and combined owner gate
pending. Base e8aa59eaec85c2bceed4a2680c2e9892b53ab7ed. This changes tests and
internal board syntax, not package version or executable skill payload.

[The packet](../plans/2026-10-13-r30-owner-gates.md) names source provenance and
bounded acceptance. The copied board parser is byte-identical to reviewed
agent-sync 8fd93be's helper. The release parser is byte-identical to cb4f9ce's
helper, with its existing documented layout bounds. The release fixture matches
make-skill 2785f6c's residue-ledger variant.

## Observed source defects and changes

The original status dictionary overwrote duplicate declarations and did not check
width. The canonical parser also found an existing blank-separated B-33/B-34/B-36
block lacking a header, plus even-backslash pipe syntax in a command cell. Added
a repeated explicit header and odd Markdown escaping; the rendered command's
literal backslash/pipe content is preserved. No board ID or task status changed.
The status reader uses the shared tokenizer and excludes fenced example rows.
Unreadable board checks now yield named failures through the document scan and
board guard instead of aborting before that guard on invalid UTF-8.

The existing release runtime guard already refuses unreachable tags. However,
removing its ancestry command or making the checkout shallow both still passed
SEO's real structural validator before the new helper. The two dedicated controls
first exited 1 because those planted defects were not refused. No workflow job,
event or publication action changed.

## Observed checks and limits

`python3 -B test/owner_board_contract.py` passed **28 controls**, including actual
validator duplicate/width negatives, escaped positive, fenced status shadow,
missing/UTF-8 board diagnostics and ancestry/shallow removal negatives. One owned
clone was created and removed on success. Earlier owned failed fixtures were
removed after replay; foreign residue was untouched.

`python3 -B test/audit_regressions/r30_owner_release.py` passed **27 controls**:
bounded workflow mutations plus actual shell extracted from the workflow against
local Git, with only gh's default-branch response replaced by a task-owned stub.
Annotated historical/current tags pass; lightweight/missing/unmerged tags refuse;
shallow history is detected without treating it as proof of non-ancestry. The
fixture uses the owner's residue ledger and removed its owned tree.

Structural checks protect the supported ancestry/full-history contract. Annotation
protection is exercised by the aggregate fixture's extraction and execution of
the real annotation step. Neither layer proves arbitrary shell/YAML semantics,
job ordering, hosted release acceptance or publication. The full owner gate has
not yet been run for this source; it follows independent review and GSC composition.

Structural validation and the combined `test/test_output_contracts.py` also exited
0, covering 115 shared, 127 sitemap, 73 agent and 28 board controls on this branch.
