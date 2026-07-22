# Security Policy

## Scope

VymoaGaurd PHM is a local research/portfolio prototype. It is not approved for real spacecraft operations and must not receive real mission telemetry.

## Do not submit

- real mission telemetry;
- credentials, tokens, private keys, or secrets;
- sensitive orbital data;
- operational maneuver plans;
- proprietary dataset files.

## Reporting a vulnerability

Please do not open a public issue for a suspected secret exposure or sensitive-data problem. Use GitHub's private vulnerability reporting once enabled for the repository, or contact the repository owner privately through the GitHub account that owns the project.

Reports should include the affected file/component, reproduction steps using synthetic data only, impact, and a suggested mitigation where possible.

## Safe development requirements

- Keep downloaded datasets outside version control.
- Run tests before publishing changes.
- Preserve validation findings, abstention behavior, and safety disclaimers.
- Never add autonomous maneuver or command-generation logic without a separate safety review.
