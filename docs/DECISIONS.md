# Decision register

One entry per decision that is expensive to reverse. Newest last.

## 2026-08-04 — Seed the documentation registers

**Decision.** Create `docs/DOCMAP.md` (single-home table + propagation matrix)
and this register, and gate them with `scripts/check-docs.sh`.

**Why.** Two drifts had already shipped: `cursor/rules/*.mdc` carried five
non-negotiables where SKILL.md carried seven, and the reference count was stated
as nineteen in CONTRIBUTING while the validator enforced twenty-one. Both are the
same failure — a fact with more than one home and nothing reconciling them. This
is the register's first entry, which is also the record of its own seeding.

## 2026-08-04 — Instruments declare their own blind spots (non-negotiable #8)

**Decision.** Add an eighth non-negotiable, and enforce it with script checks
rather than prose: `page_audit.py` ships a JS-blindness caveat in every report,
`measurement.md` carries the GA4 consent-mode conditions, and `validate.py` fails
if either disappears.

**Why.** Non-negotiables #1 and #7 govern what the auditor writes. They cannot
see an instrument that blends or omits *before* the auditor looks. The class had
occurred twice — a static parser reporting JS-injected schema as absent, and GA4
returning modelled and observed behaviour inside one number — which is the bar
for promoting a rule from a doctrine line to a script check.

**Alternative rejected.** A ninth reference file about tool limitations. It would
have been read once and would not have failed anything.

## 2026-08-04 — Report absence as absence, never as zero or a substitute

**Decision.** Where CrUX has no data, `psi_pull.py` reports it as absent and
emits no verdict; `sitemap_audit.py` refuses orphan detection outright;
`gsc_pull.py` reports the branded split as unavailable without `--brand-terms`;
`url_inspection.py` produces no findings for a URL it could not inspect.

**Why.** Every one of these has a plausible-looking wrong version that a
competitor tool ships: a lab score standing in for field data, "orphan
candidates" inferred from path shape, a guessed brand classification. Each would
manufacture a finding out of missing data, which is the defect this skill exists
to prevent. The refusals are held by tests because the useful-looking wrong
feature is the one that gets added back later.
