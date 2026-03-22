# StrikeFrame Fixtures

Fixture policy:
- Small text manifests and fixture metadata may live in this repo.
- Generated calibration renders do **not** belong in the repo by default.
- Use `/mnt/raid/Data/tmp/openclaw-builds/katya/strikeframe-vision-phase1/` for scratch renders, comparisons, and calibration batches.
- Only promote a binary fixture into the repo if it is small, stable, intentionally permanent, and required for regression coverage.

Benchmark policy:
- Good fixtures should come from external, highly qualified paid/social examples and research.
- Internal content may be stored as known-bad or diagnostic fixtures, but not as gold-standard references.
