# Google Discover — a separate surface with a separate gate

Discover is not a Search ranking with a different template. It has its own
ranking pass (`algorithm-updates.md` records the 2026-02-05 Discover core
update), its own eligibility gate, and a card that will not render at all if two
tags are absent. A site can rank well and be structurally ineligible for
Discover, and nothing in a Search-shaped audit says so.

## Contents

- [Evidence standing, stated up front](#evidence-standing-stated-up-front)
- [The two tags without which there is no card](#the-two-tags-without-which-there-is-no-card)
- [Image requirements](#image-requirements)
- [The two metatags that halt the pipeline entirely](#the-two-metatags-that-halt-the-pipeline-entirely)
- [Freshness](#freshness)
- [The audit, in order](#the-audit-in-order)
- [What not to promise](#what-not-to-promise)


Audit it as its own track. The checks below are cheap — they are metatags and
image dimensions — and the failure mode is binary, which is rare enough in this
work to be worth spending ten minutes on.

## Evidence standing, stated up front

Two different tiers are mixed in here and the difference matters when you write
the report:

- **CONFIRMED** — Google's own documentation: `max-image-preview:large` is
  required for a large image in the feed, images should be at least **1200px**
  wide, and generic images (a logo, a stock placeholder) are called out as a
  problem. Verified against
  [Get on Discover](https://developers.google.com/search/docs/appearance/google-discover)
  on 2026-08-06.
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

## The two tags without which there is no card

```html
<meta name="robots" content="max-image-preview:large">   <!-- CONFIRMED -->
<meta property="og:image" content="https://example.com/hero.jpg">
<meta property="og:title" content="The title as it should appear on the card">
```

Without `max-image-preview:large`, Google is not permitted to render the large
image — the card degrades or does not appear. Without an image, there is no card
to degrade. These two are the whole gate, and both are one line.

Recommended alongside them:

```html
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
| Minimum width for the large card | **1200px** | CONFIRMED |
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

# 2. the gate
curl -s "$URL" | grep -iE 'max-image-preview|og:image|og:title'

# 3. the image actually resolves, anonymously, and is wide enough
IMG=$(curl -s "$URL" | grep -oP '(?<=og:image" content=")[^"]+')
curl -sI "$IMG" | head -1                       # 200, not 403
curl -s "$IMG" | file -                         # dimensions, format

# 4. freshness — is anything being published at all
curl -s "$URL" | grep -oE 'datePublished"[^,]+|article:published_time[^>]+'
```

Findings route into the report like any other: gate failures are CONFIRMED
blockers, the SDK-derived items are FIELD and belong in the pilot column of the
change plan, not in the blocker list.

## What not to promise

Discover traffic is volatile by design and it is not a keyword surface — there
is no query to rank for, no position to track, and week-to-week swings of a
large factor are normal for sites that are working correctly. A plan that
projects Discover traffic like organic search is projecting something that does
not behave like organic search. Fix eligibility, publish, and report the
distribution rather than a number.
