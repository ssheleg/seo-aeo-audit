#!/usr/bin/env bash
# The documentation gate. Runs exactly the checks the propagation matrix in
# docs/DOCMAP.md names, so the gate cannot drift away from what it claims to
# enforce. A project whose gate starts red teaches everyone that it is noise.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 test/validate.py
python3 test/plant_guard_test.py
python3 test/test_page_audit.py
python3 test/test_url_inspection.py
python3 test/test_collectors.py
python3 test/test_agent_surface.py
python3 test/test_output_contracts.py
# Last on purpose: its final case reads the TMPDIR every suite above shared, so a
# leak anywhere in the gate shows up in the gate's own output.
python3 test/residue_test.py
echo "OK: structure, doctrine guards and behaviour tests all pass"
