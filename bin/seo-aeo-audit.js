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

function usage() {
  console.log(`seo-aeo-audit installer

Usage:
  npx @ssheleg/seo-aeo-audit [--force]   install skill + /seo-aeo-audit command
                                         into ~/.claude (skip existing unless --force)
  npx @ssheleg/seo-aeo-audit --help

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
  return 0;
}

process.exit(main(process.argv));
