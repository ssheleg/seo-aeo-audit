# Google Discover — a separate surface with three separate checks

Discover is not a Search ranking with a different template. It has its own
ranking pass (`algorithm-updates.md` records the 2026-02-05 Discover core
update) and its own presentation mechanics — and they are **three checks of
three different strengths**, not one gate. A recommendation reported as a gate
is how an audit invents blockers: the previous revision of this file called two
metatags "the whole gate", and a page without them would have been written up
as confirmed-ineligible for a surface Google documents as automatic.

## Contents

- [Evidence standing, stated up front](#evidence-standing-stated-up-front)
- [Check 1 — eligibility](#check-1--eligibility)
- [Check 2 — large-preview permission](#check-2--large-preview-permission)
- [Check 3 — image selection, a recommendation](#check-3--image-selection-a-recommendation)
- [Card assembly signals (FIELD)](#card-assembly-signals-field)
- [The two metatags that halt the pipeline entirely](#the-two-metatags-that-halt-the-pipeline-entirely)
- [Freshness](#freshness)
- [The audit, in order](#the-audit-in-order)
- [What not to promise](#what-not-to-promise)


Audit it as its own track. The checks below are cheap — metatags and image
dimensions — but their verdicts carry different weights, and the report must
say which weight each finding carries.

## Evidence standing, stated up front

Two different tiers are mixed in here and the difference matters when you write
the report:

- **CONFIRMED** — Google's own documentation, and every CONFIRMED rule below
  links the exact page that supports it: eligibility is automatic for indexed
  content within the content policies; `max-image-preview:large` (or AMP) is
  the documented *permission* for a large preview; images of at least
  **1200px**, the article's own rather than a logo or stock placeholder, are
  the documented *recommendation* for the large card. Verified against
  [Get on Discover](https://developers.google.com/search/docs/appearance/google-discover)
  on 2026-08-06 — three statements of three strengths, and the report keeps
  them apart.
- **FIELD** — the parsing order, freshness buckets and internal flag names below
  come from one practitioner's reverse-engineering of the Google app's SDK
  (Metehan Yesilyurt, February 2026), not from documentation and not from a
  multi-site study. They are internally consistent and match observed behaviour,
  and they are still one source with no control. **Report them as FIELD**: pilot
  on a cohort, do not sell them as a fix, and do not let a client rebuild a
  publishing workflow on them.

The distinction is not pedantry. "Google says images must be 1200px" and "one
researcher believes the SDK falls back to `twitter:image:src` fourth" carry very
different weight in a plan someone funds.

## Check 1 — eligibility

**CONFIRMED, and it is automatic.** Google's documentation
([Get on Discover](https://developers.google.com/search/docs/appearance/google-discover),
read 2026-08-06): content is eligible for Discover when it is **indexed and
meets Discover's content policies**. There is no registration, no required
metatag, and no tag whose absence makes a page ineligible. Two consequences for
the report:

- **no page is written up as "confirmed ineligible" for missing `og:` tags** —
  that verdict has no documented basis, and issuing it turns a recommendation
  into a gate;
- what CAN block indexing (noindex, robots, quality) blocks Discover too, but
  that is track A's finding, cited to track A's sources — not a Discover gate.

## Check 2 — large-preview permission

**CONFIRMED.** For the large image card, Google must be *permitted* to show a
large preview: `max-image-preview:large` in the robots meta (documented in
[Get on Discover](https://developers.google.com/search/docs/appearance/google-discover)
and the [robots meta reference](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag),
read 2026-08-06) — **or the page is served as AMP**, which is the documented
alternative. Absence is a **presentation limitation**: the card falls back to a
small preview or may not be featured large. It is not ineligibility, and the
finding says "large preview not permitted", never "not eligible".

```html
<meta name="robots" content="max-image-preview:large">   <!-- CONFIRMED: permission -->
```

## Check 3 — image selection, a recommendation

**CONFIRMED as a recommendation.** The same documentation *recommends* images
at least **1200px** wide and the article's own imagery over a logo or stock
placeholder, to improve how (and whether) the large card is selected. A
recommendation it stays: a smaller image is a "less likely to be featured
large" finding in the improvement column, never a blocker row.

## Card assembly signals (FIELD)

Useful alongside the three checks, with FIELD standing only:

```html
<meta property="og:image" content="https://example.com/hero.jpg">
<meta property="og:title" content="The title as it should appear on the card">
<meta property="og:site_name" content="Publication name">
<meta property="og:locale" content="en_US">
<meta property="og:image:secure_url" content="https://example.com/hero.jpg">
<meta property="article:content_tier" content="free">   <!-- free | metered | locked -->
```

**Set the primary tags explicitly rather than relying on a fallback.** *(FIELD)*
The reported fallback order is:

| Signal | Reported chain |
|---|---|
| Title | `og:title` → `twitter:title` → `<title>` |
| Image | `og:image` → `og:image:secure_url` → `twitter:image:src` → `image` → `twitter:image` |
| Publisher | `og:site_name` → `author` |
| Language | `og:locale` → JSON-LD `inLanguage` → `"en"` |
| Paywall | `article:content_tier` + JSON-LD `isAccessibleForFree` |

A chain is a thing to not depend on. If the language fallback really does end at
a hardcoded `"en"`, a non-English site that omits `og:locale` is mislabelled with
no error anywhere.

## Image requirements

| Requirement | Value | Tier |
|---|---|---|
| Recommended width for the large card | **1200px** | CONFIRMED (a recommendation, not a gate) |
| Aspect ratio | 16:9 for the hero card | CONFIRMED |
| Generic images (logo, stock placeholder) | called out as a problem — use the article's own image | CONFIRMED |
| Below 1200px | degrades to a thumbnail card, materially lower engagement | FIELD |
| WebP | supported | FIELD |
| Broken image URLs | tracked and counted against the page | FIELD |

Serve the image from a CDN and check that the URL in `og:image` actually
resolves for an anonymous request. A signed or referrer-restricted image URL
fetches fine in your browser and returns 403 to Google, which is invisible in
every on-page check that only reads the DOM.

## The two metatags that halt the pipeline entirely

```html
<meta name="nopagereadaloud" content="true">
<meta name="notranslate" content="true">
<!-- and its equivalent: <html translate="no"> -->
```

*(FIELD)* Either is reported to stop the content entering Discover at all — not
rank it lower, stop it. Both are injected silently by CMS plugins and
translation tooling, which is what makes this worth a mechanical grep rather
than a spot check: nobody adds `notranslate` on purpose and then forgets.

Check `<html translate="no">` as well as the meta form. They are the same signal
and only one of them is greppable by the obvious pattern.

## Freshness

*(FIELD)* Reported decay buckets: 1–7 days carries the highest weight, 8–14
medium, 15–30 low, and past 30 days a continuous decay measured in hours.

The actionable part survives even if the exact buckets do not: **the Discover
window is short and front-loaded.** Promotion effort spent in week one is worth
more than the same effort in week three, and refreshing a page meaningfully
(not a date bump) resets the signal. Content classified as evergreen is reported
to be treated differently, which is consistent with feeds that surface older
explainers.

## The audit, in order

Cheapest first — the first two are the ones that produce a binary verdict.

```bash
# 1. the blocking tags — a grep, sitewide
curl -s "$URL" | grep -iE 'nopagereadaloud|notranslate|<html[^>]*translate="no"'

# 2. large-preview permission (CONFIRMED) and card-assembly signals (FIELD)
curl -s "$URL" | grep -iE 'max-image-preview|og:image|og:title'

# 3. the image actually resolves, anonymously, and is wide enough
IMG=$(curl -s "$URL" | grep -oP '(?<=og:image" content=")[^"]+')
curl -sI "$IMG" | head -1                       # 200, not 403
curl -s "$IMG" | file -                         # dimensions, format

# 4. freshness — is anything being published at all
curl -s "$URL" | grep -oE 'datePublished"[^,]+|article:published_time[^>]+'
```

Findings route into the report by their check's strength: a blocked pipeline
(the two halt metatags) and an indexing blocker are blocker rows; a missing
large-preview permission is a CONFIRMED **presentation** finding; a small or
generic image is a CONFIRMED **recommendation**; and the SDK-derived items are
FIELD and belong in the pilot column of the change plan, not in the blocker
list. Nothing in this file confirms *ineligibility* — that word needs an
indexing or policy finding from track A.

## What not to promise

Discover traffic is volatile by design and it is not a keyword surface — there
is no query to rank for, no position to track, and week-to-week swings of a
large factor are normal for sites that are working correctly. A plan that
projects Discover traffic like organic search is projecting something that does
not behave like organic search. Fix eligibility, publish, and report the
distribution rather than a number.
