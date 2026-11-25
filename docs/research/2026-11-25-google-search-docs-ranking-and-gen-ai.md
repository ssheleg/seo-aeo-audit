report: google-search-docs-ranking-and-gen-ai
date: 2026-11-25
project: seo-aeo-audit
kind: research
status: final
sources: primary pages read 2026-11-25 00:30 to 00:45 UTC (list below)
board: request d0bb8efc-3b12-4dbb-b9e4-9141bfb344b1 (owner's order of 2026-11-24 22:54 UTC, relayed by the Fabric CEO)

# Google Search documentation update of 2026-11-24: ranking hub and generative AI controls

## What happened

On 2026-11-24 Google added five pages to the Search Central documentation, in two changelog
entries, and preannounced the December 2026 core update on the Search Status Dashboard the
same day. Every page below was fetched directly; each carries "Last updated 2026-11-24 UTC".

| # | Page | URL | Changelog entry |
|---|---|---|---|
| 1 | Google Search ranking hub | https://developers.google.com/search/docs/ranking | "Added a ranking section to the Search Central documentation" |
| 2 | Our principles for ranking results | https://developers.google.com/search/docs/ranking/principles-for-ranking-results | same |
| 3 | How to stay informed on Google Search ranking updates | https://developers.google.com/search/docs/ranking/stay-informed | same |
| 4 | Submit feedback about ranking changes in Google Search | https://developers.google.com/search/docs/ranking/submit-feedback | same |
| 5 | Control how your content is used for generative AI at Google | https://developers.google.com/search/docs/fundamentals/gen-ai-controls | "Added documentation about generative AI controls and attribution" |
| 6 | Attribution and factuality in Search generative AI features | https://developers.google.com/search/docs/fundamentals/gen-ai-attribution-factuality | same |

The owner's note counted five pages (three on ranking, two on generative AI); the ranking
section is a hub page plus three child pages, so six URLs. Changelog:
https://developers.google.com/search/updates (entry "November 24"). The `.md.txt` mirrors of the
new pages answered 404 at read time and the cached copy of the changelog still ended at
2026-11-23; the HTML pages are the source read.

Related primary sources read in the same pass:

- Search Status Dashboard incident "December 2026 core update",
  https://status.search.google.com/incidents/AXrqxXXdtSjj3672ux7X, entry 24 Nov 2026 07:03 PST.
- Search Status Dashboard feed, https://status.search.google.com/incidents.json: November 2026
  core update `begin 2026-11-10T18:06:00+00:00`, `end 2026-11-24T14:03:00+00:00`.
- Search Central blog, "Supporting a shared AI training control for websites", John Mueller,
  2026-10-30, https://developers.google.com/search/blog/2026/10/ai-training-control (the page the
  gen-ai-controls page links for `__usage_ai-training`).
- UK CMA, "Google Search: fair ranking conduct requirement",
  https://www.gov.uk/find-digital-markets-measures/google-search-fair-ranking-conduct-requirement
  (the page the stay-informed page links).

Secondary, used only where marked: Matt G. Southern, Search Engine Journal, "Google Documents
Advance Notice For Significant Ranking Updates", 2026-11-24 or 2026-11-25,
https://www.searchenginejournal.com/google-documents-advance-notice-for-significant-ranking-updates/598773/.

## Findings, each with its quote

### F1. Advance notice of significant ranking updates and actionable policy changes (`CONFIRMED`)

Page 3: "When an update introduces actionable policy requirements or may cause broad ranking
shifts for site owners, we provide notice based on the type of change. Additionally, for changes
where UK users may experience a significant ranking shift, we provide advance notice to site
owners in accordance with CMA's fair ranking conduct requirements for Google."

Two classes get notice: "Actionable policy changes" (content policies, technical guidelines,
eligibility criteria) and "Significant ranking changes: Broad algorithmic updates (such as core
updates)". Where: "We publish pre-announcements, rollout start dates, and completion notices on
the Search Status Dashboard", with an Atom / RSS feed; also the Search Central blog and the
documentation changelog, both with RSS.

The first use: the dashboard entry of 24 Nov 2026 07:03 PST "Preannounced the December 2026 core
update, which focuses on multiple improvements to how our systems understand and rank relevant
content (including for longer and more complex questions), as well as improving personalized
results for people who have personalization turned on. ... This update is scheduled to be released
in December 2026." No start date is given.

