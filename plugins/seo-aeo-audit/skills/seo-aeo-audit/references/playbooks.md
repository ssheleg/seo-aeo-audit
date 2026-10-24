# Playbooks: procedures run on a live property

A playbook is a procedure that was actually run on a live property, written so that
another agent can reproduce it, verify the result, and improve it. Each one grows: a
new run adds its date, its counts and what it got wrong, and a trap observed once is
written down before the next run meets it again.

This file holds procedures and what they observed. The doctrine they rest on has its
own homes and is linked, never restated: routing, the checkup by occasion, UI-only
steps, paid indexers, provider sheets and the push ledger live in
[tooling.md](tooling.md); dated numbers in [benchmarks.md](benchmarks.md); experiment
design in [experiments.md](experiments.md).

Every observation here is `FIELD` (one property or one network, no published method)
unless it says otherwise, and the property is never named: write "the property",
"the site", `example.com`. A provider's or engine's documented contract is marked as
such and dated; it says what the API accepts, never what it achieves.

## Contents

- [How a playbook is written and grown](#how-a-playbook-is-written-and-grown)
- [PB1. An indexing push as an experiment with a held-out control](#pb1-an-indexing-push-as-an-experiment-with-a-held-out-control)
- [PB2. IndexNow on every verified release](#pb2-indexnow-on-every-verified-release)
- [PB3. Baidu for Chinese pages](#pb3-baidu-for-chinese-pages)
- [PB4. Request indexing in Search Console](#pb4-request-indexing-in-search-console)
- [PB5. A full showcase over a dynamic catalog](#pb5-a-full-showcase-over-a-dynamic-catalog)
- [PB6. Problem-intent pages for an error message](#pb6-problem-intent-pages-for-an-error-message)
- [PB7. A sweep for unmeasured claims](#pb7-a-sweep-for-unmeasured-claims)
- [PB8. Localizing for a non-Google engine](#pb8-localizing-for-a-non-google-engine)
- [PB9. Grammatical case in templates](#pb9-grammatical-case-in-templates)
- [PB10. A network of satellite sites](#pb10-a-network-of-satellite-sites)

## How a playbook is written and grown

Every playbook carries the same five parts, in this order:

| Part | What it holds |
|---|---|
| When to use | the situation that makes the procedure worth running, and what it is not for |
| Steps | the procedure, with generic command shapes on `example.com` |
| Verify | how to read the result back from a first-party source; a provider's own count is never the verdict |
| Measure and improve | what to read next, on which day, and the runs so far with their dates and counts |
| Fails when | the traps a run actually hit |

A new run appends a dated line under *Runs so far* with both counts of any comparison
(never a percentage alone), and a new trap goes under *Fails when*. A run that
contradicts an earlier one keeps both lines and says so; the procedure changes only
when a run shows why. A playbook that reaches three properties with the same result
earns a row in [benchmarks.md](benchmarks.md) with its source and date.

## PB1. An indexing push as an experiment with a held-out control

**When to use.** New pages, a new site, or pages Google discovered and left out, when
the operator has chosen to pay for a push. This is the run-level procedure for the
occasion [tooling.md](tooling.md#the-checkup-by-occasion) defines (*An indexing
push*); the doctrine on paid indexers, owner access and the free levers that go first
is in [tooling.md](tooling.md#paid-indexers-and-index-checkers).

**Steps.**

1. **Candidates.** Every `<loc>` of every child sitemap. The URL Inspection quota
   (benchmarks.md, *URL Inspection API quota*: 2,000 calls per site per day, read
   2026-10-23) decides whether one day covers the list.
2. **Inspect** every candidate and keep the JSON:

   ```bash
   python3 "$SKILL_DIR/scripts/url_inspection.py" --site sc-domain:example.com \
     --urls-file candidates.txt --max-urls 2000 --format json > inspection.json
   ```

3. **Plan.** Keep only URLs Google reports absent (`verdict` not `PASS`) and allowed:
   `indexing_state` is `INDEXING_ALLOWED`, `robots_txt_state` is `ALLOWED`, and
   `page_fetch_state` is not `SOFT_404`, `REDIRECT_ERROR` or another failed fetch. A
   row with no verdict is missing data, not a candidate. Write the excluded rows into
   the plan by class, so the plan's counts add up to the candidate list.
4. **Split** the kept URLs by a seeded hash into treatment and control, control share
   0.2, so a re-run never moves a URL between arms:

   ```python
   import hashlib
   def arm(url, seed="indexing-2026-10-23"):
       h = int(hashlib.sha256(f"{seed}:{url}".encode()).hexdigest(), 16)
       return "control" if h % 1000 < 200 else "treatment"
   ```

5. **Push** the treatment through one paid indexer and one engine (the call shapes are
   in [tooling.md](tooling.md#provider-sheets)). The key comes from the environment,
   placed there by the vault at run time; it never appears in a command line, a URL
   that is logged, or the ledger.
6. **Ledger.** Write the ledger next to the plan as
   [tooling.md](tooling.md#the-ledger) defines it: task ids and the provider's answers
   as returned, never the key.

**Verify.** On day 7 and day 14, re-run `url_inspection.py` over **both** arms. The
verdict is the treatment's indexed share minus the control's, with both counts. The
provider's own indexed count is its checker's opinion and is recorded beside the
verdict, never as it.

**Measure and improve.** Put the day 7 and day 14 readings on the project's board with
their dates. A pay-per-indexed provider reserves tokens at creation and refunds the
unindexed after 7 days, so read its charge after the refund, not before. Below three
properties or one cohort the verdict is `FIELD`.

Runs so far:

- 2026-10-23, one property: 1,183 of 1,682 sitemap URLs already indexed (70 percent);
  395 URLs pushed, 101 held out. Readings due at day 7 and day 14.
- 2026-10-23/24, a nine-site network: 1,286 of 1,989 sitemap URLs already indexed; 560
  pushed, 142 held out. Readings due at day 7 and day 14.

**Fails when.**

- **The access token expires mid-run.** The gcloud ADC access token lives about an
  hour, so a long inspection run answered HTTP 401 from row 524 on (issue #56).
  `url_inspection.py` re-mints the token since 0.31.1; on an older install, split the
  run into pieces under an hour and merge the JSON.
- **The sitemap lists pages that cannot be indexed.** A `noindex` page or a soft 404 in
  the sitemap spends both inspection quota and money. Exclude them in the plan (step
  3), and file the sitemap defect as a finding of its own.
- **The control is skipped or recomputed.** Without a held-out arm the run measures the
  calendar; a split that is not seeded moves URLs between arms on a re-run.

## PB2. IndexNow on every verified release

**When to use.** Any property whose pages change with releases and that wants Bing,
Yandex and the other IndexNow engines to learn about them without waiting for a crawl.
It is a free lever ([tooling.md](tooling.md#the-checkup-by-occasion)) and does not
replace the sitemap.

**Steps.**

1. **Key file.** Serve the key as a public text file at `https://example.com/<key>.txt`
   whose body is the key; it proves the host. A network needs the file on every host.
2. **URL list.** With no per-URL `lastmod` to diff against, send the whole sitemap,
   including the hreflang alternates it lists. One POST carries up to 10,000 URLs (the
   protocol's documented limit); split above that.
3. **Post to each engine's own endpoint**, not the shared one (the shared endpoint
   refused a key both engines accepted; [tooling.md](tooling.md#field-notes-from-one-property-october-2026)):

   ```bash
   for ep in https://www.bing.com/indexnow https://yandex.com/indexnow; do
     curl -sS -o /dev/null -w "$ep %{http_code}\n" -X POST "$ep" \
       -H 'Content-Type: application/json; charset=utf-8' --data @indexnow.json
   done
   # indexnow.json: {"host":"example.com","key":"<key>",
   #   "keyLocation":"https://example.com/<key>.txt","urlList":[...]}
   ```

4. **Wire it into the release**, after the release's own production verification has
   passed, at most once in 20 hours. Keep the time stamp in a file outside the
   repository, so the release tool's clean-tree check is not tripped by it. A refusal
   is logged and never fails the release.

**Verify.** Record the HTTP status per endpoint and the URL count sent; 200 and 202
both mean accepted. Acceptance is not a crawl: read the host's logs for the engine's
crawler on the pushed URLs over the next days.

**Measure and improve.** Bing Webmaster crawl statistics and Yandex Webmaster's crawl
report a week later; compare the crawled share of the pushed URLs with the release
before IndexNow was wired.

Runs so far:

- 2026-10-23/24, one property: 7,182 URLs in one push; Bing 200, Yandex 202; the shared
  `api.indexnow.org` answered 403 to the same key.

**Fails when.**

- The shared endpoint answers 403 to a key the engines accept directly.
- A satellite host does not serve its own key file, so its URLs are refused.
- The stamp file lives in the repository and makes the next release refuse a dirty
  tree, or the push runs before the release is verified and announces a broken page.

## PB3. Baidu for Chinese pages

**When to use.** A property with Chinese pages that wants Baidu to index them. Baidu
does not take IndexNow; it has its own console, 搜索资源平台 (`ziyuan.baidu.com`), and
its own push API. Regional engines at launch are in
[build-time.md](build-time.md#n17-regional-engines-at-launch).

**Steps.**

1. **Human gate.** Signing in to the console with a Baidu account is the operator's
   step; no route avoids it. Everything around it is the agent's.
2. **Site side first.** Render the HTML-tag verification from an environment variable,
   so verification needs no file upload and an unset variable renders nothing:

   ```html
   <meta name="baidu-site-verification" content="${BAIDU_SITE_VERIFICATION}">
   ```

3. **Verify the site** in the console by the HTML-tag method, after the release that
   carries the tag is live.
4. **Push.** After verification the console issues a push token for 普通收录 (ordinary
   inclusion). POST the Chinese pages only, as `text/plain`, one URL per line, at most
   2,000 URLs a request (the console's documented contract, read 2026-10-24):

   ```bash
   curl -sS -H 'Content-Type: text/plain' --data-binary @zh-urls.txt \
     "http://data.zz.baidu.com/urls?site=https://example.com&token=${BAIDU_PUSH_TOKEN}"
   ```

   The token sits in the query string by Baidu's design: read it from the environment
   and keep the URL out of every log.

**Verify.** The answer's `success` count against the URLs sent, and `remain`, the daily
quota left. Then the console's index report, not the push answer, for inclusion.

**Measure and improve.** Spend the small daily quota on the pages that answer Chinese
queries first; re-read the index report a week after the first push.

Runs so far:

- 2026-10-24, one property: the site side shipped (tag from the environment, a push
  script over the Chinese sitemap); the console sign-in was still waiting on the
  operator, so no push answer has been read back yet.

**Fails when.**

- The token is logged with the request URL.
- The quota is spent on pages in other languages.

## PB4. Request indexing in Search Console

**When to use.** A handful of URLs that matter now, after the free levers. The URL
Inspection API cannot request indexing; it is a UI step, and the way an agent takes it
behind the access rule is in
[tooling.md](tooling.md#ui-only-steps-and-how-an-agent-takes-one). This playbook adds
only what a run taught.

**Steps.**

1. Follow the five steps in tooling.md: a window the agent opened itself, acted on by
   its id; the URL re-read before each click; stop if another session takes the window
   or a sign-in sheet appears.
2. Before starting, confirm the screen is unlocked and the browser is in front.
3. Record "Indexing requested" per URL with the date and its status before the request.

**Verify.** The console's own confirmation, read back, for each URL. A click that was
sent is not a request that was made.

**Measure and improve.** Re-inspect each URL 14 days later with `url_inspection.py` and
record the change of state.

**Fails when.** The screen was locked: the clicks were sent and none landed, so no
request was made. A sign-in sheet or another session in the same browser is a stop,
not something to click through.

## PB5. A full showcase over a dynamic catalog

**When to use.** Stock comes and goes per country or per product, and the public page
for an item is tempted to disappear when its stock does.

**Steps.**

1. **Keep every entity page** in the sitemap and indexable, in stock or not. Never
   `noindex`, redirect or remove a page for being out of stock: the crawl scheduler
   keeps the negative priority after the directive is gone
   ([technical-checks.md](technical-checks.md#a2-indexation-economics), *Out-of-stock
   trap*; the play is growth-plays.md L9).
2. **Make the out-of-stock page useful.** Say plainly that there is no stock now; show
   what is available instead with live prices from the catalog snapshot; offer a
   watch for the item's return and another channel to convert.
3. **No invented values.** A price or count the snapshot lacks is omitted, never
   filled, and a test holds it.
4. **Keep combination pages under a quality rule.** Programmatic product by country
   pages are a different class: near-duplicates in the hundreds of thousands caused
   an index collapse on one site. They stay behind an explicit index policy (the
   pre-publish gate is growth-plays.md G13).

**Verify.** Server HTML of an out-of-stock page: status 200, no `noindex` in the markup
or the `X-Robots-Tag` header, the page listed in the sitemap, and the alternatives
block present with prices only where the snapshot holds them.

**Measure and improve.** The sitemap count before and after, then the indexed share of
the entity pages at the next URL Inspection pass (PB1, step 2).

Runs so far:

- 2026-10-23/24, one property: country URLs in the sitemap went from 1,152 to 1,791.
  Indexed share due at the next inspection.

**Fails when.** A page is hidden for being out of stock, a missing price is filled with
a default, or the full-showcase rule is applied to programmatic combinations.

## PB6. Problem-intent pages for an error message

**When to use.** Searchers type the error they see ("X code not arriving") and
competitors rank pages for it. The page answers the error; the product is one cause
among several.

**Steps.**

1. **Answer the error first**, with honest platform-side causes: the code was sent to
   the app on another device; retry timers and "too many attempts"; a wrong country
   code or a leading zero; numbers the platform refuses (shared, VoIP, banned).
2. **Reach the product only where the number is the cause.** No delivery rate, speed
   or guarantee claims; state the refund rule.
3. **Link the page from the matching entity page in the server HTML**, not only after
   hydration (one question per page:
   [build-time.md](build-time.md#n2-one-question-per-page)).
4. **Keep the first paragraph at most about 155 characters in every locale**: it
   becomes the meta description.
5. **Keep editorial notes out of the served body**, with a test that fails if one
   reaches it.
6. **Quote a platform's UI message only when its official wording in that language is
   certain**; otherwise paraphrase.

**Verify.** Per locale: status 200, a localized title, and the inbound link present in
the server HTML of the entity page:

```bash
curl -s https://example.com/de/entity | grep -c 'href="/de/help/code-not-arriving"'
```

**Measure and improve.** Impressions and clicks for the error queries in Search
Analytics per locale, four and eight weeks after launch; rewrite a first paragraph
whose description the engine replaces.

**Fails when.** A delivery rate or guarantee is claimed; the description runs past its
length in one locale; an editorial note ships in the body; a translated UI message is
invented.

## PB7. A sweep for unmeasured claims

**When to use.** Short marketing chips and descriptions repeat across hundreds of
pages and locales, and some of them claim things about the service that nothing
measures.

**Steps.**

1. **Census** every chip and description in every locale with a one-line script over
   the data, not by reading pages:

   ```bash
   node -e 'for (const l of require("./locales.json")) for (const [k,v] of Object.entries(l.chips)) console.log(l.code, k, v)' | sort
   ```

2. **Separate** claims about the service ("Premium routes", "24/7", "High quality",
   "Great rates", "excellent support") from facts about the entity ("EU coverage").
3. **Remove** every claim no measured fact supports, in every locale at the same
   index, and delete the translation keys left orphaned.
4. **Guard** with a test that scans all locales with a multilingual pattern and fails
   on a planted claim.

**Verify.** A grep of the server HTML, per locale, for every removed string returns
nothing; the guard fails on a plant and passes on the tree.

**Measure and improve.** Re-run the census after every content change; a new claim
enters only with the measured fact that supports it.

Runs so far:

- 2026-10-23/24, one property: 47 chips and 26 descriptions removed across about 200
  indexable pages.

**Fails when.** A claim is removed in one locale and kept in another, or a key is left
orphaned and comes back with the next translation pass.

## PB8. Localizing for a non-Google engine

**When to use.** Chinese pages whose traffic comes through Bing rather than Google, or
any locale where another engine sends the readers.

**Steps.**

1. **Read the engine's own queries first** (`bwt_pull.py`, after
   `preflight.py --bing-site`) before rewriting. The traffic may be brand searches for a different,
   closed service; then the first screen leads with the contrast that searcher needs.
2. **Declare the script**: `<html lang="zh-Hans">` and the JSON-LD `inLanguage` the same
   tag; hreflang stays `zh`, because one Chinese version serves every reader
   ([build-time.md](build-time.md#n18-per-fact-provenance-and-honest-localization)).
3. **One spacing rule** between Han characters and Latin text or digits across the
   whole dictionary: take the majority form and hold it with a guard test.
4. **Put the market's query words in the first paragraph** of the page that answers
   them, since it becomes the description.

**Verify.** Server HTML carries the `lang` and `inLanguage` tags; the guard test fails on
a planted pair in the other form.

**Measure and improve.** Bing queries and clicks for the locale four weeks after the
rewrite, against the queries read in step 1.

Runs so far:

- 2026-10-23/24, one property: 511 spaced pairs against 73 glued, so the spaced form
  became the rule.

**Fails when.** The rewrite starts from guessed queries, or the script tag and
`inLanguage` disagree.

## PB9. Grammatical case in templates

**When to use.** A template inserts an entity name after a preposition, in a language
with grammatical case.

**Steps.**

1. Find templates that put a name after a preposition: "номера из {country}" breaks,
   because names are stored in the nominative and the preposition needs the genitive.
2. Rewrite as "{country}: ..." or another form that needs no inflection.
3. Test each locale's rendered string, not the template.

**Verify.** The rendered strings, per locale, over a sample of names, in the test
output.

**Measure and improve.** Repeat the search after every new template or locale.

**Fails when.** The test reads the template instead of the rendered string, or a fix
inflects one name by hand and leaves the rest broken.

## PB10. A network of satellite sites

**When to use.** One operator runs several hosts that each need to be found on their
own.

**Steps.** Per host:

1. Its own Search Console property and sitemap.
2. Yandex Webmaster and Bing Webmaster entries.
3. Its own IndexNow key file (PB2).
4. Baidu, if it has Chinese pages (PB3).
5. A row per instrument in the property instrument registry
   ([tooling.md](tooling.md#property-instrument-registry)).

The indexing experiment (PB1) runs per network, with its own control arm.

**Verify.** Each host reached in each console, with the evidence of how (the registry's
*Evidence* column), and each key file served.

**Measure and improve.** Indexed share per host at each PB1 reading; a host far below
the others is examined on its own.

Runs so far:

- 2026-10-23/24, a nine-site network: one inspection and one control arm for the whole
  network; the counts are under PB1.

**Fails when.** A host shares a key file or a property with another, or the network's
control arm is mixed with a single property's.
