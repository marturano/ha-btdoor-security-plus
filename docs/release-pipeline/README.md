# Release Pipeline & Distribution

This canonical area defines the reproducible release process for BTDoor Security+.

The pipeline separates **artifact construction** from **publication approval**. A structurally valid candidate can be built with `--force`, but it remains explicitly non-publishable until the Release Decision and Release Certification gates are approved.

## Commands

```bash
python tools/distribution/release_pipeline.py check
python tools/distribution/release_pipeline.py build
python tools/distribution/release_pipeline.py build --force
python tools/distribution/release_pipeline.py verify
```

Artifacts are written to `dist/` and include the ZIP, SHA-256 checksum and machine-readable release manifest.
