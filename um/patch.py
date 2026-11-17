"""Read-only Patch catalog discovery; no login, project writes, compute, or downloads.

    um patch assets "smoke" --limit 5
    um patch repos "elements"
    um patch blender-costs

Results are external research candidates, not verified game assets.
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request

BASE = "https://patch.gg/api/v1"
MAX_RESPONSE = 2_000_000


def public_get(path: str, params: dict | None = None) -> dict:
    """Use only hard-coded public GET paths; never attach credentials."""
    allowed = path in ("/assets/search", "/repos/search", "/blender")
    is_detail = re.fullmatch(r"/assets/[A-Za-z0-9%._~-]+", path) is not None
    if not (allowed or is_detail):
        raise ValueError("Only public catalog read endpoints are allowed")
    query = "?" + urllib.parse.urlencode(params) if params else ""
    request = urllib.request.Request(
        BASE + path + query,
        headers={"Accept": "application/json", "User-Agent": "universal-modder-readonly/0.1"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(MAX_RESPONSE + 1)
    if len(data) > MAX_RESPONSE:
        raise ValueError("Patch API response exceeds size limit")
    obj = json.loads(data)
    if not isinstance(obj, dict):
        raise ValueError("Patch API returned a non-object")
    return obj


def asset_candidates(payload: dict) -> dict:
    """Keep provenance and licensing visible; never imply use is authorized."""
    assets = []
    for item in payload.get("hits", []):
        if not isinstance(item, dict):
            continue
        fit = item.get("fit") if isinstance(item.get("fit"), dict) else {}
        prep = item.get("prep") if isinstance(item.get("prep"), dict) else {}
        assets.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "asset_type": item.get("type"),
            "origin": item.get("source"),
            "license_spdx": item.get("license"),
            "ai_generated": item.get("ai"),
            "prep_state": prep.get("state"),
            "triangles": fit.get("triangles"),
            "size_mb": fit.get("mb"),
            "variant": fit.get("variant"),
            "evidence_state": "EXTERNAL_CANDIDATE",
            "local_byte_verified": False,
            "in_game_verified": False,
        })
    return {
        "source": "patch-public-assets-api",
        "api_path": "/assets/search",
        "candidate_only": True,
        "total": payload.get("total"),
        "items": assets,
        "untrusted_fields": payload.get("untrusted_fields", []),
    }


def asset_detail(asset_id: str) -> dict:
    """Fetch provenance, immutable file hashes, variant facts and attribution."""
    if (not asset_id or len(asset_id) > 500 or "://" in asset_id
            or any(seg in (".", "..") for seg in asset_id.split("/"))):
        raise ValueError("Invalid asset id")
    payload = public_get("/assets/" + urllib.parse.quote(asset_id, safe=""))
    license_data = payload.get("license") if isinstance(payload.get("license"), dict) else {}
    variants = []
    for variant in payload.get("variants", []):
        if not isinstance(variant, dict):
            continue
        variants.append({
            "name": variant.get("name"),
            "runtimes": variant.get("runtimes", []),
            "facts": variant.get("facts", {}),
            "size_bytes": variant.get("size"),
            "files": [
                {key: file.get(key) for key in ("name", "role", "sha256", "size", "content_type")}
                for file in variant.get("files", []) if isinstance(file, dict)
            ],
        })
    return {
        "source": "patch-public-asset-detail-api",
        "asset_id": payload.get("id"),
        "title": payload.get("title"),
        "license": {key: license_data.get(key) for key in ("spdx", "name", "url", "duties", "evidence")},
        "credit": payload.get("credit"),
        "origin": payload.get("source"),
        "variants": variants,
        "untrusted_fields": payload.get("untrusted_fields", []),
        "evidence_state": "EXTERNAL_CANDIDATE",
        "local_byte_verified": False,
        "in_game_verified": False,
        "downloaded": False,
    }


def run_asset_detail(args) -> None:
    print(json.dumps(asset_detail(args.asset_id), indent=2, sort_keys=True))


def repo_candidates(payload: dict) -> dict:
    result = []
    for item in payload.get("data", []):
        if isinstance(item, dict):
            result.append({
                "handle": item.get("handle"),
                "engine": item.get("engine"),
                "kind": item.get("kind"),
                "code_license": item.get("code_license"),
                "art_license": item.get("art_license"),
                "clone_url": item.get("clone_url"),
                "evidence_state": "EXTERNAL_CANDIDATE",
                "build_verified": False,
            })
    return {
        "source": "patch-public-repos-api",
        "api_path": "/repos/search",
        "candidate_only": True,
        "items": result,
        "untrusted_fields": payload.get("untrusted_fields", []),
    }


def run_assets(args) -> None:
    print(json.dumps(asset_candidates(public_get("/assets/search", {
        "q": args.query, "limit": args.limit, "license": args.license,
    })), indent=2, sort_keys=True))


def run_repos(args) -> None:
    print(json.dumps(repo_candidates(public_get("/repos/search", {
        "q": args.query, "limit": args.limit,
    })), indent=2, sort_keys=True))


def run_blender(args) -> None:
    payload = public_get("/blender")
    print(json.dumps({
        "source": "patch-public-blender-api",
        "api_path": "/blender",
        "candidate_only": True,
        "prices": payload.get("prices", {}),
        "gpus": payload.get("gpus", []),
        "blender_versions": payload.get("blender_versions", []),
        "engines": payload.get("engines", []),
        "compute_started": False,
    }, indent=2, sort_keys=True))


def register(sub) -> None:
    p = sub.add_parser("patch", help="Read-only Patch asset, repo and Blender capability discovery")
    inner = p.add_subparsers(dest="patch_command")
    a = inner.add_parser("assets", help="Search assets without downloading or importing")
    a.add_argument("query")
    a.add_argument("--limit", type=int, choices=range(1, 101), metavar="1-100", default=10)
    a.add_argument("--license", default="safe", help="Patch license filter; review each returned license")
    a.set_defaults(func=run_assets)
    d = inner.add_parser("asset", help="Read one asset license, credit and variant hashes")
    d.add_argument("asset_id", help="Opaque Patch asset id, e.g. kenney:blaster-kit/smoke.glb")
    d.set_defaults(func=run_asset_detail)
    r = inner.add_parser("repos", help="Find public Patch source repositories")
    r.add_argument("query")
    r.add_argument("--limit", type=int, choices=range(1, 101), metavar="1-100", default=10)
    r.set_defaults(func=run_repos)
    b = inner.add_parser("blender-costs", help="Read Blender machine and credit pricing (no compute)")
    b.set_defaults(func=run_blender)
