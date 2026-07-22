# Contributing to VymoaGaurd PHM

## Before opening a change

1. Read the [PRD](docs/PRD.md), [TRD](docs/TRD.md), and [Safety and Limitations](docs/SAFETY_AND_LIMITATIONS.md).
2. Keep the domain pipeline independent from Streamlit.
3. Use public, synthetic, or de-identified data only.
4. Add or update tests for behavior changes.

## Development setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
$env:PYTHONPATH = "src"
python -m pytest
```

## Pull requests

Every pull request should explain:

- what changed and why;
- which requirements or decision-log entry it affects;
- how it was tested;
- whether model claims, thresholds, data semantics, or safety language changed.

Do not commit downloaded datasets, model checkpoints, secrets, generated reports, or real mission data.

## Commit guidance

Use concise imperative messages such as:

- `feat: add telemetry anomaly window scoring`
- `test: cover stale-input abstention`
- `docs: clarify probability claims`
