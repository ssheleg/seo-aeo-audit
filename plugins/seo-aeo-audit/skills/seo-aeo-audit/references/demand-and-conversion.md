# Track H+ — demand capture, conversion and attribution

Rankings that do not convert are a reporting artifact. This section audits what
happens after the impression: whether the page converts, whether the conversion
is measured, and whether paid and organic pull in the same direction.

Survey context (`STUDY`, practitioner survey — opinion, not effect data): 60.4%
of practitioners say qualified leads and sales are the metric they report on, yet
only 33.7% plan to invest in conversion-focused SEO. That gap is where most
audits leave money.

Tiering for this section: platform mechanics (what is or is not tracked) are
`CONFIRMED` once observed on the account; the vendor and agency case numbers
below are `FIELD` — quote them as illustrations of a mechanism, never as a
forecast.

## H+1. Does the page convert

Audit each money template for the elements that actually move a decision:

- **Transparent pricing in crawlable plain text.** Not behind a JS toggle, not in
  an image — otherwise both buyers and answer engines go to an aggregator for
  your numbers (aeo-geo.md F3).
- **Comparison content that names the alternatives** and states where you lose.
- **Implementation/onboarding detail**: timelines with milestones, integration
  guides showing how you fit an existing stack, technical documentation for the
  evaluator who is not the buyer.
- **Proof**: industry-specific case studies with numbers, ROI calculators or
  self-assessments with real benchmarks.
- **Trust surface**: reviews, guarantees, security and compliance statements,
  named humans.
- **Friction inventory**: list everything between the user and the task, then
  delete it (intent-and-content.md E2b).
- **An offer inside the buyer's acceptable price range.** Pricing below it wins
  the lead and loses the sale: a number that reads as too low re-rates the
  perceived quality of the thing, and high-consideration categories (SaaS, real
  estate) are the most discount-sensitive. Audit the offer itself as a conversion
  element, not only the button (HYPOTHESIS — practitioner framing, SEJ B2B
  lead-generation ebook 2024; no effect data, re-check before it enters a plan).

Roughly 70% of the buying process happens before a prospect contacts sales, and
58% of buyers seek expert input before deciding (`STUDY` — **undated 2025 vendor
figures, B2B buyers only**; quote them from benchmarks.md with that caveat, and
never against the ~1% in-answer click rate, which measures all sessions —
growth-plays G20 carries the same warning). The research-phase assets above *are*
the sales conversation for most of the funnel.

Landing-page rules that carry over from paid: match the page to buyer
sophistication rather than to the keyword (informed prospects skip beginner
content); reinforce one offer in the H1 plus three readable bullets; keep video
below the fold or behind a secondary button (experience-signals.md H3).

CTA form carries a known trade: a contextual, plain-language product mention
inside the content collects fewer clicks but lower-funnel, better-qualified ones,
while a standard CTA block collects more clicks at a worse rate. Decide which one
the template is for and report the matching metric — comparing a contextual CTA
on click-through against a block CTA on conversion rate makes both look wrong
(FIELD — practitioner report, HubSpot, 2024).

## H+2. Lead capture without value destruction

- A lead is a **transaction**, not a relationship: someone traded attention or
  data because they believe you will solve a problem. Deliver the value before
  extracting more.
- Gated assets must be worth the gate. A PDF the visitor could have googled turns
  a warm lead hostile — and the follow-up email turns it into a spam report.
- Ask for the minimum information the next step actually requires; every field is
  a conversion tax. Enrich later rather than interrogating up front.
- **One exception, and only one: a field that disqualifies leads you cannot
  service.** A medical-supply team added an insurance field; form abandonment
  jumped and lead volume fell, while qualification rate, conversion rate and ROI
  all rose (FIELD — single case, HubSpot, 2024). Judge any added field on
  qualified-lead rate, never on form fills — and never add one to fatten a
  database.
- **State on the form what happens next.** "You are entering a sales sequence"
  versus "newsletter only, no drip" is the difference between a lead and a spam
  report. Four gating models worth auditing against each other: fully gated;
  ungated with a subscription CTA; partially gated (content opens, the gate
  appears at a scroll threshold); mixed — gated while the asset is new, free once
  it cools, or a free executive summary with the full asset behind an opt-in
  (FIELD — publisher practice, SEJ, 2024).
