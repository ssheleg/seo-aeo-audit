# The bundled scripts — invocation, limits and traps

Moved out of `SKILL.md` when its body was 12% over the 5000-token cap. Every
script here is stdlib-only. Paths are written against `$SKILL_DIR`, which
`SKILL.md` resolves once before the first command — without it none of them
run.

## Contents

- [gsc_pull.py](#gsc_pullpy) — Search Console: queries, pages, cannibalization, the CTR curve
- [page_audit.py](#page_auditpy) — per-page mechanical evidence for tracks A, B, C, F
- [url_inspection.py](#url_inspectionpy) — the index's own answers, so a finding is CONFIRMED
- [sitemap_audit.py](#sitemap_auditpy) — declared URLs clustered into template families
- [psi_pull.py](#psi_pullpy) — field and lab, kept apart on purpose

## gsc_pull.py

`scripts/gsc_pull.py` (stdlib-only, local ADC auth) pulls the half of the picture
no crawl can see: which queries a property actually surfaces for, at what position,
and whether a drop is a *cliff that held* rather than a decline. Run it before
rating any finding by impact — a large impression count at position 50 is not an
opportunity, and only the position split shows that.

It also derives what a raw export leaves to hand-work: **cannibalization**
(several URLs competing for one query, with the incumbent named), a **CTR curve
built from this property's own rows** — never an industry table, which
[references/measurement.md](measurement.md) J6 forbids — the pages
falling materially below that curve, and the **branded / non-branded split**.
The split needs `--brand-terms`; without them it reports itself unavailable
rather than guessing, because a guess there misstates the one metric track F
leans on.

```bash
python3 "$SKILL_DIR/scripts/gsc_pull.py" --list
python3 "$SKILL_DIR/scripts/gsc_pull.py" --site sc-domain:example.com --quota-project my-proj
python3 "$SKILL_DIR/scripts/gsc_pull.py" --site sc-domain:example.com --brand-terms "acme,acme app" --format json
```

Both formats print all of it, including the split reporting itself unavailable — the
text format used to compute four of these and print none of them, so an agent that
ran the documented command saw no cannibalization section and had nothing to
distinguish "none found" from "never shown". Two limits travel in the output rather
than in this file: the cliff detector only fires on a collapse of ~90% or more that
held for two weeks, and the query set is capped at the API row limit with no
pagination, which drops the long tail the beyond-30 band is made of.

## page_audit.py

`scripts/page_audit.py` (stdlib-only, no network required in `--file` mode)
collects the per-page mechanical evidence for tracks A, B, C and F — canonical
traps, robots directives, heading and schema inventory, and the answer-engine
**read-budget estimate**. Paths below are relative to this skill's own directory;
run it on a representative URL per template, not on a single page.

```bash
python3 "$SKILL_DIR/scripts/page_audit.py" --url https://example.com/pricing --format markdown
python3 "$SKILL_DIR/scripts/page_audit.py" --file ./saved.html --base-url https://example.com/pricing
python3 "$SKILL_DIR/scripts/page_audit.py" --url-list urls.txt --format json > audit.json
```

`--format json` emits an **array**, one object per page, even for a single URL —
index it as `data[0]`, not `data`.

Its schema inventory reads **server-rendered HTML only**. Where a CMS injects
JSON-LD with JavaScript, an empty inventory is not evidence of absent markup —
non-negotiable #8, and the script says so in every report. A response cut off by
`--max-bytes` says so too, and drops every count-based finding rather than
publishing a fragment as a measurement.

**Every finding a bundled script emits carries an evidence tier as well as a
severity**, and only the tier enters the triage formula below. Severity is how loud
a finding is; the tier is what backs it. The mapping is declared in
`FINDING_TIERS` in `scripts/page_audit.py` and the validator fails if a finding is
added without one — before that, the scripts emitted severity alone and the number
the plan is ordered by had to be invented per finding.

## url_inspection.py

`scripts/url_inspection.py` asks the index instead of inferring from a fetch:
the Google-selected canonical against the declared one, coverage state, robots
verdict, last crawl. These are the engine's own answers, so a finding built on
them is `CONFIRMED` rather than an inference — which is what
[references/evidence-tiers.md](evidence-tiers.md) has always required
and nothing here could previously collect. Quota is **2000/day and 600/minute per
property**: sample a representative URL per template plus the specific pages a
finding is about, exactly as with `page_audit.py`.

```bash
python3 "$SKILL_DIR/scripts/url_inspection.py" --site sc-domain:example.com --urls https://example.com/pricing
python3 "$SKILL_DIR/scripts/url_inspection.py" --site sc-domain:example.com --urls-file urls.txt --format json
```

## sitemap_audit.py

`scripts/sitemap_audit.py` gives the *published* half of the step-1 count above —
declared URLs clustered into the template families the site actually ships,
derived from its own URLs. Pair it with the GSC Pages report for
declared-vs-indexed per template. It does **not** detect orphans: a sitemap holds
no link graph, so that needs a crawl.

## psi_pull.py

`scripts/psi_pull.py` returns field (CrUX) and lab (Lighthouse) separately and
refuses to let one stand for the other. The field percentiles are the verdict;
the lab run explains a failure you have already observed. Where CrUX has no data
for a URL, that is reported as absent — not as a pass.

```bash
python3 "$SKILL_DIR/scripts/sitemap_audit.py" --url https://example.com/sitemap.xml
python3 "$SKILL_DIR/scripts/psi_pull.py" --url https://example.com/pricing --strategy mobile
```

