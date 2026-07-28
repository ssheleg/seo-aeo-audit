# Track H — experience, satisfaction signals, CRO × SEO

## H1. What the systems actually record

Leaked internals describe a click-quality system (`QualityNavboostCrapsCrapsData`)
splitting clicks into `goodClicks`, `badClicks` and **`lastLongestClicks`** —
the case where the user spends longer on your result than on any other in the
session and does not return to search. NavBoost reranks on a **13-month** history
of these signals.

Two structural details change how you audit:

- `patternLevel` shows the signals aggregate at **URL, directory and subdomain**
  level → "topical neighborhoods". A weak section drags its neighbors; a strong
  section lifts them. Architecture concentrates or dilutes satisfaction.
- `onsiteProminence` uses high-satisfaction pages as seeds in a traffic-flow
  simulation of internal authority → pages that satisfy users become internal
  authority hubs.

All of it is sliced by country, language and device: each context is a separate
portfolio.

CTR itself is contextual, not absolute: leaked fields include
`click_age_probability` (expected clicks given document age versus what users
expect for that query), `relative_click_order` and device/layout-specific
impression weights. 5% CTR at position 3 can be over- or under-performing
depending on query, position, device and document age — **there is no universal
CTR benchmark**. Build a site-specific CTR curve from your own GSC data instead.

That curve is perishable. Practitioners reading the same leaked parameters report
that a core update appears to reset the click model's expectation baseline across
the corpus, and that SERP-layout changes (Local Service Ads, ad-block prominence)
force their own recalibration — so rebuild the curve after each documented update
and each layout change, and put the build date on it (HYPOTHESIS — practitioner
observation on leaked fields, 2026-05; no engine confirmation, no sample stated).

Two caveats an honest audit states: `unicornClicks` is a **child-account** marker
(COPPA/GDPR-K isolation), not a premium-user signal — nothing to optimize there;
and Brave's Web Discovery Project (which feeds Claude) gates every engagement
event behind >1s of active time and throttles to one increment per second, so
synthetic click activity does not inflate it.

## H2. Formats that earn the last long click

Seven page types that resolve the session instead of sending the user back:

