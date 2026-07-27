# Release Publication Runbook

## Preparation

Freeze scope, pass all gates, update versions, CHANGELOG, release dossier, handoff and checksums.

## GitHub

Push reviewed commits, create signed/annotated tag where supported, push tag, create GitHub Release, attach archive and checksum, verify links and installation instructions.

## HACS

Run validation, install from a clean Home Assistant instance, test upgrade and rollback, verify repository indexing and release visibility.

## Maintenance

Keep supported branches synchronized, issue hotfixes from the correct base, never rewrite published tags, document deprecations, archive superseded instructions and update the handoff after every publication action.
