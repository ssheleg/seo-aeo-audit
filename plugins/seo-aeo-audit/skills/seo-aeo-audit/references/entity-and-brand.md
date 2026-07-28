# Track G — entity signals, brand consensus, ghost citations

Models do not "see" a brand, they compute it. Every passage becomes a vector;
together they form a cluster whose centroid *is* your brand to the system.
Retrieval matches queries against centroids **before** ranking, so a distant or
blurred centroid keeps your pages out of the candidate pool entirely.

## G1. Cross-surface consistency (the cheapest win in this track)

Open, in one sitting: homepage H1 and top-menu services (the reference), then
LinkedIn, G2, Capterra, Clutch, Crunchbase, YouTube, X and Instagram bios. Most
companies carry 8–12 third-party profiles nobody has looked at in years.

If four surfaces say four different things, the models have no stable category
for you: they average the descriptions or take the loudest attribute, and
citation visibility suffers regardless of link authority.

Audit output: a table of surface → current description → matches reference?
→ owner → fix. Then re-check quarterly; manual synchronization of a dozen
profiles does not survive contact with reality, so put it on a schedule.

Audit the reference before you sync anything to it. The homepage is frequently
the *stalest* asset in the set — profiles get updated at launch, the homepage
gets rewritten on a redesign cycle — so record current state everywhere first,
then decide which description is correct (FIELD, practitioner method, 2026-05-06).

Consistency also plausibly reaches the **training** corpus, not just retrieval.
Dataset papers describe curated pipelines, not raw crawls: FineWeb documents
filtering and deduplication of Common Crawl snapshots, DataComp-LM treats corpus
assembly as an experiment, and the LLaMA paper lists weighted sources (Common
Crawl, C4, GitHub, Wikipedia, books, arXiv, Stack Exchange). Deduplication
collapses the same boilerplate across hundreds of URLs, so a brand described
identically on the site, Wikidata, Wikipedia, Crunchbase, G2 and press survives
that collapse as one consistent statement. Labs do not publish how live search
engines rank and select sources, so this is inference from dataset papers, not a
measured effect (HYPOTHESIS, 2026-06). Never sell it as a mechanism; the
retrieval-layer arguments above stand on their own.

## G2. Ghost citations — cited but not recommended

Analysis of 541,213 LLM answers across 20 brands and 6 platforms shows a
post-hoc pattern: the model picks brand names from parametric memory **first**,
then retrieves sources to support the answer. Citations are a bibliography, not
the brainstorm.

- Brand named in the answer → cited 53.1% of the time.
- Brand not named → 10.6%. A 5× gap that source-first retrieval could not produce.
- Ghost-citation rate varies by vertical (>20pp spread in hospitality/travel;
  0.3% in industrial services; <2% in financial services and HR tech — categories
  where a few brands are synonymous with the category).
- Worst damage at the awareness stage, where the buyer has heard of neither you
  nor your competitors, and your content shapes the conversation without your
  name in it.

Three layers of fix:

1. **Grammar.** Make the brand the subject of the extractable insight: "At
   [Brand], our approach to compliance starts with…" instead of "five approaches
   to compliance training". Extracting the insight without the name becomes
   impossible.
2. **Entity graph.** Wikidata entry, Wikipedia presence where it is legitimately
   earned, `Organization` schema with `sameAs`, one canonical brand name
   everywhere, author markup binding named experts to the company, FAQ answers
   that contain the brand name. Small competitors with clean entity graphs beat
   large ones with messy graphs here.
3. **Third-party mentions in recommendation context** — analyst notes, press,
   review aggregators, partner pages. A canonical brand name in an H1 on a
   respected domain teaches the model that your name belongs in answers about the
   category.

