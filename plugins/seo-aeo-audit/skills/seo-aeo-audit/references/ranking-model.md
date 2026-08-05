# The ranking model — what the engine is actually doing

Read this before writing any recommendation that starts with "Google wants…".
It sets the vocabulary the rest of the tracks use.

Tiering: everything here is either engine-documented or a documented industry
consensus — treat it as `CONFIRMED` for vocabulary and mechanism, and `STUDY` or
lower for any number attached to it. It never licenses a claim about *your* site
without an observation from *your* site.

## Systems, signals, factors — and why the argument is a trap

- **Systems** are the machine-learning layers applied to refine results
  (helpful-content system, RankBrain, BERT, MUM, freshness, spam systems).
- **Signals** feed those systems (keywords on the page, links, page experience,
  location, device).
- Google's own line: "the main difference is just language." Documentation moves
  items between the two lists without changing behavior — when page experience
  was removed from the *systems* page, Google clarified it was still a signal used
  by other systems.

- **Not every signal feeds every system.** Signals are selected and weighted per
  system and per query — even PageRank, the most famous of them, is not used in
  Local Search at all. "Is X a signal" and "does X apply to this SERP" are two
  different questions, and only the second one belongs in a report.

Audit consequence: never build a finding on a documentation reshuffle. Build it
on an observation about this site.

## How a change actually ships

Google's own description of the launch pipeline (Search Off the Record,
2026-05): an experimental version is built, compared **side by side** against the
current production version on random queries, evaluated by human raters, checked
statistically — the experiment has to beat the baseline — and then taken to a
launch review. Two consequences for an audit:

- Raters sit in the *evaluation* loop, never in the ranking loop. That is the
  mechanical reason E-E-A-T is a specification and not a dial (below).
- What the industry names as "an update" is the far end of that pipeline, and
  several launches can land inside one window. A causal story that only works if
  exactly one thing changed is not a finding (algorithm-updates.md).

## The stack: retrieval, scoring, re-ranking

Vocabulary, so that a finding can name the layer it belongs to:

1. **Retrieval** selects candidates. Nothing outside the candidate pool can be
   ranked, summarized or cited — this is where an unindexed or unfetchable page
   dies.
2. **Primary scoring** ranks the candidates on relevance and quality.
3. **Re-ranking** adjusts the scored list: click-quality systems (NavBoost, and
   Glue for the non-web blocks) sit **on top of** the primary ranker rather than
   replacing it — described under oath in the DOJ testimony, and the reason
   satisfaction signals amplify an existing position instead of creating one. The
   mechanics live in experience-signals.md.
4. **Serving-layer filters** decide what is finally shown (duplicate grouping,
   feature selection, per-vertical suppression).

Named components from a 2026 enumeration of ~3.7M internal Google URL paths
(RESONEO, 2026-06 — no page bodies were opened, so this is inference from path
names: `HYPOTHESIS`, and only useful as vocabulary): `Ascorer` as the primary
information-retrieval scorer, `Twiddlers` re-ranking under a `SuperRoot`
controller, and an experiment/kill-switch control plane (`Mendel`, with `Finch`
on the Chrome side) — which is why a rollout can be flipped mid-window.

Three things that corpus makes concrete, and that change how you talk to a
client:

- **Demotion and removal are separate machinery** — a demotion list and a spam
  removal list appear side by side. That matches the observed behavior that
  spam-filter losses do not recover at the next core update while quality
  reassessments do (algorithm-updates.md). Never promise one recovery path for
  both.
- **Some decisions are hand-maintained files** in specific verticals (a
  controversial-query blacklist with dated revisions). Not every SERP anomaly has
  an algorithmic explanation; sometimes the honest finding is "we cannot explain
  this from the site side".
- **AI answers ride the same stack.** Fan-out → ordinary retrieval and ranking →
  a candidate set compressed to roughly a hundred documents that reach the
  generation stage (aeo-geo.md F1). Visibility is decided at retrieval; the
  citation is a downstream artefact of it.

Query class is part of the same picture: the leaked parameter set describes
queries being sorted into a small number of classes, and the class maps to which
SERP features appear and where the answer has to sit — a short-fact query wants
the answer in the first line, a research query does not (`HYPOTHESIS`;
classification tooling in intent-and-content.md).

## The "200 ranking factors" myth

There is no published list. The number traces to a single 2009 conference remark
and stuck as PR shorthand. Modern search runs hundreds-to-thousands of features
plus ML overlays; for scale, the 2023 Yandex leak exposed roughly **690**
factors. Weighting is **query-dependent**: Google's own framing is meaning,
relevance, quality, usability and context, "the weight applied to each factor
varies depending on the nature of your query". YMYL, transactional e-commerce and
local are ranked differently from one another.

So: "is X a ranking factor" is the wrong question. The useful question is "for
*this* query class, on *this* site, what is holding the page back?"

## The three that carry the most weight

1. **Content quality and relevance.** Ranking starts by understanding the query,
   then matching it to page content. Keywords are not obsolete — they are the
   cornerstone the ML layers sit on; a page must state unambiguously what it is
   about. The failure mode is not using keywords, it is *scaffolding* a page on a
   keyword list instead of on a user's task (intent-and-content.md E2b). Entities extend this: engines resolve topics, synonyms and misspellings
   through the entity graph, not string matching.
   - Helpful-content behavior (2022 onwards): stay on your main topic,
     demonstrate first-hand experience, do not staple unrelated topics onto one
     site. Content that leaves visitors satisfied is rewarded; content that misses
     the visitor's expectation is not.
   - RankBrain (2015) connects words to concepts and handles never-seen queries;
     BERT (2018) reads word combinations and stop words as meaning; MUM (2021) is
     multimodal and surfaces mainly in Lens-style experiences.
   - Freshness is **query-dependent** (introduced 2011, ~35% of searches at the
     time): critical for news, weather, prices; near-irrelevant for evergreen
     topics. Combine with the relative-age rule in intent-and-content.md E5.
