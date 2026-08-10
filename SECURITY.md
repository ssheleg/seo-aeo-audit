# Security

## What this skill actually does on your machine

`seo-aeo-audit` is documentation plus **six** small Python scripts. Installed, it is:

| Component | Runtime behavior |
|---|---|
| `SKILL.md` + `references/*.md` | Text. Read by the agent, executes nothing. |
| `scripts/*.py` — six of them | Run only when you or the agent invokes one. Python **standard library only** — no dependencies, no install step. None writes a file; every result goes to stdout. Three of them execute `gcloud` as a subprocess — see below. |
| `commands/`, `cursor/rules/` | Text read by the host agent. |
| `bin/seo-aeo-audit.js` (npm installer) | Copies the skill directory and the slash command into `~/.claude/`. No network, no post-install script. |

There is no telemetry, no analytics, no phone-home, and nothing writes outside
the paths above.

## What each script reaches, exactly

Measured, not asserted — the verification command at the bottom reproduces this
table for all six.

| script | outbound | executes a subprocess | writes |
|---|---|---|---|
| `page_audit.py` | the URLs **you** pass | no | no |
| `sitemap_audit.py` | the sitemap URL you pass, and sitemaps it nests | no | no |
| `psi_pull.py` | `www.googleapis.com` (PageSpeed Insights) | no | no |
| `gsc_pull.py` | `searchconsole.googleapis.com` | **yes** — `gcloud` | no |
| `url_inspection.py` | `searchconsole.googleapis.com` | **yes** — `gcloud` | no |
| `preflight.py` | the origin you pass, `searchconsole.googleapis.com`, `www.googleapis.com` | **yes** — `gcloud` | no |

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
anywhere in the six — the `gcloud` calls pass an argument list, so nothing you
type is interpreted by a shell.

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

# The entire I/O surface of all six scripts, in one command:
grep -rnE "urlopen|build_opener|opener\.open|subprocess\.|socket|os\.system|\beval\(|\bexec\(|\bopen\(" \
  plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/
```

The second command prints **22 lines and that is all of it**: the `urllib`
entry points, the opener that carries `page_audit.py`'s scheme guard, the three
`subprocess.run` blocks that call `gcloud` (two lines each — the call and the
error branch), and **six `open()` calls, every one of them a file you named
yourself** on the command line (`--file`, `--url-list`, `--urls-file`). No
`os.system`, no `eval`, no `exec`, no raw sockets, no shell string. Everything
else under `plugins/` is markdown.

This grep used to be scoped to `page_audit.py` alone, and the sentence under it
said "no `subprocess`" — true of that file and false of the bundle, in the
document a reader consults precisely because they will not read the code.
