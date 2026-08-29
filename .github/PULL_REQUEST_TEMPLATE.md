## What and why

<!-- What changes, and what problem it solves. Link the issue if there is one. -->

## Evidence

<!-- Paste what you ran and what it printed. Both are required for any change. -->

```
python3 test/validate.py
python3 test/plant_guard_test.py
python3 test/test_page_audit.py
python3 test/test_url_inspection.py
python3 test/test_collectors.py
python3 test/test_agent_surface.py
python3 test/test_output_contracts.py
python3 test/test_installer.py
python3 test/residue_test.py
```

## Checklist

- [ ] Every check above passes locally
- [ ] Behavior change is reflected in `README.md` and in the skill's own docs
- [ ] `CHANGELOG.md` has an entry for this change
- [ ] If versions moved: `marketplace.json`, `plugin.json`, `package.json` and the top `CHANGELOG.md` entry all agree
- [ ] No relative links added to `cursor/rules/*.mdc` (those files get copied standalone)
