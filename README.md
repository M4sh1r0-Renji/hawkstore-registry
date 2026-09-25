# Hawkstore Registry

[简体中文](README.zh-CN.md) · English

The public package registry consumed by the Hawkstore desktop client. This repository stores metadata and a searchable index; plugin DLL and ZIP payloads belong in immutable GitHub Release assets.

## Layout

```text
index.json
categories.json
schemas/
  manifest.schema.json
  index.schema.json
mods/
  <package-id>/
    manifest.json
    README.md
examples/
tools/validate_registry.py
```

## Submission workflow

1. Package the mod as a ZIP using the Hawkstore package layout.
2. Validate the manifest and package locally with `hawkstore-publishing`.
3. Add `mods/<package-id>/manifest.json` and `README.md` on a submission branch.
4. Open a pull request using the publish template.
5. GitHub Actions validates IDs, categories, versions, ownership, hashes, and index consistency.
6. A maintainer reviews first-time publishers. Accepted versions are immutable.
7. The publishing pipeline creates a GitHub Release and updates `index.json`.

Run the repository check locally:

```bash
python tools/validate_registry.py
```

## Security

Registry acceptance is not a guarantee that a plugin is safe. BepInEx plugins execute arbitrary code. Packages should expose source code when possible, use SHA-256 verification, and remain subject to manual review and malware scanning.
