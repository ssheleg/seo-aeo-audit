#!/usr/bin/env python3
"""Read-only finite fixture for next coverage packet; never uses real transport."""
import importlib.util
from pathlib import Path
from unittest.mock import patch

root = Path(__file__).resolve().parents[3]
source = root / 'plugins/seo-aeo-audit/skills/seo-aeo-audit/scripts/agent_surface.py'
spec = importlib.util.spec_from_file_location('agent_surface_probe', source)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
calls = []

def fake(url, accept='', user_agent=mod.UA):
    calls.append((url, accept, user_agent))
    if url == 'https://example.invalid/':
        return mod.Probe(url, 200, 'text/html', '<html><body>root</body></html>')
    return mod.Probe(url, 404, 'text/plain', 'not found')

with patch.object(mod, 'fetch', side_effect=fake):
    data = mod.collect('https://example.invalid')
print({'all_fetch_invocations': len(calls), 'displayed_checks': len(data['checks']),
       'answered_displayed': data['_answered'], 'unique_request_variants': len(set(calls)),
       'coverage_present': 'coverage' in data})