Grammar layer, refined: put the **full canonical entity name in the first
sentence**, not just somewhere in the opening. Parsers weight the document head
heavily and truncate aggressively, so a name that arrives in paragraph three may
never be read at all. Strip marketing adjectives ("innovative", "world-class")
from that opening — they read as promotional noise and give the extractor
nothing to bind (FIELD, practitioner network-tab observation, 2026-06-30). The
extraction mechanics behind this live in aeo-geo.md F3; only the naming rule
belongs here. The same source pairs the technique with CSS that visually
relocates the block away from human readers — that is cloaking, it is out of
scope for any plan, and its detection belongs in threats-and-defense.md.

**Guardrail — mentions are not a currency to buy.** Google's spam policy now
covers manipulating generative answers, and Gary Illyes compared mention
manipulation to link buying at Search Central Live Sydney (CONFIRMED, engine
statement, 2026-05-29; timeline entry in algorithm-updates.md). Sanctions are
synced between classic Search and AIO/AI Mode, so a purchased-consensus footprint
costs both surfaces at once. Google also states that hunting "inaccurate
mentions" of your products is less useful than it looks (CONFIRMED, engine
statement, 2026-05) — audit mentions for *what the model concludes from them*,
not for a clean-up backlog. Everything in this track earns mentions; nothing in
it manufactures them.

Track **competitive ghost-citation rate** monthly, per platform and funnel stage.
Falling = entity work is landing. Rising = content spend is outrunning brand
spend.

## G3. Knowledge-graph plumbing

- `Organization` (or `LocalBusiness`) schema with `sameAs` pointing at the
  verified profiles; one canonical legal + trade name; consistent NAP.
- Multiple entity types: use an array (`"@type": ["Product","FinancialProduct"]`)
  — never two `@type` keys (duplicate-key error) — or `additionalType` for extra
  context, which can also point at external ontologies/Wikipedia entities where
  Schema.org lacks a type. Note `productontology.org` uses **http**.
- Author entities: Google's *Determining Topic Authority* patent computes an
  authority signature per **author** (authorship share × topic weight per
  document), accumulating across documents. Now that author profiles are
  resurfacing in Search, consistent named authorship per topic section is worth
  real editorial effort. Caveat: the inventor worked on Drive/AppSheet — treat as
  a documented architecture pattern, not a confirmed web-search factor.
- Wikidata is a lower-threshold entry point than Wikipedia and is trusted as a
  structured source, but entries are deleted without genuine external signals.
  Only pursue it alongside real corroboration (press, verified profiles,
  consistent NAP, genuine reviews) — never as a standalone trick.
- Wikidata, what it is actually worth: roughly *half* the pull of a full
  Wikipedia article, at a far lower moderation bar, because it is a structured
  repository rather than a public encyclopedia. It still moderates for
  significance — one practitioner's own entry was deleted within **24 hours** for
  insufficient external links. What makes an entry stick is triangulation with
  the other sources Google verifies against: Crunchbase, IMDb, verified LinkedIn
  and X profiles, genuine Trustpilot reviews, consistent NAP (FIELD, single
  practitioner account, 2026-06-16). The asymmetry that makes this a spam vector
  — paid Wikidata insertion at ~$30 against ~$850 for a managed Wikipedia attempt
  — is detection material: unsupported new entries in your category, with no
  press or link corroboration, are a competitor footprint. That analysis belongs
  in threats-and-defense.md, not in a plan.
- Brand pages (About, Trust, Legal) are the minimum viable entity definition.
  They carry little traffic and are load-bearing for entity resolution, so audit
  them for a canonical legal name, founding facts, locations and leadership
  rather than for keywords (FIELD, content-format ranking by defensibility,
  2026-05).
- **Capitalization is a named-entity signal.** Google tokenizes and runs NLP at
  index time, and capitalization separates the company "Apple" from the fruit
  "apple" as well as marking emphasis. Five years of controlled SearchPilot tests
  across a client base found meta-title capitalization tests **50% positive, 0%
  negative** — their most consistently successful test type, though the ideal
  pattern is not isolated yet and selective capitalization sends a cleaner signal
  than all-caps (STUDY, multi-site controlled tests, reported 2026-04). Practical
  read for this track: write the brand name in its canonical case everywhere and
  never lowercase it into ambiguity with a common noun.
