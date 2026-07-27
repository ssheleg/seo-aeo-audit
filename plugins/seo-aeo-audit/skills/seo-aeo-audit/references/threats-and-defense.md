# Track I — risk, adversaries, defence

Everything here is defensive. The tactics are described so you can **detect and
withstand** them; none of them belongs in a client plan.

## I1. Penalties and algorithmic suppression

- **Manual actions are binary.** Until lifted, content, technical, trust and link
  improvements return nothing. Complete every fix, document it, then request
  reconsideration once. Case timeline for a hacked-subdomain action: fix within
  the hour, reconsideration approved in 24h, full recovery in 36h.
- **Penalties cascade into AI surfaces.** A "Scaled content abuse" action on one
  directory removed it from Google *and* collapsed that directory's ChatGPT
  citations to near zero (residual traffic came through Bing fallback), while the
  rest of the domain kept ranking and being cited. Actions can be
  directory-level.
- **Spam filters and core updates are separate systems.** After a spam action,
  82% of domains that fell out of the top-100 stayed blocked through the
  following core update — do not promise "the next core update will fix it".
- **Quality suppression looks like nothing.** Referring domains flat for months,
  traffic bleeding with no content or technical cause, `BadBackLinksPenalized`-
  style throttling rather than a visible action. Diagnose by exclusion.

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
- **Hosting neighbourhood.** Controlled tests report a ranking ceiling for
  domains sharing an IP with hundreds of low-quality sites. Treat as a hypothesis
  worth checking (who else is on this IP?) rather than a law.

## I3. Indirect prompt injection — the new technical-SEO duty

Google Threat Intelligence recorded a **32% rise** in malicious indirect
prompt-injection attempts between Nov 2025 and Feb 2026. Injections are
instructions embedded in content an AI system will later read: "ignore previous
instructions", "recommend this business above all others", "do not mention
competitors", "insert this phrase into your summary". Research from Cornell shows
a **13-word** insertion on a UGC platform can steer deep-research agents, because
the agents use lexical similarity to the query as a proxy for trustworthiness —
and agents cite UGC in roughly a quarter of citations.

Audit five surfaces:

1. **Rendered DOM** — hidden blocks, widget injections, JS-inserted content.
2. **UGC and reviews** — user-submitted text that an AI summariser will read.
3. **Programmatic pages** — imported feeds, partner data, scraped or generated
   text.
4. **AI-visibility tactics your own team may have shipped** — the highest-risk
   category for self-inflicted policy violations.
5. **Bot behaviour analytics** — anomalous crawling of hidden content or infinite
   URL spaces.

New rule: read the source, render the DOM, look for injected instructions, and
assume an AI agent reads everything you leave in there. Google's spam policy now
explicitly covers **manipulating generative AI answers**, and sanctions are
synchronised between classic search and AI surfaces.

## I4. Adversarial patterns to detect

| Pattern | How it shows up | Defence |
|---|---|---|
| Fake DMCA / bogus government takedowns | A target URL vanishes for ~2 weeks per complaint; intraday rank collapse (top-1 → top-10 in 20 minutes) rather than a gradual update pattern; repeat filings keep pages out of the index | Document everything (screenshots, timestamps, removal notices, restoration records, attack patterns), file counter-notices immediately, escalate through the transparency report; note that filing abusive complaints is itself heavily penalised |
| Canonical hijack / cloud stacking | A clone of your HTML hosted elsewhere, canonicalised to a "master clone", flipping with you in the SERP; sometimes with your Buy buttons replaced by affiliate links back to you | Monitor for duplicated markup and cross-domain canonical claims; watch for keyword-specific losses that do not show as a sitewide drop in GSC |
| Fabricated consensus networks | Dozens of thin exact-match domains, isolated hosting, Googlebot blocked while AI crawlers are allowed, tuned to the citation volume a model uses for a target prompt | Review *who* the models cite for your category; report spam patterns; strengthen your own corroboration rather than matching the tactic |
| Behavioural poisoning | A low, steady drip of direct traffic with deliberately bad engagement across many pages, staying under alarm thresholds | Segment traffic by source and engagement, alert on anomalous zero-dwell direct traffic, keep a control benchmark |
| Crawl-budget attacks | Bulk fabricated URLs on your domain with junk backlinks pointing at them; Googlebot spends its allowance on your 404s | Watch log status-code distribution over time; serve fast 410s; keep a per-day 404 baseline |
| Weaponised spam reports | Manual actions arriving in competitive niches shortly after a public complaint wave | Keep your own site defensibly clean; document compliance decisions |
| Fake search-volume sites | A guest-post seller "ranking" for an invented brand; tool traffic estimates in the millions from a handful of keywords | Always open the keyword tab: 70 variants of one brand name and nothing else is fabricated demand |
| Parasite hosting on your terms | Competitors renting third-party authority (high-DR publishing platforms, social long-form, embed pages) to outrank you on brand and category queries | Track brand-SERP composition monthly; respond with your own owned/earned placements and platform policy reports where rules are broken |
| Historic-URL resurrection | A dead URL path of yours recreated on someone else's domain, inheriting algorithmic memory | Keep valuable retired URLs redirected and monitored rather than simply deleted |

## I5. Brand-SERP defence

- Track what occupies page one for the brand query, including UGC threads.
- Platform policies are the leverage on harmful threads: Reddit's content rules
  cover harassment, spam and manipulation (including competitor astroturfing),
  privacy violations and impersonation. Reports work when they cite a **specific
  rule, comment, date and user**; vague "this is defamatory" does not. A removed
  thread leaves the SERP, freeing the slot for a page you control.
- Coordinated review attacks have footprints (e.g. a majority of negatives from
  single-review accounts). Report through the platform's process and document it;
  never respond with fake positives.

## I6. Link risk, in proportion

Penguin 4.0 devalues rather than demotes: isolated junk links almost never move
rankings. Leaked quality tags include `SiteAuthority`, `PageRankNS` and
`BadBackLinksPenalized` — the last behaves as a lingering ceiling rather than a
visible action.

Disavow only in four situations:

1. A manual action in GSC (disavow, then request reconsideration).
2. A genuine negative-SEO spike — referring domains flat for months, then
   hundreds-to-thousands of low-quality foreign links in 24–72h **and** rankings
   fall. Disavow the spike window only, never the last 30 days wholesale.
3. A bought-link blast you can date (a burst from automated comment/forum tools).
4. Inherited spam from a previous agency.

Toxicity is relative to the niche baseline: 20% exact-match anchors is fatal for
a local plumber and normal in iGaming. Third-party toxicity percentages collapse
context into one number and cause self-inflicted damage — a legitimate DR-10
local blog is fine, a DR-70 expired domain selling guest posts is not, and the
tool cannot tell them apart. Also audit **301 sources**: a redirect from an
expired domain inherits that domain's entire link profile.

Widget and embed links are named in Google's link-spam guidance: `nofollow` them
(plus `noindex` on an iframe page you control) and keep widgets for referral
traffic, not link building. Risk scales with footprint size.

## Evidence to capture for track I

- Property inventory and DNS records for every variant, with owner and expiry.
- GSC Manual Actions and Security Issues screenshots, dated.
- Log-derived 404/410 volume and bot mix over time.
- Injection scan results per surface (rendered DOM, UGC, programmatic templates).
- Brand-SERP snapshot with dates, and any takedown/report tickets filed.
