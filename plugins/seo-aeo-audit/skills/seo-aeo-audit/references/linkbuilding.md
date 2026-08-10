# Link-building extraction — targets, keywords, anchors

Produce a brief and a CSV a link-building contractor can work from, for any
site, without inventing a single number.

This is a **deliverable for someone else to execute**, which changes the
evidence bar rather than relaxing it. An auditor who overstates a finding wastes
their own time. A brief that overstates one spends a client's budget on a page
that cannot rank.

## The non-negotiable: never blend measured with assumed

**One column decides how much every row is worth: `source`.** Measured rows and
candidate rows live in the same file and must never be confused for each other.

| `source` | Meaning | Volume columns |
|---|---|---|
| `gsc-current` | Search Console served this page for this query in the window | real numbers |
| `gsc-historic-<window>` | Measured, but from an earlier window — a page's proven ceiling, not its current state | real numbers, window named |
| `product-candidate` | Derived from what the site sells. Nobody has confirmed anyone searches it | **blank — never zero, never estimated** |

Blank, not zero. A `0` reads as "measured, no volume"; blank reads as
"unmeasured", which is the truth. If a spreadsheet sorts candidates to the
bottom because their volume cell is empty, that is the correct behavior.

Say in the brief, in the partner's own words, that candidate rows need volume
validation in a keyword tool before budget touches them. That sentence is the
difference between a brief and a wish list.

## Mode A — Search Console reachable

Preferred. Everything is measured.

1. Pull, for the last 90 days and one earlier comparison window:
   `["query","page"]`, plus `["page"]` and `["query"]` alone. Use
   `scripts/gsc_pull.py`, or any client — the shape matters, not the tool.
   **The bundled script pulls one window.** It takes `--days` for the recent window
   and a daily series for the trend; it does not pull a query×page set for an earlier
   comparison window, so the `gsc-historic-<window>` rows come from a second run with
   a different `--days`, or from any client that accepts a date range. Say which
   window each historic row came from — that is what the label is for.
2. **Split the query set by position before ranking anything.** This is the
   step that decides the whole brief:
   - **position ≤ 20** — already competitive. Small volume, high CTR. Links
     here convert into clicks fastest.
   - **position 21–30** — striking distance. Where links move the needle most.
   - **position > 30** — impressions without rank. Often the biggest raw numbers
     in the account and worth the least: `scripts/gsc_pull.py` prints the position
     split first for exactly this reason, and SKILL.md step 2 makes it a
     precondition of rating any finding by impact. (This claim lives there, not in
     `myths.md` — an earlier version of this line pointed at a myth row that does
     not exist.)
3. Pick targets by `clicks × position potential`, never by impressions alone.
4. For each target, take its top queries by impressions, filtered to
   **≥5 impressions OR position ≤ 20**, capped around 25 per target. Uncapped
   long tail drowns the deliverable; a contractor will not read 1,000 rows.
5. Where a page ranked far better in an earlier window, include those rows as
   `gsc-historic-<window>` and say plainly what changed. A page that once held
   position 3 is a different proposition from one that never has.

**Watch for:** the reporting lag (~2 days — querying up to today returns a
partial tail that reads as a drop); scraper noise in the query set (`-site:`
operators, quoted strings, raw URLs — filter them out); and branded-vs-generic
splits inside one page's query set, which usually tell opposite stories.

## Mode B — no Search Console

Still produces a real deliverable, from the site itself. Nothing here is a guess
about the market; it is a description of the product, and it is labelled as
such.

1. **Read what the site actually sells.** Pricing page, product constants,
   feature pages, the checkout. Write down the product's *own* words — those are
   the seed terms, and they beat invented synonyms because the page can actually
   satisfy them.
2. **Find the products with no search surface.** A product the site sells but has
   no page for, or has a page nobody links to, is where candidate keywords are
   worth most: no incumbent has bothered either.
3. **Take competitors from the site's own comparison page**, not from your
   assumptions. If it names three rivals, those three are grounded; a fourth you
   thought of is not.
4. **Mine the site's own machine-readable assets** — `openapi.json`, a pricing
   feed, `llms.txt`, a sitemap's URL shapes. They enumerate the product surface
   more honestly than the marketing copy.
5. Emit every one of these as `product-candidate` with empty volume columns.

Mode B also runs **alongside** Mode A, for products Search Console cannot see
because the site has never ranked for them at all. That gap is invisible to GSC
by construction, and it is often where the differentiated product lives.