The notice periods themselves are not on Google's page ("our advance notice timelines" is
promised in the intro, no figure follows). SEJ reports, from the CMA's decision PDF, at least 30
business days for changes publishers could act on and at least 15 for other significant changes,
effective 2026-12-17. That is `FIELD` here: the CMA PDF was downloaded but this machine had no
PDF text tool, so the figures were not read at the primary.

**Audit consequence.** A decline analysis now has a third date per core update: the
pre-announcement, before the rollout start and end. The skill's rule that shifts can begin 7 to 10
days before an announcement (algorithm-updates.md, step 2 of "How to use the timeline") is about
unannounced crawl-pattern changes and still stands; the pre-announcement is a new, earlier anchor
for planning, not evidence of movement.

### F2. Google's own analysis window: completion plus at least a week (`CONFIRMED`)

Page 3: "Wait until an update is marked complete on the Search Status Dashboard (plus at least a
week of post-rollout data) before evaluating traffic changes in Search Console". The skill's
protocol already freezes 28 days either side; the new rule is the floor for when an "after"
reading may start. For the November 2026 core update (complete 2026-11-24 14:03 UTC) the first
full post-rollout week ends 2026-12-01, and the December core update may begin inside the
following window, so the two must be split.

### F3. Feedback channel with update hashtags, and a UK indexing appeal from 2026-12-17 (`CONFIRMED`)