1. Ultimate guides that absorb the follow-up questions.
2. Comparison pages where the decision happens on your page.
3. Tools and calculators (task completion, no email wall before the result).
4. Case studies with concrete numbers ("position 11 → 3 in 90 days on a keyword
   worth £8,000/month").
5. Original research the user cannot get elsewhere.
6. Step-by-step processes that keep the user engaged through completion.
7. FAQ hubs that answer the next logical question in the same visit.

Nine page-level tactics: answer the main question above the fold; pre-empt the
next step; delete unsupported claims; place the CTA at the point of task
completion; cut load time (drop-off spikes around 4s); map the title tag hard to
the content (over-promising is the biggest `badClick` risk); optimize mobile
scroll depth; use FAQ/HowTo markup to pre-qualify the click in the SERP; keep it
evergreen (stale pages dilute the 13-month window).

Avoid: context-free news, opinion without evidence, empty category pages, basic
listicles that spawn ten new questions, and hub pages that link without
answering.

**Usefulness is judged on function, not only on text.** Google has evaluated
where content sits on the page since the 2012 Page Layout algorithm (CONFIRMED —
documented). The 2026 practitioner extension of that — "visual semantics" — is
that whole verticals carry their value in comparison modules, tables and
interactive layouts rather than prose: flight booking, credit aggregation and
marketplace listings cannot be assessed from the running text at all, and a
helpful page is one that lets the user complete the task, decide, or act
(HYPOTHESIS — Koray Tuğberk Gübür, 2026-07-15; mechanism plausible, no controlled
evidence). Audit each money template for whether the decision can be made **on
the page**, not merely read about — that is the same property as the last long
click, expressed as layout.

## H3. CRO and SEO are the same work

Measured across 47 pages over 90 days: bounce −31%, dwell +187%, average position
+6.2, organic +218%, conversion +134%. Individual levers:

| Change | Effect |
|---|---|
| Load 4.2s → 1.3s | bounce 67% → 41%, CVR +93%, +8 positions after 6 weeks (FIELD — speed here moved satisfaction signals too; page experience on its own is a tiebreaker between near-equivalent candidates, see ranking-model.md) |
| Mobile UX rework (tap targets, form simplification, thumb zone) | mobile CVR ×2 |
| Layout restructure (scannable blocks, multiple CTAs above the fold) | CVR +127%, scroll depth +45%, bounce −23% |
| Contextual internal links to related content/cases/FAQ | pages per session 1.4 → 3.2 |
| Trust signals (reviews, security badges, guarantees) | CVR +89%, dwell +2.1 min |

Landing-page specifics with field evidence:

- **One-second test**: translate the page into an unfamiliar language and show it
  to five people. If the visual alone does not communicate the category, the page
  leaks traffic before anyone reads a word.
- Aggregated across ~130,000 split tests, generic stock photography above the
  fold cost ~19% conversion; real product screenshots, uniformed staff and
  branded vehicles beat lifestyle imagery.
- **Mobile-only failures hide behind a passing desktop page**: text below legible
  size, tap targets crowded together, horizontal scroll, interstitial popups,
  fixed elements covering the navigation. Mobile-first indexing means the mobile
  rendering is the one indexed (CONFIRMED — documented), so test every money
  template on a real device profile rather than a narrowed desktop window (FIELD
  — recurring agency-audit finding, 2026-06).
- Video above the fold cannibalizes attention: session benchmark is 30–60s while
  the average explainer view is ~16s. Move it below the fold or behind a "See how
  it works" secondary button, use a static screenshot with a play button, no
  autoplay, always show the duration.

## H4. Core Web Vitals — triage order that actually works

1. **TTFB** — the page is blank until then; fix with caching (query, page, code).
2. **Clear the LCP path** of everything less important than the LCP element:
   icons, third-party scripts, below-fold images, secondary fonts.
3. `fetchpriority="high"` on the LCP element.
4. Defer non-critical JS until after `load`.
5. Only then image formats and responsive images (`sizes="auto"` +
   `loading="lazy"` replaces hand-written `sizes`; width/height still required;
   the LCP hero must **not** be lazy-loaded).

Inventory what blocks the render before optimizing anything. One documented
template profile: 12 CSS files, 8 JS libraries (half of them unused), fonts
queued ahead of the content, and synchronous analytics. Deferring the
non-critical set took one SaaS site from 3.8s to 1.2s with organic up 23% (FIELD
— single site, 2026-06; no control group, so treat the 23% as the size of a bet,
not a forecast).

INP traps: modal patterns that add a scroll-lock class to `<html>` plus a blurred
overlay push style recalculation into the click handler and add tens of
milliseconds every open/close — use the native `<dialog>` element with
`::backdrop`.

Fonts: 900KB of preloaded fonts widened the P90 TTFB→FCP gap from ~840ms on fast
connections to ~1,488ms on slow ones, correlating with ~18% fewer pageviews per
session — measure with real-user data, not lab scores.

Page weight is a real SEO lever on listings: cutting a category grid from 48 to
36 products was positive at 85% confidence, via LCP rather than content depth —
worth testing per site, not copying.

Use **field data**: `cruxvis.withgoogle.com` gives real Chrome data per origin,
including the mobile/desktop/tablet form-factor split, for any competitor with
enough Chrome traffic (Chrome-only, so no iOS Safari). Compare parity between
your desktop and mobile experience and against the sites you actually compete
with, before presenting anything.

Regional reality check: identical technical work produced 25% → 97% good URLs in
one country and zero movement in another, because CDN proximity, server location
and device quality cap what optimization can achieve. Do not promise uniform CWV
targets across markets, and never let CWV work outrank an indexing fix.

## Evidence to capture for track H

- Per template: CrUX field values (LCP/INP/CLS) by form factor, lab trace of the
  LCP path, TTFB.
- GSC query-level CTR versus your own site curve (not an industry table), with
  the date the curve was built and the update or layout change that invalidates
  it.
- Per money template: can the user decide or complete the task on the page, or
  only read about it.
- Behavioral metrics per template (bounce, dwell, pages/session, scroll depth),
  and the return-to-SERP rate if you can approximate it.
- Before/after for any CRO change, with the 60–90 day ranking window stated.
