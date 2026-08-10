# Pipeline run records

One file per `task-pipeline` run, named for the date it started. These are
**records of a finished run**, not configuration.

`pipeline.json` used to sit in the repository root, where a file with that name
reads as current config. It described the 2026-08-05 run and carried that run's
decisions — "No deploy this run by operator decision", a stage-6 gate naming two of
the four test files — so the next agent to open it inherited a closed run's choices
as policy. Moving it here is the fix: the root has no file that looks like a
standing configuration when it is a diary entry.

The gate a run must actually pass is `scripts/check-docs.sh`, and the four commands
it runs are named in `CONTRIBUTING.md` and reconciled by `test/validate.py`.
