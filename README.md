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
tools/verify_release_assets.py
```

The first live entry is `com.usami.dynamicterraincraters` (Dynamic Terrain Craters 1.9.0). Its ZIP is distributed as a GitHub Release asset and the registry stores the immutable URL, byte size, and SHA-256 digest.

## Submission workflow

1. Package the mod as a ZIP using the Hawkstore package layout.
2. Validate the manifest and package locally with `hawkstore-publishing`.
3. Add `mods/<package-id>/manifest.json` and `README.md` on a submission branch.
4. Open a pull request using the publish template.
5. The publishing service verifies the submitted SteamID64 through a Steam OpenID callback. Author-submitted manifests remain `pending`; only the Registry service can promote the identity to `verified`.
6. GitHub Actions validates IDs, categories, versions, ownership, Steam identity fields, index consistency, and the live Release asset's size and SHA-256.
7. A maintainer reviews first-time publishers. Accepted versions are immutable.
8. The publishing pipeline creates a GitHub Release and updates `index.json`.

Run the repository check locally:

```bash
python tools/validate_registry.py
python tools/verify_release_assets.py
```

## Security

Registry acceptance is not a guarantee that a plugin is safe. BepInEx plugins execute arbitrary code. Packages should expose source code when possible, use SHA-256 verification, and remain subject to manual review and malware scanning.
