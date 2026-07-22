# GitHub Repository Setup Options

## Recommended repository settings

| Setting | Choose |
|---|---|
| Owner | `SheeshDarth` |
| Repository name | `vyomaguard-phm` |
| Display name | `VymoaGaurd PHM` |
| Visibility | Public portfolio repository |
| Default branch | `main` |
| Description | Explainable space mission-assurance prototype for conjunction risk, telemetry anomaly detection, and deterministic operator triage. |
| Issues | Enabled |
| Discussions | Disabled initially; enable later if the project gains users |
| Wiki | Disabled; documentation already lives in `docs/` |
| Projects | Optional; enable only when tracking work outside the roadmap |
| Actions | Enabled; CI is defined in `.github/workflows/ci.yml` |
| Security policy | Enabled via `SECURITY.md` |
| License | MIT, already committed locally |

## Important GitHub UI choice

Because this local repository already contains the README, `.gitignore`, and `LICENSE`, do **not** select GitHub's “Initialize this repository with a README,” `.gitignore`, or license options. Choose none of those duplicate initializers when creating the repository from the local checkout.

## Recommended topics

```text
aerospace
space-mission-assurance
conjunction-risk
space-situational-awareness
telemetry-anomaly-detection
explainable-ai
predictive-health-monitoring
python
scikit-learn
streamlit
```

## Command-line creation

From the new project folder, after reviewing the staged files:

```powershell
gh repo create SheeshDarth/vyomaguard-phm `
  --public `
  --description "Explainable space mission-assurance prototype for conjunction risk, telemetry anomaly detection, and deterministic operator triage." `
  --source . `
  --remote origin `
  --push
```

## After creation

1. Add the repository topics listed above.
2. Enable private vulnerability reporting when available.
3. Add branch protection to `main` after CI has run successfully:
   - require pull requests;
   - require the CI check;
   - block force pushes;
   - require conversation resolution.
4. Create the first release only after the dataset label audit and acceptance matrix are complete.
5. Keep downloaded datasets and generated reports outside Git.

## License choice

MIT is the current recommendation for a public portfolio prototype because it permits reuse with minimal friction. If the project later incorporates third-party code or institutional requirements, review compatibility before changing the license.