- **The funnel is a reporting shape, not a behavior.** Leads move backwards and
  sideways between stages: a budget freeze, a changed brief, a new stakeholder, a
  different device. Auditing one gate at one stage misses them — look for several
  capture points at different data costs, each with its own KPI (FIELD —
  practitioner framing, SEJ, 2024).
- Two capture models, usually paired: accessible content that earns a subscriber,
  and gated content that converts a subscriber into a lead. Audit both paths, and
  check what happens in the first 24 hours after the form.
- For zero-click markets, the owned-audience play (growth-plays.md G16) *is* the
  lead-gen strategy: newsletter, community, notifications.

## H+3. Attribution — stop measuring the last screen

Failure modes to test for, in order of how much revenue they hide:

| Gap | Symptom | Fix |
|---|---|---|
| Last-click only | Organic looks flat while brand/direct grows | Multi-touch view; report assisted and later-touch conversions |
| Untracked calls | Service and local businesses with phone-heavy intent; one mover found 80–90% of a channel's conversions arrived by phone | Call tracking with dynamic number insertion, per-source |
| Missed calls | Leads lost at the door; one firm cut missed calls 30% → 21% and measurably lifted consultations; brands report ~10% more closed leads just by tracking them | Route/answer coverage, after-hours handling |
| Offline conversion not returned to the platform | Bidding optimizes for cheap clicks, not revenue | Offline conversion import, value-based bidding |
| AI referrals unattributed | ChatGPT/Gemini/Perplexity traffic hidden in direct — and mostly hidden in **search**, not direct: in one panel 55.9% of AI-influenced visits arrived via search against 40.4% of ordinary ones (benchmarks.md) | Referral parsing where the platform passes one; inbound-log analysis where it does not; UTM discipline on owned distribution |
| Internal traffic counted as customers | Office, agency and developer sessions inflate every rate the audit quotes. GA4's internal-traffic filter is **created in testing mode and stays inert until somebody activates it**, so "we set that up" is not evidence it is on | Admin → Data Filters: confirm the filter is *Active*, not *Testing*; check the IP list still matches the office and VPN egress. Do this before quoting any conversion rate — a page "converting at 4%" with 15% office sessions is a fiction with a decimal point |
| Cross-device journeys | Desktop research → mobile action | Device-segmented reporting; ~94% of AI search referrals originate on desktop while a majority of Google mobile traffic is iPhone — the two ends of one journey |
| Zero-click and voice | Demand visible in brand search, invisible in landing reports | Track branded search volume and direct traffic as outcome metrics (measurement.md J3b) |
| Discovery that no click records | Referral, directory, dark social and AI-assistant discovery all arrive as direct | **Self-reported attribution**: ask "how did you hear about us?" on the form and on the call, then categorize the free-text answer — the only first-party read on channels no click model sees (FIELD — vendor product data, CallRail, 2025) |
| Form fills counted, outcomes not | Lead volume looks healthy while booked revenue does not move | Track forms per source alongside calls, and attribute to the booked appointment or job rather than to the submission (FIELD — agency case, 2025) |

Sequence the journey before arguing about credit. A workable ladder for AI-era
discovery: AI answer mention → brand visibility; click-through → high-intent
signal; multi-page session → research stage; call, text or booking → conversion
or near-conversion. Each rung needs a different instrument and none of them is
last click (FIELD — vendor framework, CallRail/SEJ, 2025). Speed matters at the
last rung: a captured lead that waits is a lost lead, and one firm cut its
missed-call response time by 98% and reported doubled sales (FIELD — vendor case,
2025).

For a local or short-funnel business, replace citation and ranking counts with
what the funnel already exposes — calls, direction requests, booked jobs. A
citation that produces no call is the same vanity metric ranking positions were
(FIELD — practitioner field data, 2026-07). Measuring the call outcome can also
reverse an investment argument: one multi-location veterinary group found 35–44%
of organic-search callers booked an appointment, and that number is what funded
more SEO (FIELD — vendor case, 2025).

