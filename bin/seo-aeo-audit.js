#!/usr/bin/env node
/*
 * seo-aeo-audit installer CLI.
 *
 * Installs the seo-aeo-audit skill into ~/.claude/skills/seo-aeo-audit and the
 * /seo-aeo-audit slash command into ~/.claude/commands/ (same layout as install.sh).
 * Idempotent: existing installs are skipped unless --force. Zero dependencies.
 *
 * For other agents (Cursor, Codex, 70+) use: npx skills add ssheleg/seo-aeo-audit
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const ROOT = path.resolve(__dirname, '..');
const REPO = 'ssheleg/seo-aeo-audit';

// Exit codes are the contract: 0 installed or skipped, 1 corrupted package,
// 2 usage error, 3 refused — the plugin channel owns this agent (--force overrides).
const EXIT_PLUGIN_PRESENT = 3;

/**
 * The plugin spec (`<name>@<marketplace>`) installed for `name` in this home,
 * or null.
 *
 * `installed_plugins.json` is the record of what is actually installed. The
 * `plugins/marketplaces/<name>` directory — the only signal cheaper checks
 * read — under-reports: a marketplace added from a local `directory` source
 * has no dir there at all, and plugin names differ from marketplace names, so
 * a check keyed on it stays green while the shadow lands. Absence and
 * corruption both read as "no plugin": the fresh HOME is the common case, and
 * an installer that crashes on a parse error refuses the machines that need
 * it most.
 */
function installedPluginSpec(home, name) {
  try {
    const raw = fs.readFileSync(
      path.join(home, '.claude', 'plugins', 'installed_plugins.json'), 'utf8');
    const parsed = JSON.parse(raw);
    const plugins =
      parsed && typeof parsed === 'object' &&
      parsed.plugins && typeof parsed.plugins === 'object'
        ? parsed.plugins
        : parsed;
    if (!plugins || typeof plugins !== 'object') return null;
    for (const spec of Object.keys(plugins)) {
      if (spec === name) return `${name}@${name}`;
      if (spec.startsWith(name + '@')) return spec;
    }
  } catch {
    // missing or corrupt = no plugin — fail open on absence, never crash
  }
  return null;
}

function usage() {
  console.log(`seo-aeo-audit installer

Usage:
  npx @ssheleg/seo-aeo-audit [--force]   install skill + /seo-aeo-audit command
                                         into ~/.claude (skip existing unless --force)
  npx @ssheleg/seo-aeo-audit --help

Exit codes:
  0 installed or skipped   2 usage error
  1 corrupted package      3 refused: the seo-aeo-audit PLUGIN is installed in
                             this home — a plain copy would shadow it (pass
                             --force to write it anyway)

Other install paths:
  Claude Code plugin:  /plugin marketplace add ${REPO}
                       /plugin install seo-aeo-audit@seo-aeo-audit
  Any agent (70+):     npx skills add ${REPO}`);
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}

function installOne(label, src, dest, isDir, force) {
  if (fs.existsSync(dest) && !force) {
    console.log(`skip: ${label} already installed at ${dest} (rerun with --force to overwrite)`);
    return;
  }
  fs.rmSync(dest, { recursive: true, force: true });
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  if (isDir) copyDir(src, dest);
  else fs.copyFileSync(src, dest);
  console.log(`Installed ${label} -> ${dest}`);
}

function main(argv) {
  const args = argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    usage();
    return 0;
  }
  const force = args.includes('--force');
  const unknown = args.filter((a) => a !== '--force');
  if (unknown.length) {
    console.error(`unknown argument(s): ${unknown.join(' ')}`);
    usage();
    return 2;
  }

  const skillSrc = path.join(ROOT, 'plugins/seo-aeo-audit/skills/seo-aeo-audit');
  const cmdSrc = path.join(ROOT, 'plugins/seo-aeo-audit/commands/seo-aeo-audit.md');
  for (const [p, what] of [[skillSrc, 'skill sources'], [cmdSrc, 'command source']]) {
    if (!fs.existsSync(p)) {
      console.error(`error: ${what} missing at ${p} — corrupted package?`);
      return 1;
    }
  }

  const home = os.homedir();

  // One channel per agent. A plain ~/.claude/skills/seo-aeo-audit beside an
  // installed plugin is two listings of the same skill, and the stale copy
  // wins — the exact shadow this family's canon forbids. Refuse rather than
  // create it, and refuse LOUDLY: a refusal that exits 0 reads as success to
  // every script above it. Reproduced live 2026-08-29: a bare
  // `npx @ssheleg/telegram-dev` shipped three shadows past a marketplace-dir-
  // only check while the plugin was enabled. The marketplaces/ dir is kept
  // only as a fallback signal — installed_plugins.json is the record.
  const spec = installedPluginSpec(home, 'seo-aeo-audit');
  const marketplace = path.join(home, '.claude', 'plugins', 'marketplaces', 'seo-aeo-audit');
  const viaMarketplaceDir = !spec && fs.existsSync(marketplace);
  if ((spec || viaMarketplaceDir) && !force) {
    const found = spec
      ? `installed as the Claude Code plugin ${spec}\n` +
        '         (declared in ~/.claude/plugins/installed_plugins.json)'
      : `registered as a Claude Code marketplace\n         (${marketplace})`;
    console.error(
      `refused: seo-aeo-audit is already ${found}.\n` +
      '         A plain copy in ~/.claude/skills/seo-aeo-audit would shadow the plugin\n' +
      '         and serve this frozen version forever. Update the plugin channel\n' +
      '         instead:\n' +
      '           claude plugin marketplace update seo-aeo-audit\n' +
      `           claude plugin update ${spec || 'seo-aeo-audit@seo-aeo-audit'}\n` +
      '         Family launcher (updates every member, prunes shadow copies):\n' +
      '           npx --yes sshlg-skills@latest update\n' +
      '         Pass --force to write the plain copy anyway — a deliberate choice\n' +
      '         to run two channels, where the stale one wins.'
    );
    return EXIT_PLUGIN_PRESENT;
  }

  installOne(
    'seo-aeo-audit skill  ',
    skillSrc,
    path.join(home, '.claude', 'skills', 'seo-aeo-audit'),
    true,
    force
  );
  installOne(
    '/seo-aeo-audit command',
    cmdSrc,
    path.join(home, '.claude', 'commands', 'seo-aeo-audit.md'),
    false,
    force
  );
  // The last lines say how the next version arrives and when it takes effect —
  // "Installed" is not a complete sentence. Auto-update is off on purpose: this
  // member composes with its family, and per-marketplace autoUpdate moves each
  // member on its own clock, into combinations nobody tested together.
  console.log(
    '\nUpdates: rerun `npx @ssheleg/seo-aeo-audit@latest --force`, or refresh the\n' +
    'whole family with `npx --yes sshlg-skills@latest update` (every channel,\n' +
    'and it prunes plain copies that would shadow a plugin).\n' +
    'Restart Claude Code (or start a new session) to load the new version —\n' +
    'skills are read at session start, so a running session keeps the old set.'
  );
  return 0;
}

process.exit(main(process.argv));
