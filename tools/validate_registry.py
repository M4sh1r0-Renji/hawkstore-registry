#!/usr/bin/env python3
"""Dependency-free structural validation for the Hawkstore registry."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)+$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
SHA_RE = re.compile(r"^[A-Fa-f0-9]{64}$")
STEAM_ID_RE = re.compile(r"^7656119[0-9]{10}$")
REQUIRED = {"schemaVersion", "id", "name", "version", "author", "owners", "description", "categories", "game", "bepInEx", "plugin", "release"}


def load(path: Path):
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def main() -> int:
    errors: list[str] = []
    categories = set(load(ROOT / "categories.json")["categories"])
    index = load(ROOT / "index.json")
    index_ids = [item["id"] for item in index.get("packages", [])]
    if len(index_ids) != len(set(index_ids)):
        errors.append("index.json contains duplicate package IDs")

    live_ids: list[str] = []
    for path in sorted((ROOT / "mods").glob("*/manifest.json")):
        try:
            manifest = load(path)
        except Exception as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        missing = REQUIRED - manifest.keys()
        if missing:
            errors.append(f"{path}: missing fields: {', '.join(sorted(missing))}")
            continue
        package_id = manifest["id"]
        live_ids.append(package_id)
        if path.parent.name != package_id:
            errors.append(f"{path}: directory must match id '{package_id}'")
        if not ID_RE.fullmatch(package_id):
            errors.append(f"{path}: invalid package id")
        if not SEMVER_RE.fullmatch(manifest["version"]):
            errors.append(f"{path}: version must be semantic versioning")
        if manifest["schemaVersion"] != 1:
            errors.append(f"{path}: unsupported schemaVersion")
        unknown = set(manifest["categories"]) - categories
        if unknown:
            errors.append(f"{path}: unknown categories: {', '.join(sorted(unknown))}")
        if not manifest["owners"]:
            errors.append(f"{path}: at least one owner is required")
        author = manifest.get("author", {})
        if not STEAM_ID_RE.fullmatch(author.get("steamId", "")):
            errors.append(f"{path}: author.steamId must be a SteamID64")
        verification = author.get("steamVerification", {})
        if verification.get("provider") != "steam-openid":
            errors.append(f"{path}: author.steamVerification.provider must be steam-openid")
        if verification.get("status") not in {"pending", "verified"}:
            errors.append(f"{path}: author.steamVerification.status must be pending or verified")
        if verification.get("status") == "verified" and not verification.get("verifiedAt"):
            errors.append(f"{path}: verified Steam identities require verifiedAt")
        release = manifest.get("release")
        if release and not SHA_RE.fullmatch(release.get("sha256", "")):
            errors.append(f"{path}: release.sha256 must contain 64 hex characters")
        plugin = manifest.get("plugin", {})
        for field in ("installDirectory", "entryDll"):
            value = plugin.get(field, "")
            if not value or "/" in value or "\\" in value:
                errors.append(f"{path}: plugin.{field} must be a single path component")

    if len(live_ids) != len(set(live_ids)):
        errors.append("mods contains duplicate package IDs")
    if set(index_ids) != set(live_ids):
        errors.append("index.json package IDs do not match mods/*/manifest.json")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Registry valid: {len(live_ids)} live package(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