2. **Page experience.** HTTPS, page speed, mobile friendliness, Core Web Vitals.
   Google's framing: core ranking systems "look to reward content that provides a
   good page experience". It rarely decides a SERP on its own — it separates
   near-equivalent candidates. Treat it as a tiebreaker and a conversion lever,
   not as a growth strategy (details in experience-signals.md).
3. **Links — internal and external.** Historically the citation model of
   PageRank; still how pages get discovered and how importance is distributed.
   Public messaging is deliberately deflationary ("it's absolutely possible to
   rank without links", "no universal top 3") because links are the most
   manipulated signal, but quality and relevance of individual links still move
   rankings, and a page with no inbound or internal links is hard to crawl,
   index and rank at all. Internal linking also builds the topic cluster
   (architecture-and-equity.md).

## "Content" includes layout and function, not only text

The helpful-content framing is that the page lets the user *complete the task
behind the query* — and for whole verticals (flights, credit products,
aggregators, comparison-driven commerce) the substance of the page lives in
comparison modules, tables and interactive blocks, not in prose. The documented
ancestor is the Page Layout algorithm; the modern reading — "visual semantics",
layout and functionality as evaluated parts of the document — is a practitioner
framework built on top of documented pieces (`HYPOTHESIS`).

Audit consequence: read a template by asking whether the task can be finished on
it, not by counting words. A text-only judgement of "quality" will pass a page
that answers nothing and fail a page that answers everything in a table
(intent-and-content.md, experience-signals.md).

Controlled evidence exists for the *position* half of this, and it is modest:
split tests moving substance out of tabs and above the fold, and removing a
commercial module from a template holding a non-commercial intent, both moved
organic traffic (experiments.md). That supports "where an element sits is read",
not "structure the page for the retriever" — chunk boundaries are the engine's
choice, and myths.md holds that line. Google's spam policy on **misleading
functionality** points the same way from the other side: a page promising a
calculator or a comparison has to deliver one, which is a rule about the
function being real, not about its markup.

One counterweight to carry into any AEO plan built on layout: in a practitioner sample of
B2B prompts across two answer engines, product pages barely appeared — listings
and comparison pages took nearly all of it (FIELD, 2026-08; the source's own
sample count did not survive a primary check, so it is not quoted here). If retrieval filters by page *type* before layout
gets a vote, template work earns its return in classic ranking long before it
shows up in citations. Sequence it accordingly, and do not sell a template
rebuild as an AI-citation fix.

## E-E-A-T: important, not a factor

Experience, Expertise, Authoritativeness, Trustworthiness comes from the Search
Quality Rater Guidelines. Raters do not rank pages; they evaluate them so the
systems can be trained and measured. So E-E-A-T is **a specification of what
quality means**, not a dial. It matters most in YMYL categories, and the "first
E" — demonstrated first-hand experience — is the part AI cannot replicate:
original photography, detailed walkthroughs, credible author bios, transparent
process.

Practical audit questions: who wrote this, what is their evidence, is the
evidence visible on the page, and would a rater reading the guidelines agree?

**Authority may accrue to people, not only domains.** A Google patent
(*Determining Topic Authority*) describes an authority signature accumulated per
**author entity** — authorship share of a passage × the topic's weight in the
document, summed across documents. Its named inventor worked on Drive and
AppSheet rather than Search, so this is a documented architecture pattern, not a
confirmed web-search factor (`HYPOTHESIS`; the operational version and the
consistency checks live in entity-and-brand.md). It is worth carrying because it
reframes the question: not "does this page have an author box" but "does the same
named person cover the same topic consistently, across this site and off it, in a
form a machine can bind together" — which is exactly what the publisher and
creator Search profiles now surface (algorithm-updates.md).

## Personalization and locality sit on top of everything

Results differ by history, location and device. "Best coffee shop" is a local
pack; "London Zoo" skews to research formats on desktop and to tickets and
directions on mobile. Personal context now extends into AI answers
(algorithm-updates.md, Personal Intelligence). Any ranking claim without a stated
market, device and (where relevant) user context is unfalsifiable — record those
with every rank observation.

**Other engines are the same shape, differently weighted.** Yandex works from the
same raw material — on-page content, links, metadata, mobile friendliness, SERP
interaction — and also applies ML layers of its own, but weights backlinks and
click behavior differently, and its own leaked factor set is architecture, not
weights. So a Yandex leak tells you *what kind of thing* is measured and never
what to do on a Google-facing site (`HYPOTHESIS` for any transfer). The same
discipline applies to Bing, which documents far more mechanical detail than
Google does: use it, then verify it on this site (evidence-tiers.md rule 4).

## How to use this in the report

- Frame findings as "this query class rewards X, this page delivers Y".
- Do not promise that fixing a signal moves a ranking; state the mechanism and
  the evidence tier.
- When a stakeholder asks about a factor from a listicle, answer with the model
  above and the site's own evidence, then move to the plan.
