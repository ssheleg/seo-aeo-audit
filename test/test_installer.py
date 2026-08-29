#!/usr/bin/env python3
"""Installer functional tests — both installers, against throwaway HOMEs.

The case that earns this file its place is PLUGIN-PRESENT: an installer that
writes `~/.claude/skills/seo-aeo-audit` while the same skill is installed as a
Claude Code plugin creates a plain copy that shadows the plugin and serves its
frozen version forever. Until v0.25.7 neither installer here looked at all —
the fail-open class: `installed_plugins.json` is the record of what is actually
installed, the `plugins/marketplaces/<name>` directory under-reports (a
directory-sourced marketplace has no dir there, and plugin names differ from
marketplace names), and an exit 0 reads as success to every script above.
Reproduced live in this family on 2026-08-29: a bare `npx @ssheleg/telegram-dev`
shipped three shadows past exactly this hole while the plugin was enabled.

Absence and corruption of the JSON both read as "no plugin" — the fresh HOME is
the common case, and an installer that crashes on a parse error refuses the
machines that need it most. `--force` overrides the refusal, deliberately.

House residue rule: every fake HOME comes from `residue.workspace()`, so a
passing case loses its tree at exit, a failing case KEEPS it (a defect is
debugged by reading the tree it landed in), and the run ends with one line
saying what it left, `nothing` included.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import residue  # noqa: E402

BIN = os.path.join(ROOT, "bin", "seo-aeo-audit.js")
SH = os.path.join(ROOT, "install.sh")
POSIX = os.name == "posix"
NODE = shutil.which("node")

failures = []
cases = 0


def case(name, fn):
    global cases
    cases += 1
    residue.open_case(name)
    try:
        fn()
    except AssertionError as e:
        failures.append("%s: %s" % (name, e))
        print("  FAIL  %s: %s" % (name, e))
    else:
        print("  ok  %s" % name)
        residue.close_case(name)


def run(cmd, home):
    """Run an installer as a process against `home`, never against the real one."""
    proc = subprocess.run(
        cmd,
        cwd=home,  # never the repo: the installer must not depend on its cwd
        env=dict(os.environ, HOME=home, USERPROFILE=home),
        capture_output=True,
        text=True,
        timeout=120,
    )
    return proc.returncode, proc.stdout + proc.stderr


def node_installer(home, *args):
    return run([NODE, BIN] + list(args), home)


def sh_installer(home, *args):
    return run(["bash", SH] + list(args), home)


def skill_dir(home):
    return os.path.join(home, ".claude", "skills", "seo-aeo-audit")


def cmd_file(home):
    return os.path.join(home, ".claude", "commands", "seo-aeo-audit.md")


def declare_plugin(home, spec):
    d = os.path.join(home, ".claude", "plugins")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "installed_plugins.json"), "w", encoding="utf-8") as f:
        json.dump({"version": 2, "plugins": {
            spec: [{"scope": "user", "installPath": "/nonexistent",
                    "version": "0.25.6"}],
        }}, f, indent=2)


def declare_plugins_raw(home, text):
    d = os.path.join(home, ".claude", "plugins")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "installed_plugins.json"), "w", encoding="utf-8") as f:
        f.write(text)


def nothing_written(home):
    assert not os.path.exists(skill_dir(home)), \
        "the plain skill copy was written despite the refusal"
    assert not os.path.exists(cmd_file(home)), \
        "the command file was written despite the refusal"


assert NODE, "node is not on PATH — the npm installer under test is a Node CLI"

# ---------------------------------------------------------------- node CLI --


def fresh_home_installs_and_says_how_updates_arrive():
    home = residue.workspace("home-fresh")
    rc, out = node_installer(home)
    assert rc == 0, "exit %s, expected 0\n%s" % (rc, out)
    assert "Installed" in out, "no 'Installed' line:\n%s" % out
    assert os.path.isfile(os.path.join(skill_dir(home), "SKILL.md")), "SKILL.md missing"
    assert os.path.isfile(os.path.join(skill_dir(home), "references", "myths.md")), \
        "references/myths.md did not travel"
    assert os.path.isfile(os.path.join(skill_dir(home), "scripts", "page_audit.py")), \
        "scripts/page_audit.py did not travel"
    assert os.path.isfile(cmd_file(home)), "/seo-aeo-audit command missing"
    # the last thing an installer states: how the next version arrives, and that
    # a running session will not see it until restart (skills load at session start)
    assert "sshlg-skills@latest update" in out, "no update path named:\n%s" % out
    assert "Restart" in out, "no session-restart reminder:\n%s" % out


def rerun_skips_force_overwrites_unknown_arg_exits_2():
    home = residue.workspace("home-rerun")
    rc, _ = node_installer(home)
    assert rc == 0, "first install failed"
    rc, out = node_installer(home)
    assert rc == 0 and "skip:" in out, "rerun: %s\n%s" % (rc, out)
    rc, out = node_installer(home, "--force")
    assert rc == 0 and "Installed" in out, "--force: %s\n%s" % (rc, out)
    rc, _ = node_installer(home, "--wat")
    assert rc == 2, "unknown arg exit %s, expected 2" % rc


def plugin_present_refuses_exit_3_remedy_nothing_written():
    home = residue.workspace("home-plugin")
    declare_plugin(home, "seo-aeo-audit@seo-aeo-audit")
    rc, out = node_installer(home)
    assert rc == 3, "exit %s, expected 3\n%s" % (rc, out)
    assert "refused" in out, "no 'refused' in output:\n%s" % out
    assert "claude plugin update seo-aeo-audit@seo-aeo-audit" in out, \
        "remedy does not name the plugin spec:\n%s" % out
    assert "--force" in out, "override flag not offered:\n%s" % out
    nothing_written(home)


def differently_named_marketplace_remedy_names_the_real_spec():
    home = residue.workspace("home-othermkt")
    declare_plugin(home, "seo-aeo-audit@sshlg-skills")
    rc, out = node_installer(home)
    assert rc == 3, "exit %s, expected 3\n%s" % (rc, out)
    assert "claude plugin update seo-aeo-audit@sshlg-skills" in out, \
        "remedy does not carry the spec from the JSON:\n%s" % out
    nothing_written(home)


def force_overrides_the_refusal_deliberately():
    home = residue.workspace("home-force")
    declare_plugin(home, "seo-aeo-audit@seo-aeo-audit")
    rc, out = node_installer(home, "--force")
    assert rc == 0, "exit %s, expected 0\n%s" % (rc, out)
    assert os.path.isfile(os.path.join(skill_dir(home), "SKILL.md")), \
        "forced install wrote nothing"


def corrupt_json_reads_as_no_plugin_install_never_crash():
    home = residue.workspace("home-corrupt")
    declare_plugins_raw(home, "{ this is not json")
    rc, out = node_installer(home)
    assert rc == 0, "exit %s, expected 0 (fail open)\n%s" % (rc, out)
    assert os.path.isfile(os.path.join(skill_dir(home), "SKILL.md")), \
        "install did not happen"


def other_plugins_and_a_prefix_collider_do_not_false_refuse():
    home = residue.workspace("home-collider")
    declare_plugins_raw(home, json.dumps({"version": 2, "plugins": {
        "telegram-dev@telegram-dev": [{"scope": "user", "installPath": "/x",
                                       "version": "1.0.0"}],
        "seo-aeo-audit-extra@somewhere": [{"scope": "user", "installPath": "/y",
                                           "version": "1.0.0"}],
    }}))
    rc, out = node_installer(home)
    assert rc == 0, "exit %s, expected 0\n%s" % (rc, out)
    assert os.path.isfile(os.path.join(skill_dir(home), "SKILL.md")), \
        "install did not happen"


def marketplaces_dir_alone_still_refuses_fallback_signal():
    home = residue.workspace("home-mktdir")
    os.makedirs(os.path.join(home, ".claude", "plugins", "marketplaces",
                             "seo-aeo-audit"))
    rc, out = node_installer(home)
    assert rc == 3, "exit %s, expected 3\n%s" % (rc, out)
    assert "claude plugin update seo-aeo-audit@seo-aeo-audit" in out, \
        "no default remedy spec:\n%s" % out
    nothing_written(home)


for _name, _fn in [
    ("node: fresh HOME installs skill + command, and says how updates arrive",
     fresh_home_installs_and_says_how_updates_arrive),
    ("node: rerun skips, --force overwrites, unknown arg exits 2",
     rerun_skips_force_overwrites_unknown_arg_exits_2),
    ("node: plugin present in installed_plugins.json — refuse, exit 3, remedy, nothing written",
     plugin_present_refuses_exit_3_remedy_nothing_written),
    ("node: plugin under a differently-named marketplace — remedy names the real spec",
     differently_named_marketplace_remedy_names_the_real_spec),
    ("node: --force overrides the refusal, deliberately",
     force_overrides_the_refusal_deliberately),
    ("node: corrupt installed_plugins.json reads as no plugin — install, never crash",
     corrupt_json_reads_as_no_plugin_install_never_crash),
    ("node: other plugins, and a prefix-collider, do not trigger a false refusal",
     other_plugins_and_a_prefix_collider_do_not_false_refuse),
    ("node: marketplaces/<name> dir alone still refuses (fallback signal, exit 3)",
     marketplaces_dir_alone_still_refuses_fallback_signal),
]:
    case(_name, _fn)

# --------------------------------------------------------------- install.sh --

if POSIX:
    def sh_fresh_install_rerun_skip():
        home = residue.workspace("home-sh-fresh")
        rc, out = sh_installer(home)
        assert rc == 0, "exit %s, expected 0\n%s" % (rc, out)
        assert os.path.isfile(os.path.join(skill_dir(home), "SKILL.md")), "SKILL.md missing"
        assert os.path.isfile(cmd_file(home)), "/seo-aeo-audit command missing"
        assert "sshlg-skills@latest update" in out, "no update path named:\n%s" % out
        assert "Restart" in out, "no session-restart reminder:\n%s" % out
        rc, out = sh_installer(home)
        assert rc == 0 and "skip:" in out, "rerun: %s\n%s" % (rc, out)

    def sh_plugin_present_refuses_and_force_installs():
        home = residue.workspace("home-sh-plugin")
        declare_plugin(home, "seo-aeo-audit@seo-aeo-audit")
        rc, out = sh_installer(home)
        assert rc == 3, "exit %s, expected 3\n%s" % (rc, out)
        assert "claude plugin update seo-aeo-audit@seo-aeo-audit" in out, \
            "remedy does not name the plugin spec:\n%s" % out
        nothing_written(home)
        rc, out = sh_installer(home, "--force")
        assert rc == 0, "--force exit %s\n%s" % (rc, out)
        assert os.path.isfile(os.path.join(skill_dir(home), "SKILL.md")), \
            "forced install wrote nothing"

    def sh_marketplaces_dir_refuses_corrupt_json_fails_open():
        home = residue.workspace("home-sh-mktdir")
        os.makedirs(os.path.join(home, ".claude", "plugins", "marketplaces",
                                 "seo-aeo-audit"))
        rc, out = sh_installer(home)
        assert rc == 3, "marketplace-dir exit %s, expected 3\n%s" % (rc, out)
        shutil.rmtree(os.path.join(home, ".claude", "plugins", "marketplaces"))
        declare_plugins_raw(home, "{ this is not json")
        rc, out = sh_installer(home)
        assert rc == 0, "corrupt-JSON exit %s, expected 0 (fail open)\n%s" % (rc, out)
        assert os.path.isfile(os.path.join(skill_dir(home), "SKILL.md")), \
            "install did not happen"

    for _name, _fn in [
        ("install.sh: fresh install, rerun-skip, and the update line",
         sh_fresh_install_rerun_skip),
        ("install.sh: plugin present — refuse, exit 3, nothing written; --force installs",
         sh_plugin_present_refuses_and_force_installs),
        ("install.sh: marketplaces dir alone refuses; corrupt JSON fails open",
         sh_marketplaces_dir_refuses_corrupt_json_fails_open),
    ]:
        case(_name, _fn)
else:
    print("skip: install.sh cases (POSIX only — use npx, the plugin, or the skills CLI)")

if failures:
    print("\nFAIL: %d of %d" % (len(failures), cases))
    sys.exit(1)
print("PASS: installer behavior — %d cases" % cases)
