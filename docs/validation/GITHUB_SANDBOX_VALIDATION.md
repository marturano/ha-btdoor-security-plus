# GitHub Sandbox Validation

The project provides two workflows:

- `GitHub Sandbox Validation`: read-only mandatory validation for pushes, pull requests and manual runs.
- `Ruff Remediation`: manual workflow that applies supported Ruff fixes, formats the code, runs every release gate and commits only if all checks pass.

## Mandatory release sequence
1. Run Ruff Remediation when lint or formatting errors exist.
2. Review the generated commit and evidence artifact.
3. Run GitHub Sandbox Validation on the resulting commit.
4. Require all repository and publication workflows to pass.
5. Import the evidence into release readiness and the Release Decision Engine.
6. Generate an RC or Final package only after the required Quality Scale level is still demonstrated.

## Local equivalent

```bash
bash tools/validation/github_sandbox_validate.sh check
```

To apply supported automatic remediation in an isolated branch:

```bash
bash tools/validation/github_sandbox_validate.sh fix
```

The `fix` mode is not a release approval. A subsequent clean `check` execution is required.
