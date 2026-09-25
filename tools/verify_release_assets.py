#!/usr/bin/env python3
"""Verify that every published package asset is reachable and immutable."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNK_SIZE = 1024 * 1024


def load(path: Path):
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def verify(manifest_path: Path) -> list[str]:
    errors: list[str] = []
    manifest = load(manifest_path)
    release = manifest.get("release") or {}
    url = release.get("downloadUrl", "")
    expected_size = release.get("size")
    expected_sha = str(release.get("sha256", "")).upper()

    if not url.startswith("https://"):
        return [f"{manifest_path}: release.downloadUrl must use HTTPS"]
    if not isinstance(expected_size, int) or expected_size <= 0:
        return [f"{manifest_path}: release.size must be a positive integer"]

    request = urllib.request.Request(url, headers={"User-Agent": "Hawkstore-registry-validator/1.0"})
    digest = hashlib.sha256()
    actual_size = 0
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            final_url = response.geturl()
            if not final_url.startswith("https://"):
                errors.append(f"{manifest_path}: asset redirected to a non-HTTPS URL")
            while chunk := response.read(CHUNK_SIZE):
                actual_size += len(chunk)
                if actual_size > expected_size:
                    errors.append(
                        f"{manifest_path}: asset is larger than declared size "
                        f"({actual_size} > {expected_size})"
                    )
                    return errors
                digest.update(chunk)
    except (urllib.error.URLError, TimeoutError) as exc:
        return [f"{manifest_path}: asset download failed: {exc}"]

    if actual_size != expected_size:
        errors.append(f"{manifest_path}: asset size mismatch ({actual_size} != {expected_size})")
    actual_sha = digest.hexdigest().upper()
    if actual_sha != expected_sha:
        errors.append(f"{manifest_path}: asset SHA-256 mismatch ({actual_sha} != {expected_sha})")
    return errors


def main() -> int:
    errors: list[str] = []
    manifests = sorted((ROOT / "mods").glob("*/manifest.json"))
    for manifest_path in manifests:
        errors.extend(verify(manifest_path))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Release assets verified: {len(manifests)} package(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
