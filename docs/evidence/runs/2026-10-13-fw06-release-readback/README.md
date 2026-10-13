# FW06 release readback — 0.26.6

Exact normally merged release source: `c5a32d23da41d7717942f33995228b36971d2657`.
[Packaging PR37](https://github.com/ssheleg/seo-aeo-audit/pull/37) merged after genuine
[full candidate checks](https://github.com/ssheleg/seo-aeo-audit/actions/runs/38366586778)
on [candidate c06b0a1](https://github.com/ssheleg/seo-aeo-audit/commit/c06b0a14ec13378c54a90fab8279a05f92a809ea) passed both required jobs.

## Exact-main local gate

The clean detached merged source passed **npm run test:all**, exit 0, in 201.22 seconds.
[Machine receipt](exact-main-full.json) and [complete compressed log](exact-main-full.log.gz)
bind the actual source, command, result, elapsed time and disk observation. All 31
negative groups passed, along with the preceding doctrine/behavior and following
nine audit-regression files. The watchdog did not interrupt; minimum observed free
space was 1,788,387,328 bytes. This is a new complete exact-main pass; earlier failed
composed runs remain failed in their original receipts.

The release watcher required this exact-source local receipt before creating the
annotated v0.26.6 tag. It then pushed that tag at the same commit. Release
[38372719449](https://github.com/ssheleg/seo-aeo-audit/actions/runs/38372719449) completed
successfully: validate, House skill audit, release and publish all passed.
[Release receipt](release-run.json) retains their exact states.

No live provider, native host or model-quality claim follows from these source
checks. Parent owns the family pin and installed-state update after publication
and complete payload readback are independently evidenced.

Local `git cat-file -t v0.26.6` returned `tag`; remote `git ls-remote --tags`
returned tag object d51b68f235ff0fc2c6631596d6c839bf7f5ea084 and peeled source
c5a32d23da41d7717942f33995228b36971d2657. No tag was moved or replaced.

## Immutable registry payload readback

[Registry receipt and every file hash](registry-payload.json) records
`@ssheleg/seo-aeo-audit@0.26.6`, its immutable tarball URL and SHA512 SRI.
Registry `gitHead` equals the tagged source. The downloaded archive's SHA512 matches
that SRI; every regular file was compared with `npm pack --json --pack-destination`
from the clean exact tagged checkout: paths, bytes/SHA256, length and mode all equal.
Directory tar entries are not payload files; unsupported member kinds and duplicate
paths would refuse comparison. No downloaded archive was extracted or executed.

**46 files / 1,119,910 bytes; whole payload equal.** This proves the complete
published source payload, not only the seven collector scripts. The receipt records
all four successful release jobs and the exact source again for independent review.

Next action: family owner advances its reviewed SEO pin to the accepted release,
runs its own integration checks, updates installed copies and records byte readback.
This owner branch changes evidence only, keeps 0.26.6, and makes no installed-state
claim. The completed bounded collector contract does not turn missing provider,
native-host or model-quality evidence into a pass.