- Entity pages with proper linked-data relations improved answer accuracy ~29% in
  one presented analysis, while schema alone gave no lift: the moat is the linked
  data layer, not the markup volume.
- `citemap.json` is circulating as a proposed standard that would extend entity
  depth past Schema.org with data provenance, trust level and mis-attribution
  protection. There is no published evidence that any engine reads it — the same
  evidence class as `llms.txt` (see myths.md), which is documented as ignored.
  Answer the question when a client raises it, never bill it as a lever
  (HYPOTHESIS, proposal-stage, 2026-04-27).

## G3b. Discovery is fragmented — audit where the audience actually is

Buyers now form an opinion before any query reaches your site: on TikTok, Reddit,
Quora, YouTube, Substack, Discord, in Meta AI inside WhatsApp/Facebook, in
Gemini, Google Lens, ChatGPT and Perplexity. Both humans and models read those
spaces to decide who you are and whether you can be trusted.

Audit questions, answered with evidence, not assumption:

- Which platforms does this audience use to research this category? (ask them,
  read support tickets, check referral and branded-search patterns)
- What do those spaces currently say about the brand — and who is saying it?
- Is the brand narrative consistent there, or is it being written by others?
- Which of those surfaces are **owned** (email list, Discord/Slack community,
  Substack) versus **rented** (subreddit, Facebook group, TikTok account)? Rented
  platforms can change the rules or disappear overnight; owned surfaces compound
  and survive algorithm changes on both search and social.

The practical cycle: participate on rented platforms to learn the audience and
build awareness, then move engaged people onto a surface you own. For B2B,
community management on UGC platforms doubles as LLM-training input — a thread
with multiple independent perspectives teaches a model more than a
brand-controlled page.

**Platform weight is rented too, and it is rewritten without notice.** Reddit
measured at roughly 40% of LLM citations (Semrush), and Reddit's share of ChatGPT
answers then fell from about 60% to 10% **in six weeks** after a single
retrieval-logic change; after the May 2026 core update and the June 2026 spam
update, Google demoted mass auto-translated Reddit content and AI Overviews
followed (STUDY + dated platform observations, 2026-05/2026-06). Audit
consequence: date every platform-share number you quote, never build a plan whose
payoff depends on one UGC platform holding its weight, and re-measure the mix per
engine each month (measurement.md). Depth of forum research is cheap — appending
`.json` to any Reddit thread URL returns the structured thread for analysis — but
threads skew toward a loud minority, so triangulate before treating a thread as
the category's opinion (FIELD, 2026-05).

Reddit has no surface E-E-A-T markers — no verified accounts, no author bios —
but thread engagement, comment depth and upvotes act as forensic proxies, and a
thread of 10–50 replies from practitioners, skeptics and edge cases carries more
distinct perspectives than any single polished post (FIELD, 2026-05). That is the
mechanism behind the community-management point above; it is not an argument for
seeding threads yourself.

Gen Z is Google's fastest-growing Search demographic and roughly 1 in 10 of their
searches starts with Google Lens, of which about 1 in 5 carries commercial
intent — visual and multimodal entry points belong in the audit for consumer
brands.

## G4. Reputation is now a retrieval input

Analysis of 5M ChatGPT conversations: once "review" enters the fan-out (hidden
behind "which X is better", "should I buy X"), the model leans on Reddit for
social proof and Trustpilot for ratings; Wikipedia's weight is falling.

Scope, so this does not read as a contradiction: it describes **commercial
evaluation prompts** — the ones that generate a review sub-query. On
general/informational queries Wikipedia is still one of the most-cited sources in
the citation corpus (aeo-geo.md F2). Both hold; the source mix is query-class
dependent, so establish which class your priority prompts fall into before
choosing where to invest. Reddit's own share is volatile per engine and per
retrieval change (benchmarks.md) — re-measure rather than inheriting last
quarter's mix.

