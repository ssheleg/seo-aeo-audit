# Track I — risk, adversaries, defense

Everything here is defensive. The tactics are described so you can **detect and
withstand** them; none of them belongs in a client plan.

## Contents

- [I1. Penalties and algorithmic suppression](#i1-penalties-and-algorithmic-suppression)
- [I2. Domain, DNS and infrastructure](#i2-domain-dns-and-infrastructure)
- [I3. Indirect prompt injection — the new technical-SEO duty](#i3-indirect-prompt-injection--the-new-technical-seo-duty)
- [I4. Adversarial patterns to detect](#i4-adversarial-patterns-to-detect)
- [I5. Brand-SERP defense](#i5-brand-serp-defense)
- [I6. Link risk, in proportion](#i6-link-risk-in-proportion)
- [Evidence to capture for track I](#evidence-to-capture-for-track-i)


## I1. Penalties and algorithmic suppression

- **Manual actions are binary.** Until lifted, content, technical, trust and link
  improvements return nothing (`CONFIRMED` — documented behaviour). Complete every
  fix, document it, then request reconsideration once. Case timeline for a
  hacked-subdomain action: fix within the hour, reconsideration approved in 24h,
  full recovery in 36h (`FIELD`, single case, undated — an existence proof that fast
  recovery is possible, not a horizon to promise).
- **Penalties cascade into AI surfaces.** A "Scaled content abuse" action on one
  directory removed it from Google *and* collapsed that directory's ChatGPT
  citations to near zero (residual traffic came through Bing fallback), while the
  rest of the domain kept ranking and being cited. Actions can be
  directory-level.
- **Spam filters and core updates are separate systems.** After a spam action,
  82% of domains that fell out of the top-100 stayed blocked through the following
  core update (`STUDY`, March-2026 SERP study; figures in benchmarks.md) — do not
  promise "the next core update will fix it".
- **Quality suppression looks like nothing.** Referring domains flat for months,
  traffic bleeding with no content or technical cause, `BadBackLinksPenalized`-
  style throttling rather than a visible action. Diagnose by exclusion.
- **Rich results can be withheld as a sanction.** Markup that still passes the
  Rich Results Test but stopped producing the SERP feature is a symptom, not a
  markup bug: spam actions, thin-content and UGC quality warnings, and duplicate
  problems all suppress rich results. Check Manual Actions before anyone touches
  the schema (FIELD, 2026-05).
- **Mass machine-translated content is a demotion profile.** After the May 2026
  core update and the June 2026 spam update, bulk auto-translated content was
  demoted — including on a high-authority UGC platform — and AI Overviews
  followed (FIELD, 2026-07). Audit every auto-translated locale you run before
  reaching for a sitewide explanation.
- **Cluster the losses before you conclude.** Deindexation can correlate with a
  syntactic attribute rather than with content: around the March 2026 update
  roughly 20% of two-to-three-year-old URLs carrying a colon in the title element
  dropped out of the index in one tracked set (HYPOTHESIS, 2026-03). Pivot the
  dropped URLs on template, title syntax, publish age and directory, and look for
  the shared attribute before rewriting anything.
- **Reconsideration hygiene.** Confirm that removals and redirects actually
  resolve, resubmit the sitemap, and watch crawl and index behavior while the
  review is open. Work shipped while the flag was up earns no credit, and a
  premature request can be rejected (FIELD, 2026-06).

## I2. Domain, DNS and infrastructure

- **Subdomain takeover.** Real case: the `www` DNS record pointed at a
  decommissioned cloud redirect app; when the app was shut down the subdomain was
  released, an attacker claimed it and pointed it at a gambling network. The site
  was fully deindexed; the tell was a one-day spike of 12,000 clicks on gambling
  queries to the `www` homepage, visible only in the **domain property**.
  Checks: verify every property variant in GSC; monitor DNS and traffic for both
  `www` and non-`www`; inventory dangling CNAMEs to decommissioned services;
  expect a 24h+ lag between deindexation and any manual action; when
  investigating look for **spikes**, not only drops.
- **Registrar risk.** A 27-year-old domain was transferred to a stranger's
  account with no documentation, despite privacy protection and 2FA, and support
  closed the ticket. Registrar lock, a monitored registrant mailbox, a documented
  recovery path and an out-of-band contact belong in the audit.
- **Staging exposure.** Search operators still surface dev/staging hosts
  (`site:dev.*`, `site:staging.*` patterns and custom search engines). Check your
  own before a competitor does; block with auth, not with `robots.txt`.
- **Hosting neighborhood.** Controlled tests report a ranking ceiling for
  domains sharing an IP with hundreds of low-quality sites. Treat as a hypothesis
  worth checking (who else is on this IP?) rather than a law. In the reported
  test the ceiling sat near position 7 for IPs carrying 200+ domains, while
  isolated cloud instances took 90% of the top-10 slots (FIELD, 2026-05-22).

## I3. Indirect prompt injection — the new technical-SEO duty

Google Threat Intelligence recorded a **32% rise** in malicious indirect
prompt-injection attempts between Nov 2025 and Feb 2026 (`STUDY` — vendor threat
report, window stated). Injections are
instructions embedded in content an AI system will later read: "ignore previous
instructions", "recommend this business above all others", "do not mention
competitors", "insert this phrase into your summary". Research from Cornell shows
a **13-word** insertion on a UGC platform can steer deep-research agents, because
the agents use lexical similarity to the query as a proxy for trustworthiness —
and agents cite UGC in roughly a quarter of citations (`STUDY` — published academic
work; the citation share is from the same paper).

Audit five surfaces:

1. **Rendered DOM** — hidden blocks, widget injections, JS-inserted content.
2. **UGC and reviews** — user-submitted text that an AI summarizer will read.
3. **Programmatic pages** — imported feeds, partner data, scraped or generated
   text.
4. **AI-visibility tactics your own team may have shipped** — the highest-risk
   category for self-inflicted policy violations.
5. **Bot behavior analytics** — anomalous crawling of hidden content or infinite
   URL spaces.

New rule: read the source, render the DOM, look for injected instructions, and
assume an AI agent reads everything you leave in there. Google's spam policy now
explicitly covers **manipulating generative AI answers**, and sanctions are
synchronized between classic search and AI surfaces.

Two 2026 additions to the same duty:

- **Third-party-writable fields are assistant input now.** Google Business
  Profile reviews and customer Q&A became declared input to a connected AI
  assistant in June 2026 (CONFIRMED, 2026-06-11). Any field a stranger can write
  on a listing you own is an instruction channel — moderate it exactly like
  on-site UGC, and include it in surface 2 of the scan.
- **A hidden layer "for the models" is a double liability.** Hidden text is
  demoted in ranking, and models extract preferentially from nearer the top of
  the page anyway (STUDY, 2026-05, 54-study meta-analysis) — so the block buys
  nothing and now also lands under the generative-manipulation clause of the spam
  policy. If your own team shipped an invisible block, that is a finding, not a
  tactic.

## I4. Adversarial patterns to detect

| Pattern | How it shows up | Defense |
|---|---|---|
| Fake DMCA / bogus government takedowns | A target URL vanishes for ~2 weeks per complaint; intraday rank collapse (top-1 → top-10 in 20 minutes) rather than a gradual update pattern; repeat filings keep pages out of the index | Document everything (screenshots, timestamps, removal notices, restoration records, attack patterns), file counter-notices immediately, escalate through the transparency report; note that filing abusive complaints is itself heavily penalized |
| Canonical hijack / cloud stacking | A clone of your HTML hosted elsewhere, canonicalized to a "master clone", flipping with you in the SERP; sometimes with your Buy buttons replaced by affiliate links back to you | Monitor for duplicated markup and cross-domain canonical claims; watch for keyword-specific losses that do not show as a sitewide drop in GSC |
| Fabricated consensus networks | Dozens of thin exact-match domains, isolated hosting, Googlebot blocked while AI crawlers are allowed, tuned to the citation volume a model uses for a target prompt | Review *who* the models cite for your category; report spam patterns; strengthen your own corroboration rather than matching the tactic |
| Fabricated information gain | Thin pages made to look data-rich: one national statistic re-derived per location across a large exact-match-domain network, so every town page carries "unique" numbers that are the same figure divided differently. Signature: identical sentence scaffolding across hundreds of hosts, per-location numbers that reconcile to a single national source, no method or collection date anywhere, no named author, and no primary source that predates the network (`HYPOTHESIS` — pattern description, no controlled measurement) | Detection only. When a competitor's data claims look impossible for their size, reconcile their per-location numbers against the national figure and check whether a method is published; report the pattern as scaled/thin content. Defensively, make your own information gain checkable — publish the collection method, the sample and the date next to every original number, so a reconciliation test separates you from the network instead of grouping you with it (intent-and-content.md, ranking-model.md). Never the tactic |
| Behavioral poisoning | A low, steady drip of direct traffic with deliberately bad engagement across many pages, staying under alarm thresholds | Segment traffic by source and engagement, alert on anomalous zero-dwell direct traffic, keep a control benchmark |
| Crawl-budget attacks | Bulk fabricated URLs on your domain with junk backlinks pointing at them; Googlebot spends its allowance on your 404s | Watch log status-code distribution over time; serve fast 410s; keep a per-day 404 baseline |
| Weaponized spam reports | Manual actions arriving in competitive niches shortly after a public complaint wave | Keep your own site defensibly clean; document compliance decisions |
| Fake search-volume sites | A guest-post seller "ranking" for an invented brand; tool traffic estimates in the millions from a handful of keywords | Always open the keyword tab: 70 variants of one brand name and nothing else is fabricated demand |
| Parasite hosting on your terms | Competitors renting third-party authority (high-DR publishing platforms, social long-form, embed pages) to outrank you on brand and category queries | Track brand-SERP composition monthly; respond with your own owned/earned placements and platform policy reports where rules are broken |
| Historic-URL resurrection | A dead URL path of yours recreated on someone else's domain, inheriting algorithmic memory | Keep valuable retired URLs redirected and monitored rather than simply deleted |
| Autocomplete and volume injection | Suggestions pairing your brand with terms nobody types, or someone else's brand riding your head term; third-party tools report volume that GSC impressions never corroborate | Snapshot brand autocomplete per country monthly, report fabricated suggestions through Google's autocomplete feedback link, and refuse to budget against tool volume with no impression trail (FIELD, 2026-06-18) |
| Retrieve-and-switch | A page earns indexing and stable retrieval on inoffensive informational filler, and the body is swapped for the commercial or affiliate offer once the engines are reliably pulling it. Signature: a URL whose ranking history and inbound context do not match the content it serves today, and a stored render that disagrees with the live page in substance rather than in detail | Detection only. Compare a competitor's cached/stored render against the live page before treating their position as evidence of anything; on your own estate, the same comparison catches a compromised template. `HYPOTHESIS` — pattern description, no controlled measurement |
| Canonical pulsing from expired domains | A cross-domain canonical pointed from an aged expired domain at a money page, removed the moment suppression lands, and reapplied once the historical score has reset — the removal is the point, because it breaks the association before it can be scored against the target | Detection only, and it is the same watch as the canonical-hijack row: cross-domain canonical claims naming your properties, plus the 301-source audit in I6, which is where an expired domain's whole profile arrives. `HYPOTHESIS` |

Several of these need more than a row.

**Takedown abuse — plan for a campaign, not an incident.** Intake carries no
identity or veracity check, and Google enforces US DMCA globally regardless of
local jurisdiction (CONFIRMED, 2026-07-01). What the defense actually looks like:

- **Expect re-filing.** One documented URL stayed suppressed for 2.5 months after
  Google had already confirmed the request was fraudulent, and repeat counter-
  notices returned template refusals for "the same URL". Operators with in-house
  counsel report a fresh complaint landing as the page re-enters the index, so it
  never holds a position long enough to recover (FIELD, 2026-06-09).
- **The government-request variant is worse.** It needs an explicit appeal rather
  than a counter-notice, and has been used against third-party review pages with
  no plausible state interest (FIELD, 2026-06-09).
- **Volume is rising.** Attack frequency rose 100–200% within days of public
  coverage, with takedown-as-a-service sellers and automated filings as the
  scaling mechanism (FIELD, 2026-06). Budget the defense as a standing cost, not
  a one-off legal bill.
- **Build the pattern case, not the single rebuttal.** Cluster filings by
  originating IP range, template wording and repeated fictitious firm names, and
  put the cluster into the counter-notice and every escalation. Google
  demonstrably detects patterns at scale elsewhere; give it the pattern.
- **Verify per country.** A removal can be scoped to one market, so a page that
  looks intact from your own location may be gone in the one that pays
  (HYPOTHESIS, 2026-06). Check with country-scoped rank data, not your browser.
- **"Not indexed yet" is not safety.** Google's largest complainant plateaued at
  60–70M URL removal requests per week, ~8% of them for URLs Google had not yet
  indexed, suppressed pre-emptively through a trusted-partner bulk channel
  (CONFIRMED, 2026-06-23). A page that never appeared may have been blocked
  rather than missed — check the transparency record before debugging indexing.
- **Never answer in kind.** A domain filing roughly 800 false complaints a day
  was itself removed from the index, with recovery estimated at 18–24 months
  (FIELD, 2026-06-18). Document and escalate; do not file.

**Canonical hijack — where the loss actually shows.** In the documented case the
clone displaced the original on about half the tracked keywords, the two
alternated in the SERP daily, and in places both ranked at once (positions 7 and
23). The shadow-affiliate variant swaps the clone's buy path for affiliate links
pointing back at you: you fulfill the order and pay the commission, and GSC shows
nothing because the displacement is keyword-specific. Detection: affiliate
payouts to partners you never recruited, plus keyword-level losses with no
sitewide drop (FIELD, 2026-06-15).

**Behavioral poisoning — the clock matters.** Click-quality data is collected in
a 28-day window and reranked on a 13-month history (experience-signals.md), so
the damage outlives the attack by about a year. The drip rotates source IPs
continuously, which is why per-IP rate limits and CDN bot rules do not catch it.
Alert on zero-dwell direct traffic per template against a control benchmark
**inside** the collection window, not at quarter end (FIELD, 2026-06-16).

**The paid-mention market now sells itself as AEO.** The industry's belief that
third-party brand mentions drive AI visibility opened an arbitrage: outreach
vendors repackaging the same link inventory as "GEO" or "AI visibility" at a
large multiple of a normal placement price. This one arrives as a proposal on the
client's desk, so the audit needs the signature rather than an opinion (`FIELD`,
vendor audits, Aug 2026):

- A brand mention priced at a multiple of that vendor's own link price, with
  "partnership" language standing in for a disclosure.
- Donor domains with no topical relationship to the client — a single page about
  the client's category on a site otherwise publishing whatever pays.
- Placements on pages already carrying outbound commercial anchors to
  competitors.
- Community "seeding" that the platform removes within weeks for breaching its
  own rules, which is the tell that it was never participation.
- Billing where the vendor pays the publisher directly and re-invoices the
  client, with approval falling to whoever is junior enough not to evaluate the
  donor.

Two things to say when it lands. Google's spam policy covers manipulating
generative answers and states there are no special optimizations for its AI
surfaces (algorithm-updates.md), so this is the paid-link conversation wearing a
new label, and sanctions are synced across surfaces. And the mechanism the pitch
rests on — that models learn brands from third-party sources — does not imply
that *bought* mentions on discounted domains change an answer; one proposed
explanation for any short-term effect is that a second index still carries pages
the first has discounted, which would make the window a defect rather than a
channel (`HYPOTHESIS`).

**Synthetic consensus is cheap, and the cluster is what sells it.** A fabricated
industry award — no legal entity, no committee, no ceremony, judges invented —
ranked first for its category term within days, and Google's AI Overview
described it in its own words as a leading programme in the field. The lever was
not the site: it was three source types agreeing (an exact-match domain, a
neutral-reading reference page, and a page on an established personal domain the
engine already trusted), with the last one carrying the weight because a known
entity vouching for an unknown one reads as corroboration. A press-release
variant reached an AI Overview citation within minutes of distribution
(`FIELD`, Aug 2026). Defensively this is the "fabricated consensus networks" row
above with a documented case attached, and the consequence for your own site is
the uncomfortable one: an engine that cannot verify an entity is also unable to
verify *you*, so first-party claims need corroboration you can point at —
independent coverage, a method published next to your numbers, records that
predate the claim.

**Coordinated generation is detected at the cluster, not the page.** Google
Research published a two-stage system for synthetic-content abuse on video
platforms (S-CTS): one component scores repetitive, templated generated
narratives, the other groups accounts by shared infrastructure signals into
"generation clusters" which are then terminated together — reported as 50,000
clusters covering 130,000 channels over six months, with a lightweight adapter
retrained when operators switch generative models (`STUDY`, published research,
2026-08; a video-platform system, transferred here by analogy — the mechanism is
not documented for web search). What transfers is the join key: shared build
footprints, one publishing cadence and one template make a set of properties a
single object to a detector even where each page would pass alone. Two audit
consequences follow, both defensive. A site built by a page generator carries its
boilerplate signature whether or not the content is thin — check what your
builder leaves behind. And a "network" of your own microsites sharing a
template, a host and a publishing script is one object, so the risk is not priced
per site.

**Review moderation is a queue, and queues are attackable.** Local review
platforms generate a ticket per report rather than merging duplicates, so a
volume of reports on one review distributes across several human reviewers, and
the attack works on the probability that one of them errs — which means genuine
reviews disappear without any policy having been broken (`FIELD`, Aug 2026).
Defensive practice: track review counts per location over time so a removal is
noticed at all, keep your own evidence for each review you would contest, and
limit profile access to the smallest set of roles that still gives you
redundancy, so a suspension on one account cannot take a whole portfolio of
locations with it.

## I5. Brand-SERP defense

- Track what occupies page one for the brand query, including UGC threads.
- Platform policies are the leverage on harmful threads: Reddit's content rules
  cover harassment, spam and manipulation (including competitor astroturfing),
  privacy violations and impersonation. Reports work when they cite a **specific
  rule, comment, date and user**; vague "this is defamatory" does not. A removed
  thread leaves the SERP, freeing the slot for a page you control.
- Coordinated review attacks have footprints (e.g. a majority of negatives from
  single-review accounts). Report through the platform's process and document it;
  never respond with fake positives.
- The clearest footprint is **divergence between platforms**, not a single low
  score: one company sat at 1.3/5 on one review site and 4.87 on another in the
  same period, with 75% of the negatives coming from single-review accounts
  (FIELD, 2026-07-13). Check every platform the engines actually cite
  (entity-and-brand.md), not only the one you already monitor.
- **Third-party entity records are an attack surface.** Wikidata moderates at a
  lower threshold than Wikipedia and Google trusts it as a structured source;
  entries also disappear fast when external corroboration is thin — one
  practitioner's own entry was removed within 24h (FIELD, 2026-06-16). Watchlist
  your item, and treat a silent deletion or an unexplained claim change as a
  brand-SERP incident, not a data-quality chore (entity-and-brand.md).
- **Legal review removals are becoming visible.** Since April 2026 Google
  Business Profile in Germany publishes how many reviews the business had removed
  by legal process, counted separately from policy removals. Law-based removals
  happen without the reviewer taking part — they receive an email with an appeal
  option — so your only warning arrives in the mailbox tied to the listing, and
  in that market a scrubbing habit is now disclosed to consumers (CONFIRMED,
  2026-04-29).
- **Displacement beats removal, and it is slower than anyone budgets.** A hostile
  thread ranking on the brand term survives because it earns clicks, and chasing
  moderators turns them adversarial. The documented sequence that worked ran the
  other way round: months of genuine presence on the platform first, until
  first-party threads ranked for a spread of brand queries and the sentiment mix
  changed; only then, with an account that read as official rather than as spam,
  an approach to the original author — whose complaint had since been fixed —
  which ended in the author removing their own post (FIELD, Aug 2026). The order
  is the finding: the outreach worked because the trust was already built, and a
  plan that starts at the outreach is a plan to be ignored.
- **Own the review query rather than renting it.** A first-party `/reviews`
  section on the root domain competes for "<brand> reviews" against third-party
  threads and feeds the same source pool the answer engines read
  (growth-plays.md G29). It holds only on genuine feedback: choosing which
  customers are asked is review gating, which is a policy violation and belongs
  on this page, not in a plan.
- Keep a register of every report filed: rule cited, content, date, user,
  outcome. Removal then becomes a repeatable process rather than a one-off favor.

## I6. Link risk, in proportion

Penguin 4.0 devalues rather than demotes: isolated junk links almost never move
rankings (`CONFIRMED` — engine-documented behaviour). Leaked quality tags include
`SiteAuthority`, `PageRankNS` and `BadBackLinksPenalized`, the last behaving as a
lingering ceiling rather than a visible action — a leak describes architecture, not
a live weight, so that reading is `STUDY` at best (evidence-tiers.md rule 5).

Disavow only in four situations:

1. A manual action in GSC (disavow, then request reconsideration).
2. A genuine negative-SEO spike — referring domains flat for months, then
   hundreds-to-thousands of low-quality foreign links in 24–72h **and** rankings
   fall. Disavow the spike window only, never the last 30 days wholesale.
3. A bought-link blast you can date (a burst from automated comment/forum tools).
4. Inherited spam from a previous agency.

Toxicity is relative to the niche baseline: 20% exact-match anchors is fatal for a
local plumber and normal in iGaming (`FIELD` — practitioner reading, undated; the
*relativity* is the durable part, the percentage is an illustration). Third-party toxicity percentages collapse
context into one number and cause self-inflicted damage — a legitimate DR-10
local blog is fine, a DR-70 expired domain selling guest posts is not, and the
tool cannot tell them apart. Also audit **301 sources**: a redirect from an
expired domain inherits that domain's entire link profile.

Two more numbers for the spike test: the algorithm reacts to **scale patterns**,
not to isolated junk — roughly 200 exact-match anchors inside 48 hours, or 500
links in a month from automated comment and forum tooling, are what moves it
(FIELD, 2026-07-08). Below that, assume devaluation and keep the disavow file
closed.

**External anchor distribution and velocity (owned here; referenced from
architecture-and-equity.md and growth-plays.md P8).** A natural-looking external
profile as observed in field work: branded 40–50%, naked URL 20–30%, generic
15–25%, partial match 10–15%, exact match 5–10%, with a 30–50% nofollow share
and a home-market-weighted geo mix; expect 5–15%/yr decay. Velocity shape
matters as much as volume: spiky, event-driven acquisition (launches, PR, a
research release) reads as natural, flat linear growth does not — **500 links in
30 days triggered penalties within 48h in one report, while 370 over 8 months
ranked top-3** (FIELD). Read every one of these bands against the niche
baseline, per the paragraph above. None of this is an internal-anchor rule:
internal anchors are not a spam-risk surface and should stay descriptive and
consistent (architecture-and-equity.md).

Screening an inherited profile or a 301 source, read these as **network
footprints**, not quality signals: a donor blocking third-party SEO crawlers at
server level (nobody can verify its link graph), sponsored posts published as
orphan pages, one-or-two-links-per-article sterility, and a mixed CMS stack
across otherwise identical sites. Network operators work at hiding exactly these
— one 20-site test reported 25% less deindexation over six months from footprint
masking alone (FIELD, 2026-05-19) — so the absence of a visible footprint is not
evidence of a clean donor. Judge donors on independently verifiable traffic and
relevance; the GSC Links report is the sampled view Google itself shows you
(tooling.md).

Widget and embed links are named in Google's link-spam guidance: `nofollow` them
(plus `noindex` on an iframe page you control) and keep widgets for referral
traffic, not link building. Risk scales with footprint size.

## Evidence to capture for track I

- Property inventory and DNS records for every variant, with owner and expiry.
- GSC Manual Actions and Security Issues screenshots, dated.
- Log-derived 404/410 volume and bot mix over time.
- Injection scan results per surface (rendered DOM, UGC, programmatic templates,
  third-party-writable listing fields).
- Brand-SERP snapshot with dates, and any takedown/report tickets filed.
- Brand autocomplete snapshot per term and country, dated.
- Takedown register: filing date, claimant named, URL, removal and restoration
  dates, counter-notice or appeal reference, and the country checked.
- Review-platform spread — rating on every platform the engines cite, with the
  share of negatives from single-review accounts.
