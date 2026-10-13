"""Parsed-invocation bootstrap reports without provider access or secret reads."""
import contextlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
from collector_coverage_contract import capture, coverage_records

LOCAL_RUN = subprocess.run  # used only for the copied CLI paths and controlled env below


def _run(check, root, workspace):
    count = 0
    def ok(value, label):
        nonlocal count
        count += 1; check(value, 'B1 bootstrap: ' + label)
    def load(name):
        p = Path(root) / 'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts' / (name + '.py')
        spec = importlib.util.spec_from_file_location('bootstrap_' + name, p)
        mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod; spec.loader.exec_module(mod); return mod
    mods = {name: load(name) for name in ('page_audit', 'psi_pull', 'url_inspection', 'gsc_pull', 'sitemap_audit', 'preflight', 'agent_surface')}
    def invoke(mod, args, fmt='json'):
        try:
            code, out, err = capture(mod.main, [*args, '--format', fmt])
            return code, json.loads(out) if fmt == 'json' and out else out, err
        except BaseException as exc: return 'escaped', {}, type(exc).__name__
    empty = Path(workspace) / 'empty.txt'; empty.write_text(' # comment\n\n')
    invalid = Path(workspace) / 'invalid.txt'; invalid.write_bytes(b'\xff\xfe')
    missing = Path(workspace) / 'missing.txt'
    good = Path(workspace) / 'urls.txt'; good.write_text('https://example.invalid/a\nhttps://example.invalid/a\nhttps://example.invalid/b\n')
    for name, args, flag in [('page_audit', [], '--url-list'), ('psi_pull', [], '--urls-file'), ('url_inspection', ['--site', 'sc-domain:example.invalid'], '--urls-file')]:
        mod = mods[name]
        for file, requested in ((missing, None), (invalid, None), (empty, 0)):
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.object(mod, 'fetch' if name != 'url_inspection' else 'inspect', side_effect=AssertionError('no resolved inputs must not fetch')))
                if name == 'url_inspection': stack.enter_context(patch.object(mod, 'access_token', return_value='offline-fixture'))
                code, data, err = invoke(mod, [*args, flag, str(file)])
            try: records = coverage_records(data)
            except ValueError: records = []
            ok(code == 1 and bool(records), name + ' unresolved list emits existing JSON carrier')
            if records:
                cov = records[0]
                ok(cov['requested'] == requested and cov['attempted'] == cov['returned'] == 0 and cov['dropped'] == (None if requested is None else 0) and cov['state'] != 'complete', name + ' unknown population is not known empty')
                if name == 'page_audit': ok(isinstance(data, list) and all(row.get('record_type') == 'input_error' and row.get('url') == '' for row in data), 'page error rows are typed input resolution, not observed pages')
    page = mods['page_audit']
    for file in (missing, invalid):
        code, data, _ = invoke(page, ['--file', str(file)])
        ok(code == 1 and isinstance(data, list) and data and data[0].get('record_type') == 'input_error' and data[0]['coverage']['requested'] == data[0]['coverage']['attempted'] == 1 and data[0]['coverage']['returned'] == 0, 'local HTML open/decode failure is one attempted local input')
    psi = mods['psi_pull']; valid_psi = {'lighthouseResult': {'categories': {'performance': {'score': .8}}}}
    with patch.object(psi, 'fetch', return_value=valid_psi) as fetched:
        code, data, _ = invoke(psi, ['--url', 'https://example.invalid/a', '--url', 'https://example.invalid/a', '--urls-file', str(invalid)])
    ok(code == 0 and isinstance(data, dict) and len(data.get('results', [])) == fetched.call_count == 2 and data.get('coverage', {}).get('requested') is None and data['coverage']['returned'] == 2, 'PSI retains explicit duplicates when optional list is unreadable')
    ui = mods['url_inspection']
    for token in ('', None):
        with patch.object(ui, 'access_token', return_value=token), patch.object(ui, 'inspect', side_effect=AssertionError('no credentials')):
            code, data, _ = invoke(ui, ['--site', 'sc-domain:example.invalid', '--urls', 'https://example.invalid/a', 'https://example.invalid/a', 'https://example.invalid/b', '--max-urls', '1'])
        cov = data.get('coverage', {}) if isinstance(data, dict) else {}
        ok(code == 1 and cov.get('requested') == 2 and cov.get('attempted') == cov.get('returned') == 0 and cov.get('dropped') == 2 and data.get('inspected') == 0 and data.get('not_inspected') == 2, 'Inspection dedup/cap plus absent credentials excludes selected inputs before attempt')
    with patch.object(ui, 'access_token', return_value='offline'), patch.object(ui, 'inspect', return_value={'inspectionResult': {'indexStatusResult': {'verdict': 'PASS'}}}) as inspected, patch.object(ui.time, 'sleep'):
        code, data, _ = invoke(ui, ['--site', 'sc-domain:example.invalid', '--urls', 'https://example.invalid/a', 'https://example.invalid/a', '--urls-file', str(missing)])
    ok(code == 0 and inspected.call_count == 1 and data.get('coverage', {}).get('requested') is None and data['coverage']['attempted'] == data['coverage']['returned'] == 1, 'Inspection preserves explicit deduplicated results beside unknown list')
    gsc = mods['gsc_pull']
    for token in ('', None):
        with patch.object(gsc, 'access_token', return_value=token), patch.object(gsc, 'call', side_effect=AssertionError('no credentials')):
            code, data, _ = invoke(gsc, ['--site', 'sc-domain:example.invalid'])
        records = data.get('coverage_by_unit', {}) if isinstance(data, dict) else {}; cov = records.get('api_request', {})
        ok(code == 1 and cov.get('requested') == cov.get('dropped') == 6 and cov.get('attempted') == cov.get('returned') == 0 and all(records.get(name + '_row', {}).get('requested') is None for name in ('date', 'query', 'page', 'query_page')), 'GSC missing credentials exclude six known requests, provider populations stay unknown')
    for fmt in ('json', 'text'):
        with patch.object(gsc, 'access_token', return_value='offline'), patch.object(gsc, 'call', return_value={'siteEntry': []}) as calls:
            code, data, _ = invoke(gsc, ['--list'], fmt)
        ok(code == 0 and calls.call_count == 1, 'explicit empty property listing succeeds in ' + fmt)
        if fmt == 'json' and isinstance(data, dict): ok(data.get('mode') == 'list' and data.get('sites') == [] and data.get('coverage_by_unit', {}).get('api_request', {}).get('requested') == 1, 'list mode has its own one-operation carrier')
    with patch.object(gsc, 'access_token', side_effect=AssertionError('usage must precede credentials')):
        code, data, _ = invoke(gsc, [])
    ok(code == 1 and data == '', 'missing GSC site without explicit list is a no-network usage boundary')
    for name, args in [('psi_pull', []), ('sitemap_audit', []), ('preflight', [])]:
        mod = mods[name]
        code, data, _ = invoke(mod, args)
        try: records = coverage_records(data)
        except ValueError: records = []
        ok(code == 1 and records and all(r['requested'] == r['attempted'] == r['returned'] == r['dropped'] == 0 and r['state'] == 'partial' for r in records), name + ' parsed no-input invocation reports zero attempts with explicit gap')
        if name == 'preflight' and isinstance(data, dict): ok(data.get('probes') == [] and all(row['status'] == 'unlooked' for row in data.get('coverage', [])), 'preflight no-input does not invent Python/ADC/network or track observations')
    for name in ('gsc_pull', 'url_inspection'):
        mod = mods[name]
        for effect in (subprocess.CalledProcessError(1, ['gcloud'], stderr='private ADC diagnostic'), subprocess.TimeoutExpired(['gcloud'], 20), UnicodeError('private ADC diagnostic')):
            with patch.object(mod.subprocess, 'run', side_effect=effect):
                code, data, err = invoke(mod, ['--site', 'sc-domain:example.invalid'] + (['--urls', 'https://example.invalid/a'] if name == 'url_inspection' else []))
            ok(code == 1 and isinstance(data, dict) and 'private ADC diagnostic' not in json.dumps(data) + err, name + ' bounded credential failure produces no raw secret diagnostic')
    with patch.object(ui, 'access_token', return_value=''), patch.object(ui, 'inspect', side_effect=AssertionError('no credentials')):
        code, data, _ = invoke(ui, ['--site', 'sc-domain:example.invalid', '--urls', 'https://example.invalid/a', 'https://example.invalid/a', 'https://example.invalid/b', '--max-urls', '1', '--urls-file', str(missing)])
    ok(code == 1 and data['coverage']['requested'] is None and data['coverage']['dropped'] is None and data['coverage']['attempted'] == 0 and data['not_inspected'] == 2, 'unknown list plus dedup/cap/ADC keeps known exclusions separate from unknown total')
    for envelope, observed, kept in [({'siteEntry': [42]}, False, 0), ({'siteEntry': [42, {'siteUrl': 'sc-domain:example.invalid'}]}, False, 1), ({'siteEntry': []}, True, 0)]:
        with patch.object(gsc, 'access_token', return_value='offline'), patch.object(gsc, 'call', return_value=envelope):
            code, data, _ = invoke(gsc, ['--list'])
        ok(data['properties_observed'] is observed and len(data['sites']) == kept and code == (0 if observed or kept else 1) and data['coverage_by_unit']['api_request']['state'] == ('complete' if observed else 'partial'), 'list-only typed empty differs from malformed membership, preserving valid siblings')
    # Mutating unknown input population to the known prefix must be observable.
    source = (Path(root) / 'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/psi_pull.py').read_text()
    needle = 'None if unknown_input else len(urls)'
    ok(source.count(needle) == 1, 'false-known-input mutation selector unique')
    mutant_path = Path(workspace) / 'psi-false-known.py'; mutant_path.write_text(source.replace(needle, 'len(urls)', 1))
    spec = importlib.util.spec_from_file_location('psi_false_known', mutant_path); mutant = importlib.util.module_from_spec(spec); spec.loader.exec_module(mutant)
    with patch.object(mutant, 'fetch', return_value=valid_psi):
        code, data, _ = invoke(mutant, ['--url', 'https://example.invalid/a', '--urls-file', str(missing)])
    ok(code == 0 and data['coverage']['requested'] is not None, 'independent unknown-population assertion detects false-known source mutation')
    # Both renderers and parser boundaries remain explicit and make no network calls.
    for name, args, fmt in [
        ('page_audit', ['--url-list', str(missing)], 'markdown'),
        ('psi_pull', [], 'markdown'),
        ('url_inspection', ['--site', 'sc-domain:example.invalid'], 'markdown'),
        ('gsc_pull', ['--site', 'sc-domain:example.invalid'], 'text'),
        ('sitemap_audit', [], 'markdown'), ('preflight', [], 'markdown'),
    ]:
        mod = mods[name]
        with contextlib.ExitStack() as stack:
            if hasattr(mod, 'access_token'): stack.enter_context(patch.object(mod, 'access_token', side_effect=SystemExit('unavailable fixture')))
            code, out, _ = invoke(mod, args, fmt)
        ok(code == 1 and 'Collector coverage' in out and ('partial' in out or 'unknown' in out), name + ' default bootstrap report carries explicit gap')
    for name in ('page_audit', 'url_inspection', 'agent_surface'):
        code, out, err = invoke(mods[name], [])
        ok(code == 'escaped' and err == 'SystemExit', name + ' required-argument parser remains outside collection')
    pre = mods['preflight']
    with patch.object(pre, 'check_python', side_effect=AssertionError('no input means no local probe')), patch.object(pre, 'check_gcloud', side_effect=AssertionError('no input means no ADC')):
        code, _, _ = invoke(pre, [])
    ok(code == 1, 'no-input preflight skips even Python prerequisite probe')
    for name in ('gsc_pull', 'url_inspection'):
        mod = mods[name]
        with patch.object(mod.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, stdout='  ', stderr='')) as proc:
            try: mod.access_token()
            except SystemExit: refused = True
            else: refused = False
        ok(refused and proc.call_args.kwargs.get('timeout') == 20, name + ' empty ADC output refused with explicit process timeout')
    # Isolated subprocesses: fake gcloud only, and sitecustomize denies every
    # HTTP entry point before the copied script imports. No live profile is used.
    import os
    copies = Path(workspace) / 'copied'; copies.mkdir()
    bindir = Path(workspace) / 'fake-bin'; bindir.mkdir()
    guarddir = Path(workspace) / 'guard'; guarddir.mkdir()
    adc_marker = Path(workspace) / 'adc-count'; network_marker = Path(workspace) / 'network-count'
    fake = bindir / 'gcloud'
    fake.write_text('#!' + sys.executable + '\nfrom pathlib import Path\nimport sys\np=Path(' + repr(str(adc_marker)) + ')\np.write_text((p.read_text() if p.exists() else "")+"1")\nsys.stderr.write("private ADC fixture")\nsys.exit(1)\n'); fake.chmod(0o755)
    (guarddir / 'sitecustomize.py').write_text('import urllib.request\nfrom pathlib import Path\ndef deny(*a,**k):\n Path(' + repr(str(network_marker)) + ').write_text("attempt")\n raise AssertionError("HTTP denied by isolated bootstrap fixture")\nurllib.request.urlopen=deny\nurllib.request.OpenerDirector.open=deny\n')
    env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ.get('PATH', ''), PYTHONPATH=str(guarddir))
    cases = [
        ('page_audit', ['--url-list', str(invalid)], None, 0),
        ('page_audit', ['--file', str(missing)], 1, 1),
        ('psi_pull', ['--urls-file', str(invalid)], None, 0),
        ('url_inspection', ['--site', 'sc-domain:example.invalid', '--urls', 'https://example.invalid/a', '--urls-file', str(invalid)], None, 0),
        ('gsc_pull', ['--site', 'sc-domain:example.invalid'], 6, 0),
        ('gsc_pull', ['--list'], 1, 0), ('sitemap_audit', [], 0, 0), ('preflight', [], 0, 0),
    ]
    for name, args, expected_requested, expected_attempted in cases:
        copied = copies / (name + '.py')
        copied.write_bytes((Path(root) / 'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts' / (name + '.py')).read_bytes())
        for fmt in ('json', 'text' if name == 'gsc_pull' else 'markdown'):
            proc = LOCAL_RUN([sys.executable, '-B', str(copied), *args, '--format', fmt], cwd=copies, env=env, capture_output=True, text=True, timeout=10)
            ok(proc.returncode == 1 and 'private ADC fixture' not in proc.stdout + proc.stderr and 'HTTP denied' not in proc.stdout + proc.stderr, name + ' actual copied bootstrap ' + fmt + ' preserves report without private diagnostic')
            if fmt == 'json':
                records = coverage_records(json.loads(proc.stdout))
                selected = next((r for r in records if r['unit'] == 'api_request'), records[0])
                ok(selected['requested'] == expected_requested and selected['attempted'] == expected_attempted and selected['returned'] == 0, name + ' copied JSON exact bootstrap denominator')
    ok(not network_marker.exists(), 'copied bootstrap invocations attempted zero HTTP operations')
    ok(adc_marker.read_text() == '111111', 'only selected Inspection and explicit GSC modes invoked fake ADC in two formats')
    print(f'B1 bootstrap: {count} controls')


def run(check, root, workspace):
    # Deny credentials and provider transport before entering ANY main. Individual
    # fixtures may override these only with explicit local return values/errors.
    import urllib.request
    with patch.object(subprocess, 'run', side_effect=AssertionError('fixture attempted real subprocess')), patch.object(urllib.request, 'urlopen', side_effect=AssertionError('fixture attempted provider transport')):
        return _run(check, root, workspace)


if __name__ == '__main__':
    import residue
    failures = []; residue.open_case('bootstrap-contract'); work = residue.workspace('bootstrap-contract')
    run(lambda cond, label: failures.append(label) if not cond else None, Path(__file__).resolve().parents[1], work)
    if not failures: residue.close_case('bootstrap-contract')
    residue.report()
    if failures:
        print('FAIL: bootstrap contract\n' + '\n'.join('  - ' + item for item in failures)); raise SystemExit(1)
    print('PASS: bootstrap contract')