## Choosing targets — the ordering that survives contact

1. **The head/brand cluster**, if it has volume and no rank. Usually the largest
   single opportunity and the one most responsive to off-site authority. Check
   first whether the brand name is *contested* — a name shared with an
   established incumbent turns this into a multi-quarter fight, and the brief
   must say so rather than promise movement.
2. **Assets that earn links rather than need them.** API documentation,
   published statistics, original research, free tools. Developers and writers
   link to these unprompted; everything else needs outreach. If the site has
   one, it is the best target it owns regardless of its current position.
3. **Comparison and alternatives pages.** High intent, and the anchor text
   writes itself.
4. **Striking-distance money pages**, from step 2 of Mode A.
5. **Differentiated products with no category competitor** — candidate keywords,
   validate first, but a category nobody contests is cheap to enter.

## What to exclude, explicitly

A brief that only says what to do gets budget spent on the rest. Name the
exclusions:

- **Pages already inside the top 5.** Protect, do not spend.
- **`noindex` pages** — auth, account, checkout. Verify rather than assume.
- **Pages whose canonical points elsewhere.** A link there passes through at
  best; localized duplicates are the common case.
- **Queries that rank on page one already and have no linkable audience.**
  Third-party brand terms are the classic trap: real clicks, page-one positions,
  and nobody on the open web will ever link to "<vendor> sign up". They need
  on-page work, not outreach — and they are often a large share of current
  clicks, so the brief must protect them while excluding them.
- **Any page whose product cannot be delivered.** If inventory, coverage or
  availability makes a page unable to convert, ranking it buys nothing. Say so
  and let the client decide; do not quietly include it.

## Anchor discipline

- Mostly **branded and naked-URL**. Exact-match anchors on a contested term are
  the fastest way to look manipulative.
- Vary within a target: brand, brand + category, category alone, naked URL,
  in-sentence phrases.
- Give anchors **per target, not per keyword** — a contractor picks from a set;
  a 1:1 keyword→anchor map produces an unnatural profile.
- Never instruct paid link networks, PBNs or bulk directory placement. The donor
  and velocity signatures are in `references/threats-and-defense.md` I6 (network
  footprints, the anchor bands, the disavow triggers); `references/myths.md` owns the
  adjacent refusal — disavowing on a third-party toxicity score. A site that has just
  cleaned its on-site signals should not acquire off-site ones that undo it.

**Sponsorship, said honestly.** Sponsoring a local organization is ordinary
marketing, the coverage is genuinely local, and sponsor pages survive for years
because volunteer-run sites rarely audit them — which is exactly why they get
pitched as a link tactic. Hold the distinction in the brief: a sponsorship the
business would fund anyway is marketing, and a sponsorship bought for the link is
a **paid link**, which needs qualifying (`rel="sponsored"`) whatever the invoice
says. Recommend it as community presence with a link that may or may not pass
equity; never as a per-link price, never as a volume program, and never with a
visibility multiplier attached — the figures circulating for that come from an
unnamed survey and did not survive a source check, so they are not in this file.

## CSV contract

One row per target × keyword. Columns, in this order:

```
priority,target_url,keyword,keyword_type,intent,source,
impressions,clicks,position,why_this_target,anchor_variants
```

- `priority` — `P1`, `P2`, … Grouping, so the contractor can work top-down.
- `keyword_type` — `brand-head`, `product-*`, `competitor`, `geo`,
  `commercial-content`, `trust-asset`. Lets them sort by campaign type.
- `intent` — `navigational` / `informational` / `commercial` / `transactional`.
- `source` — per the table at the top. **The most important column in the file.**
- `impressions`, `clicks`, `position` — blank for `product-candidate`.
- `why_this_target` — one sentence, repeated per row of that target. Redundant
  in a database, essential in a spreadsheet someone filters.
- `anchor_variants` — pipe-separated, per target.

Ship the CSV next to a markdown brief that carries the reasoning, the
exclusions, and a **measurable baseline** (clicks, impressions, CTR, and the
position split) so the engagement can be judged later against something.

## Verification before handing it over

- Every `target_url` returns `200` and is not `noindex` — check, do not assume.
- No target's canonical points at a different URL.
- No row mixes a candidate keyword with a measured volume.
- The exclusions section names the pages a contractor would otherwise reach for.
- Every claim of past performance names its window.