Page 4: verified owners submit feedback in Search Console "by clicking the Submit Feedback button.
In the feedback box, include the specific actionable policy change or significant ranking change, in
hashtag format (for example, if it was a November core update 2026, include
#NovemberCoreUpdate2026 in the submission)." Recommended content: performance snapshot, queries
and locale, affected and competing URLs, impact, context, and "UK market impact". "Submitting
feedback doesn't result in manual ranking adjustments for individual URLs."

New appeal route: "UK CMA indexing appeal: If your site provides web content, goods, or services
to users in the United Kingdom and your site as a whole has been manually excluded from Google's
search index, you will be able to submit an appeal ... starting on December 17, 2026." EU DMA
Article 6(12) appeals are listed beside it.

**Audit consequence.** A change plan for a site hit by a dashboard-listed update can include a
feedback submission as an action, framed as aggregate input, never as a recovery lever.

### F4. Ranking principles: one utility criterion for every result type (`CONFIRMED`)

Page 2: "web page listings and other results like AI Overviews, carousels, images, and videos are
evaluated using the same criteria. No result receives preferential treatment." "We don't make manual
adjustments to alter search rankings other than to comply with legal obligations or apply our
clearly defined Content Policies for Search." Changes are tested for usefulness and evaluated
against the Search Quality Rater Guidelines.

**Audit consequence.** Policy-level statement, no new lever. It supports the skill's standing
position that classic ranking is the prerequisite for AI Overviews and AI Mode (aeo-geo.md F4).

### F5. Generative AI controls: training and grounding are separate, five controls (`CONFIRMED`)

Page 5 defines two uses of crawled content: "AI model training" and "Grounding" ("Looking up
relevant, fresh information from the Google Search index when answering a prompt (also known as
retrieval-augmented generation, or RAG)"), and says "Google provides the following controls so that
you can manage foundation model training, non-Search grounding, and Search generative AI grounding
independently":

| Control | What it governs | Where |
|---|---|---|
| Search generative AI control | grounding and display (including links) in AI Overviews, AI Mode, Discover generative features; "doesn't affect generative AI model training, and it isn't used as a ranking or inclusion signal for other parts of Google Search" | Search Console settings |
| `Google-Extended` | training and grounding of "certain commercially available generative AI products and services"; "not used as a ranking signal in Search and doesn't affect a site's inclusion in Search" | robots.txt |
| `GoogleOther` | Google's generic crawler for non-Search uses such as R&D crawls, "without affecting Search" | robots.txt |
| robots meta, `data-nosnippet`, `X-Robots-Tag` | previews; "nosnippet and max-snippet also give you the option to prevent your content from being used as a direct input for AI Overviews and AI Mode" | page HTML or HTTP header |
| `noindex` | out of Search including generative AI features | page HTML or HTTP header |

The page also gives a goal-to-control table (for example "Stay on Google Search (including AI
Overviews and AI Mode), but limit AI model training and grounding on other Google generative AI
products: Disallow Google-Extended in robots.txt").

**Audit consequence.** The skill's crawler table (agent-readiness.md K2a) put `Google-Extended`
under "Model grounding" only and named "Gemini / Vertex AI grounding". Google now documents it as
training **and** grounding for non-Search products. The row is corrected. The Search generative AI
control is the one switch for AI Overviews and AI Mode; a robots.txt rule cannot do it.

### F6. The shared AI-training token `__usage_ai-training`, planned for early 2027 (`HYPOTHESIS` until it ships)

Page 5: "Google intends to support the shared machine-readable training preference signal (with
user-agent: __usage_ai-training) in early 2027." The link goes to the 2026-10-30 blog post: a
"policy token" in robots.txt based on the IETF AIPREF working group; "When a website uses this policy
token to opt out of training in its robots.txt file (and Google-Extended is not explicitly
specified), Google plans to interpret that as if the publisher had disallowed Google-Extended."
"Existing company-specific controls will continue to function alongside this new joint signal."
The post says 2027 without a month; the documentation says early 2027. No other provider's support
is documented in these sources.

**Audit consequence.** From the day it ships, a `User-agent: __usage_ai-training` group with a
disallow is a cross-provider training opt-out, and for Google it reads as a Google-Extended
disallow **unless Google-Extended is named explicitly**, so a robots.txt that disallows the shared
token and allows Google-Extended keeps Gemini grounding. Until it ships the group is an announced
intention: report it, never price it. `agent_surface.py` does not classify the token yet; that is
a backlog row (B-41).

### F7. How AI Overviews and AI Mode pick and link sources (`CONFIRMED`)

Page 6: "a customized Gemini model integrated directly with Google's core web ranking, information
retrieval, and quality systems"; snippets of ranked results are the basis; related searches
("query fan-out"); "Grounding and corroboration"; links chosen by balancing "relevance and quality
signals from Search ranking with a clear layout ... and a diverse set of helpful sources".
Eligibility for a supporting link: "Only pages that are indexed and eligible to be shown in Search
with a snippet, meeting the technical requirements, can be shown as supporting links. Your site must
also be included in Search generative AI features in Search Console." Practice notes: important
information in text, clear sourcing and author or About pages, "Avoid changing a page's date unless
the content has substantially changed", and the Generative AI performance report for monitoring.
Misattribution routes: the Feedback link under the answer; edit and recrawl one's own page; the
Removals tool (about 6 months, all of Search); syndication partners `noindex`; DMCA for copying.

**Audit consequence.** Three checks become `CONFIRMED`: snippet eligibility gates AI citation
(`nosnippet` blocks it), the Search Console inclusion setting gates it, and query fan-out is
Google's documented mechanism. A date bumped without a substantive change is now named by Google
as a practice to avoid; the skill treats it as a finding on freshness-signalling templates.

## What changed in the skill (0.33.0)

- `references/algorithm-updates.md`: November 2026 core update row (2026-11-10 to 2026-11-24, from
  the feed), December 2026 core update preannounced row, five platform rows dated 2026-11-24 (F1,
  F3, F5, F6, F7), the pre-announcement and the one-week floor in "Protocol when a new update is
  announced", the Search Status Dashboard RSS feed in the refresh protocol; stamps moved to
  2026-11-25 / 2026-11-24.
- `references/agent-readiness.md` K2a: `Google-Extended` row corrected to training and grounding
  of non-Search products; `GoogleOther` and the planned `__usage_ai-training` token added; the
  contested-study paragraph now cites the 2026-11-24 page.
- `references/aeo-geo.md` F3 bullets: the five-control matrix and the supporting-link eligibility
  rule, with the date-bump check.
- `README.md` stamp follows the single home.

## Hand-offs this research implies (not done in this repository)

1. **seo-content-agent**: take F5 to F7 into its content pipeline: important facts in text,
   sourcing and author pages, no date bump without a substantive change, snippet controls only
   where intended.
2. **nicegram-app-web**: before the site update, decide the robots.txt policy per control (F5
   table), check the Search Console generative AI setting, keep snippets on answer pages, and
   plan the before/after window around the December 2026 core update (F1, F2).
3. **Watcher**: subscribe the Search Status Dashboard RSS
   (https://status.search.google.com/en/feed.atom, the feed both the dashboard and the
   stay-informed page link) and the documentation changelog RSS
   (https://developers.google.com/search/updates/search_docs_updates.rss) in the observer or
   Research Agent, so a pre-announcement lands as a dated row within a day.
4. **Owner's personal skills**: the request asks for them where they touch SEO; this machine holds
   no inventory of them, so that part stays open on the board.