Three rules that keep the measurement section honest. All three come from the
same 2026 practitioner panel — opinion, not effect data — but they are the ones
that survive contact with a client review:

- **There is no single source of truth.** In-platform ROAS is siloed and
  over-attributed; a marketing-efficiency ratio is hard to act on. Pick two
  lenses — one microscope, one satellite — and say what each is for, instead of
  reconciling a dozen.
- **The strategy has to survive attribution loss.** If the plan only works while
  every touch is traceable, it is a measurement plan, not a strategy. Say so
  before recommending attribution tooling that costs more than the decisions it
  improves.
- **Year-over-year CPA, CVR and ROAS are not apples to apples across a price
  change.** A price rise that moved a brand from cheapest to second in its
  competitive set moves the conversion rate by itself. Calibrate for it before
  declaring a decline (algorithm-updates.md has the same discipline for
  ranking causes).

Conversation data is also a content input: call transcripts and chat logs contain
the exact phrasing buyers use. Teams that fed that language back into copy and
targeting report double-digit lead and ROI gains; one agency reported 67% more
leads and 11% higher ROI after mining call conversations, another a 23% sales
lift after aligning landing-page messaging with the questions callers actually
asked. Treat transcripts as the cheapest keyword research you own.

**Map-pack calls need their own number, or they land in the organic pile.**
Where a local business runs paid placement on the map pin, the standard tagging
does not survive a click-to-call: there is no landing page to carry a parameter.
The fix is on the profile rather than in the ad — a dedicated tracking number
entered in the profile's advanced settings, which the platform substitutes for
the organic number only while the paid placement is showing. Without it, paid
calls are counted as organic local demand, and the local channel reports a
success it did not earn (`FIELD`, Aug 2026). Audit it wherever paid and organic
share a listing.

## H+4. Paid and organic in the same room

The audit should say something about paid whenever it exists, because the two
share the SERP, the landing pages and the measurement stack:

- **Message alignment.** Buyers do not separate paid from organic. If ad copy
  contradicts the organic narrative on the same query, the journey breaks.
- **SERP real estate.** AI-era campaign types (Performance Max, Demand Gen,
  AI-expanded search) plus ads inside AI answers change how much organic space
  remains for a query — factor it into traffic forecasts rather than blaming a
  ranking drop.
- **Query overlap.** Paid search-term reports are a live intent feed for organic
  content planning; organic top performers are a candidate list for cheap paid
  coverage where organic is capped.
- **First-party data is the shared asset.** Consent-based first-party and
  zero-party data now drives both bidding quality and personalization; audits
  should note whether it is being collected and returned to the platforms at all.
- **Conversion data is what the automated bidding runs on.** If conversions never
  return to the platform, its model cannot tell which people deserve budget.
  Small accounts often have to consolidate conversion actions just to reach
  usable volume; the intended state is consent-mode conversions plus offline
  conversion import, and where consent blocks that, impression-based audience
  building that does not depend on a click (practitioner panel, 2026 — opinion).
- **What stays controllable under AI-first campaign types is the SEO team's own
  surface**: the creative, the conversion tracking and the landing page. When
  targeting and bidding are automated, page quality is where the remaining
  leverage sits — which is why the CRO findings above are a paid deliverable too.
- **Call sentiment splits by source.** In one vendor's tracked corpus, calls from
  the website, the business phone line and organic search skewed positive, while
  Google Ads calls skewed neutral or negative — earlier-stage explorers, or ad
  copy that did not match the page. Read it as a message-match check, not a
  reason to cut spend. The same corpus found nearly 40% of tracked traffic was
  returning customers, so retention belongs in the count (FIELD — vendor report,
  2025).
- **Landing pages are shared infrastructure.** Speed, clarity and trust work for
  both channels; a CRO win usually lifts both (experience-signals.md H3).

Do not turn the SEO audit into a paid audit. One section, factual, with the
handoff named.

## What to record

- Per money template: the conversion elements present/absent, the conversion rate
  from organic, and the revenue or lead volume attached.
- The measurement inventory: what is tracked, what is not, and the estimated
  blind spot (calls, offline, AI referrals, cross-device).
- The three questions every stakeholder will ask: what did organic contribute,
  how do we know, and what would change it.
