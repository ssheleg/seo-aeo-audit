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
- Entity pages with proper linked-data relations improved answer accuracy ~29% in
  one presented analysis, while schema alone gave no lift: the moat is the linked
  data layer, not the markup volume.

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

Gen Z is Google's fastest-growing Search demographic and roughly 1 in 10 of their
searches starts with Google Lens, of which about 1 in 5 carries commercial
intent — visual and multimodal entry points belong in the audit for consumer
brands.

## G4. Reputation is now a retrieval input

Analysis of 5M ChatGPT conversations: once "review" enters the fan-out (hidden
behind "which X is better", "should I buy X"), the model leans on Reddit for
social proof and Trustpilot for ratings; Wikipedia's weight is falling.

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
  notes.
- Ghost-citation rate per platform and stage, with the measurement method stated.
