# Security

## What this skill actually does on your machine

`seo-aeo-audit` is documentation plus **seven** small Python scripts. Installed, it is:

| Component | Runtime behavior |
|---|---|
| `SKILL.md` + `references/*.md` | Text. Read by the agent, executes nothing. |
| `scripts/*.py` — seven of them | Run only when you or the agent invokes one. Python **standard library only** — no dependencies, no install step. None writes a file; every result goes to stdout. Three of them execute `gcloud` as a subprocess — see below. All seven read three environment variables and no others — see below. |
| `commands/`, `cursor/rules/` | Text read by the host agent. |
| `bin/seo-aeo-audit.js` (npm installer) | Copies the skill directory and the slash command into `~/.claude/`. No network, no post-install script. |

There is no telemetry, no analytics, no phone-home, and nothing writes outside
the paths above.

## What each script reaches, exactly

Measured, not asserted — the verification command at the bottom reproduces this
table for all seven, and `test/validate.py` fails when the count in this file drifts
from the directory. It said **six** scripts and **22** grep lines against a measured
seven and 26 for four releases, in the document a reader consults *because* they will
not read the code (B-17, closed 2026-08-19).

| script | outbound | executes a subprocess | writes |
|---|---|---|---|
| `page_audit.py` | the URLs **you** pass | no | no |
| `sitemap_audit.py` | the sitemap URL you pass, and sitemaps it nests | no | no |
| `psi_pull.py` | `www.googleapis.com` (PageSpeed Insights) | no | no |
| `gsc_pull.py` | `searchconsole.googleapis.com` | **yes** — `gcloud` | no |
| `url_inspection.py` | `searchconsole.googleapis.com` | **yes** — `gcloud` | no |
| `preflight.py` | the origin you pass, `searchconsole.googleapis.com`, `www.googleapis.com` | **yes** — `gcloud` | no |
| `agent_surface.py` | the origin, API host, page and OpenAPI URL **you** pass | no | no |

**The `gcloud` subprocess is the one thing here worth understanding before you
run it.** Three scripts mint a short-lived OAuth access token by running
`gcloud auth print-access-token` and passing the result as a `Bearer` header to
Google's own API. That is the whole interaction: no credential is read from disk
by this skill, none is written, none is logged, and no token appears in any
output. The scripts hold no secret of their own — they borrow the login you
already gave the Google Cloud SDK, and they can reach exactly what that account
can reach. Revoking is `gcloud auth revoke`; it takes effect immediately because
nothing here caches.

There is no `eval`, no `exec`, no `os.system`, no raw socket and no shell string
anywhere in the seven — the `gcloud` calls pass an argument list, so nothing you
type is interpreted by a shell.

## The three environment variables every script reads

Each script stamps its output with a **producer block** saying which execution
produced it — tool version, script, UTC timestamp, interpreter, arguments and the
input set it was pointed at. Three of those fields are the calling harness's to
supply, so each script reads one variable per field and **nothing else**:

| variable | field it fills |
|---|---|
| `SEO_AEO_AUDIT_ACTOR` | who or what invoked the run |
| `SEO_AEO_AUDIT_MODEL` | the model behind the agent, if the harness knows it |
| `SEO_AEO_AUDIT_TRACE` | the id linking the run to a trace |

Unset is the normal case and is reported as `unavailable: <VAR> is not set by this
harness` — never guessed. Nothing else in the environment is read, no variable is
written, and the values are echoed only into the output you are already reading.

**The arguments in the producer block are redacted.** `psi_pull.py --key <secret>`
is the one flag whose value is a credential; both `--key V` and `--key=V` print as
`<redacted>`, because a producer block is pasted into a deliverable somebody emails.

## Network behavior of `page_audit.py`

The auditor is the one that fetches arbitrary URLs, so its guard is the strictest:

- Plain `GET` requests, **http and https only** — any other scheme (`file://`,
  `ftp://`, `gopher://`, …) is refused before a request is made, and a redirect
  that leaves http(s) is refused too.
- Only to URLs **you** pass via `--url` / `--url-list`. In `--file` mode it makes
  no requests at all, which is how the test suite runs.
- No cookies, no credentials, no auth headers; a plain User-Agent that identifies
  the tool.
- Bounded: `--timeout` (default 20s) and `--max-bytes` (default 5 MB). A declared
  content type that is not HTML/XHTML/XML is refused rather than parsed.
- Read-only: results go to stdout. The script never writes a file. The only files
  it ever **reads** are the two you name yourself (`--file`, `--url-list`).

## What the skill will not tell an agent to do

The audit procedure is explicitly **defensive**. Manipulative tactics —
cloaking, fabricated consensus networks, review manipulation, click-signal
spoofing, takedown abuse — appear only in `references/threats-and-defense.md`,
written as *detect and withstand*, and the skill's non-negotiables forbid
recommending them.

The procedure is also read-only by default: it will not submit forms, request
indexing, disavow links or change a live property without explicit approval in
the session.

## Reporting a problem

Open an issue at <https://github.com/ssheleg/seo-aeo-audit/issues>. If it is
sensitive, say so in the issue without the details and a private channel will be
arranged.

## Verifying for yourself

```bash
git clone https://github.com/ssheleg/seo-aeo-audit && cd seo-aeo-audit
bash scripts/check-docs.sh   # the whole gate: structure, doctrine, behaviour

# The entire I/O surface of all seven scripts, in one command:
grep -rnE "urlopen|build_opener|opener\.open|subprocess\.|socket|os\.environ|os\.system|\beval\(|\bexec\(|\bopen\(" \
  plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/
```

The second command prints **33 lines and that is all of it**, and it breaks down
exactly:

| lines | what they are |
|---|---|
| 13 | `urllib` — **9 that issue a request**: 7 `urlopen` calls, plus the `build_opener` and `opener.open` that carry `page_audit.py`'s scheme guard. The other 4 are 2 import lines and 2 comments that only mention these names |
| 7 | the three `subprocess.run` blocks that call `gcloud`, with their error branches — 2 lines each in `gsc_pull.py` and `url_inspection.py`, 3 in `preflight.py`, which also catches a timeout |
| 7 | `os.environ` — one read per producer field per script, the three variables above |
| 6 | `open()` calls that open a **file**, every one of them a file you named yourself on the command line (`--file`, `--url-list`, `--urls-file`, `--openapi-file`). A seventh line matches `\bopen\(` — `opener.open` — and is counted in the `urllib` row above, which is why the four rows sum to 33 and a per-pattern grep gives 34 |

No `os.system`, no `eval`, no `exec`, no raw sockets, no shell string. Everything
else under `plugins/` is markdown.

Two numbers on this page are counted rather than restated. `test/validate.py` runs
the regex above **out of this file** and compares both the script count and the line
count against the tree, so the pair cannot drift again the way it did between v0.19.0
and v0.22.0.

This grep used to be scoped to `page_audit.py` alone, and the sentence under it
said "no `subprocess`" — true of that file and false of the bundle, in the
document a reader consults precisely because they will not read the code.
