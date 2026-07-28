# The ranking model — what the engine is actually doing

Read this before writing any recommendation that starts with "Google wants…".
It sets the vocabulary the rest of the tracks use.

## Systems, signals, factors — and why the argument is a trap

- **Systems** are the machine-learning layers applied to refine results
  (helpful-content system, RankBrain, BERT, MUM, freshness, spam systems).
- **Signals** feed those systems (keywords on the page, links, page experience,
  location, device).
- Google's own line: "the main difference is just language." Documentation moves
  items between the two lists without changing behaviour — when page experience
  was removed from the *systems* page, Google clarified it was still a signal used
  by other systems.

Audit consequence: never build a finding on a documentation reshuffle. Build it
on an observation about this site.

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
   about. Entities extend this: engines resolve topics, synonyms and misspellings
   through the entity graph, not string matching.
   - Helpful-content behaviour (2022 onwards): stay on your main topic,
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

## Personalisation and locality sit on top of everything

Results differ by history, location and device. "Best coffee shop" is a local
pack; "London Zoo" skews to research formats on desktop and to tickets and
directions on mobile. Personal context now extends into AI answers
(algorithm-updates.md, Personal Intelligence). Any ranking claim without a stated
market, device and (where relevant) user context is unfalsifiable — record those
with every rank observation.

## How to use this in the report

- Frame findings as "this query class rewards X, this page delivers Y".
- Do not promise that fixing a signal moves a ranking; state the mechanism and
  the evidence tier.
- When a stakeholder asks about a factor from a listicle, answer with the model
  above and the site's own evidence, then move to the plan.