Counter-intuitive finding: brands with **bad** ratings surface more often than
mediocre ones — the model highlights one strong option and contrasts it with weak
ones, so *average* is the worst position. There is nothing to say about you.

Audit steps:

1. For each attribute buyers care about (support, pricing, security, delivery),
   ask the engines and collect the **URLs they cite**. That short list — not your
   marketing site — writes the verdict.
2. Check those pages for staleness (a two-year-old security article can still be
   feeding concerns the company resolved months ago) and for coordinated attacks
   (e.g. 75% of negatives from single-review accounts is a footprint, not
   feedback — report it through the platform's process).
3. Treat the complaints the model repeats as **product findings**. Fixing the
   product and cleaning the cited sources are now the same task.
4. Reddit specifics: a comment recommending a client was quoted by ChatGPT
   **1h45m** after posting. Mentions without links count when they are specific,
   contextual and in a thread the model already trusts. Monitor brand mentions
   without links, and know that platform weight differs — Reddit is heavy in
   ChatGPT, light in Perplexity. Do not buy aged accounts: Reddit detects
   ownership transfer on seven independent signals and removes the buyer's whole
   footprint.
5. Compare ratings **across** platforms, not only against your own history. In
   the same 5M-conversation analysis, Revolut sat at 1.3/5 on Sitejabber against
   4.87 on Glassdoor with 75% of the negatives coming from single-review
   accounts. A wide divergence between two review surfaces for one brand is the
   cheapest coordinated-attack detector you have; the attack patterns themselves
   are catalogued in threats-and-defense.md (FIELD, 2026-07-13).

### Mention volume is not brand visibility — the cluster label decides

A viral political fight over junk food drove a brand's ChatGPT mentions **+2800%
in under 60 days**. The model absorbed the volume, ignored the negative context
of those first mentions, and bound the entity to a "junk-food scandal" semantic
cluster — after which it was systematically dropped from transactional and
recommendation prompts such as "best fast food". Raw mention volume never
overrode that categorization (FIELD, single-brand practitioner analysis,
2026-07-01).

Audit consequence: measure **mention volume and the semantic cluster the mentions
attach to as two separate metrics**. A dashboard reporting only "mentions up" can
be reporting a commercial collapse. Where a spike is already underway, the
legitimate response is publishing comparable factual data and earning coverage
that places the brand alongside neutral category peers — not suppressing
competitors' consensus, which is the manipulation route and belongs in
threats-and-defense.md.

Related, and worth knowing before you promise a sentiment fix: practitioners
report that models render roughly **~70% agreement across sources as flat fact**,
and anything below that as hedged "some say X, others say Y" — with reviews,
press and social feeding that count (HYPOTHESIS, community observation,
2026-07-17). Useful as a framing for why a contested brand reads as hedged; not
a number to build a target around.

### Where the verdict is actually hosted

- **Third-party opinion outweighs self-description.** Link building aimed at a
  Google Maps profile does not move it; the weight sits in what other people say
  in reviews (FIELD, 2026-07-01). The corollary tactic — engineering keyword-
  bearing reviews to weld a brand to a topic — is review manipulation, stays out
  of every plan, and is detection material for threats-and-defense.md.
- **Derive the off-page target list from the cited-source inventory, not from
  DR.** If the engines answer your category by citing aggregators, niche
  publishers and third-party tools, then those are the domains worth a digital-PR
  or contributed placement; a high-DR domain the models never cite buys nothing
  here (FIELD, practitioner consensus, 2026-07).
- **Platform transparency is changing what buyers see.** In Germany, Google
  Business Profile now publishes how many reviews the owner had removed **by
  legal process** (a count that excludes policy-violation removals, which are
  handled without owner involvement). Check whether your profile carries such a
  counter before advising any removal action (CONFIRMED, platform behavior,
  2026-06).
- **New surface to inventory:** Google announced one-tap connection of a Google
  Business Profile to Gemini, giving the assistant the business's reviews,
  customer questions and performance data (announced 2026-06-11, rollout
  "in the coming weeks"). Record whether it is connected and who owns that
  decision; do not connect a client property without explicit approval.
- **False claims about a brand in AI answers have a legal remedy.** A Munich
  court held Google directly liable for false statements in AI Overviews —
  reasoning that AI summaries are Google's own content, rewritten and weighted in
  its own words and structure, and therefore not protected like ordinary search
  results — and issued a temporary injunction for two publishers wrongly linked
  to fraud schemes, with Google ordered to pay 80% of costs (CONFIRMED, reported
  court ruling, 2026-06-10). Escalation paths and takedown mechanics live in
  threats-and-defense.md; what belongs in this track is capturing the verbatim
  false answer, dated, with the engine and prompt, as evidence.

## G5. Mention vs citation vs recommendation

Three different things — measure them separately:

- **Mention**: the model names the brand in the answer. This is what the buyer
  actually hears. In field data on 85 mid-market companies, when a brand is named
  it is in the top-3 in 63% of cases.
- **Citation**: the model links a source. It may link a parts catalogue while
  recommending Audi — citation-only scorecards mark visible brands invisible.
- **Recommendation**: the model tells the user to choose you. It rides on
  external signals (referring domains, brand mentions elsewhere in AI answers),
  not on self-praise: when a brand's own "best [category]" page was the cited
  source, the brand was excluded from the recommendation **69%** of the time.
- **Retrieval** is a fourth state, visible only in logs: the page enters the
  candidate set and the answer never links it. Report it separately where you can
  see it (measurement.md).

Being linked is not being recommended, and the gap is measurable. In the
9,886-answer experiment below, **43%** of answers that linked the new event's
promo page did not mention the event at all — the model used the page as a data
source and recommended a competitor from the same list — against **11%** for
product pages, a gap the authors attribute to accumulated trust rather than text
quality. Retrieved-but-uncited is worse still: **74%** of those answers ignored
the brand, which reads as retrieval mostly *reinforcing* the consensus the model
already holds rather than shifting the recommendation (STUDY, 9,886 answers
across ChatGPT/Gemini/Perplexity/Copilot, 2026-02-07 → 2026-05-31).

Audit consequence: a "we got cited" screenshot proves nothing on its own. Score
every recorded answer on the four states, and treat a page that is cited while
the brand goes unmentioned as a **trust** finding, not a content finding.

Self-promotional placement works only as a bridge from *unknown* to *mentioned*:
in a 9,886-answer experiment, a brand-new entity filled 72 previously empty
answer slots (82% citing the new pages), while an established tool got only 6% of
its new mentions from them. Narrow intent multiplies it (66.4% presence for "best
SEO conferences 2026" vs 15.8% for "best marketing conferences 2026"). Sanity
test before shipping any such page: **would this brand read as a natural
recommendation if a third party had written the page?**

## Evidence to capture for track G

- The consistency table (surface → description → verdict).
- The verbatim prompt-set answers per engine, dated, with accuracy/confidence/
  consistency scores.
- The cited-source inventory per buyer attribute, with staleness and sentiment
  notes — doubling as the target list for any off-page work in the plan.
- Ghost-citation rate per platform and stage, with the measurement method stated.
- Mention **volume** and the **semantic cluster** those mentions attach to, as
  two separate series, so a reputational spike is never read as growth.
- Per answer, the four states scored separately: mentioned / recommended / cited
  / retrieved-only.
- The knowledge-graph corroboration inventory: which of Wikidata, Wikipedia,
  Crunchbase, verified social profiles, NAP records and genuine review profiles
  actually exist and agree, with the date each was last verified.
- Cross-platform rating divergence per review surface, with the single-review-
  account share where the platform exposes it.
- Every platform-weight number you quote, carrying its date — those shares have
  moved by 50pp in six weeks.
