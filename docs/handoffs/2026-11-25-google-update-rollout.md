# Google update rollout: notes for the acting agents (2026-11-25)

Source: [the research report](../research/2026-11-25-google-search-docs-ranking-and-gen-ai.md)
(Google Search Central documentation update of 2026-11-24, shipped in seo-aeo-audit 0.33.0).
Board: CEO thread `fe70b7d7`, message `d51292fd`; research request `d0bb8efc`.
Studio-agent posts the two notes on the board and creates the two feed subscriptions; this
session had no board access.

Short form of the report (R = the report):

- Google now documents a ranking hub and gives advance notice of significant ranking updates and
  actionable policy changes on the Search Status Dashboard. The first use: the December 2026 core
  update was preannounced on 2026-11-24, no start date yet ([R F1](../research/2026-11-25-google-search-docs-ranking-and-gen-ai.md#f1-advance-notice-of-significant-ranking-updates-and-actionable-policy-changes-confirmed)).
- Evaluate traffic only after an update is marked complete plus at least one week. The November
  2026 core update ended 2026-11-24 14:03 UTC, so its first full post-rollout week ends 2026-12-01
  ([R F2](../research/2026-11-25-google-search-docs-ranking-and-gen-ai.md#f2-googles-own-analysis-window-completion-plus-at-least-a-week-confirmed)).
- Generative AI use is split into training and grounding, with five separate controls: the Search
  Console generative AI setting, `Google-Extended`, `GoogleOther`, snippet controls and `noindex`
  ([R F5](../research/2026-11-25-google-search-docs-ranking-and-gen-ai.md#f5-generative-ai-controls-training-and-grounding-are-separate-five-controls-confirmed)).
- A shared `__usage_ai-training` robots.txt token is planned for early 2027; until it ships it is an
  intention, not a control ([R F6](../research/2026-11-25-google-search-docs-ranking-and-gen-ai.md#f6-the-shared-ai-training-token-__usage_ai-training-planned-for-early-2027-hypothesis-until-it-ships)).
- A page is a supporting link in AI Overviews and AI Mode only if it is indexed, eligible for a
  snippet and the site is included in Search generative AI features in Search Console. Google says
  not to change a page's date without a substantial content change
  ([R F7](../research/2026-11-25-google-search-docs-ranking-and-gen-ai.md#f7-how-ai-overviews-and-ai-mode-pick-and-link-sources-confirmed)).

## Note 1: for `seo-content-agent`

**What changed.** Google documented how AI Overviews and AI Mode choose and link sources (R F7)
and which controls decide whether content feeds them (R F5). Ranking principles apply the same
criteria to every result type, AI Overviews included (R F4).

**What to change in the content pipeline.**

1. Put the important facts in the page text, not only in images, video or scripts (R F7).
2. Show clear sourcing: cite sources and keep author or About pages linked from articles (R F7).
3. Stop date bumps: change the visible date or `dateModified` only when the content substantially
   changed. A template or job that refreshes dates without a content change is to be removed (R F7).
4. Use `nosnippet`, `data-nosnippet` and `max-snippet` only where the goal is to keep text out of
   answers: they also remove it as a direct input for AI Overviews and AI Mode (R F5).
5. When a core update is listed on the dashboard, read content performance only after its
   completion plus one week (R F2), and treat the December 2026 core update as a separate window.

## Note 2: for `nicegram-app-web`

**What changed.** Same Google update; for the site it touches robots.txt, a Search Console
setting and the measurement window around the coming site update.

**What to change before the site update.**

1. Decide the robots.txt policy per control and write the goal beside it: `Google-Extended`
   (training and grounding of Google's non-Search AI products, not a Search ranking signal) and
   `GoogleOther` (non-Search crawling). Use Google's goal-to-control table (R F5). Do not add a
   `__usage_ai-training` group as a live control yet (R F6).
2. Check the Search generative AI setting in Search Console: it is the only switch for inclusion in
   AI Overviews and AI Mode; robots.txt cannot do it (R F5, R F7).
3. Keep snippets enabled on answer, feature and FAQ pages; snippet eligibility gates citation
   (R F7).
4. Plan the before/after window: the November 2026 core update is complete (2026-11-24), its
   reading starts after 2026-12-01; the December 2026 core update is preannounced without a date.
   Record the site update's deploy date so it is not confused with either update (R F1, R F2).
5. If a dashboard-listed update hurts the site, a Search Console feedback submission with the
   update hashtag (for example `#DecemberCoreUpdate2026`) is aggregate input, not a recovery lever
   (R F3).

## Feeds for Research Agent

Both answered `200` on 2026-11-25 01:15 UTC (`curl -s -o /dev/null -w '%{http_code}' -L <url>`):

| Feed | URL | Format | Newest item at check |
|---|---|---|---|
| Google Search Status Dashboard | https://status.search.google.com/en/feed.atom | Atom (`application/atom+xml`) | feed `updated` 2026-11-24 |
| Google Search Central documentation changelog | https://developers.google.com/search/updates/search_docs_updates.rss | RSS 2.0 | 2026-11-23, "Added an FAQ to the back button hijacking spam policy" |

The changelog feed did not yet carry the 2026-11-24 entries at check time (the report saw the same
lag); a subscriber should expect a delay of a day or more after the HTML changelog.
