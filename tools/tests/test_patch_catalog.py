"""Offline regression checks for the opt-in read-only Patch catalog adapter."""
import io
import json
from unittest.mock import patch as mock_patch

import pytest

from um import patch as patch_api
from um.cli import GROUPS


def test_cli_registration_and_write_path_rejection():
    assert "patch" in GROUPS
    with pytest.raises(ValueError, match="Only public"):
        patch_api.public_get("/blender/sessions", {"wait": 60})
    with pytest.raises(ValueError):
        patch_api.public_get("/projects")


def test_get_is_public_unauthed_and_bounded():
    seen = {}
    def urlopen(request, timeout=0):
        seen["method"] = request.get_method()
        seen["url"] = request.full_url
        seen["authorization"] = request.get_header("Authorization")
        seen["timeout"] = timeout
        return io.BytesIO(json.dumps({"hits": []}).encode("utf-8"))
    with mock_patch.object(patch_api.urllib.request, "urlopen", urlopen):
        result = patch_api.public_get("/assets/search", {"q": "stone wall", "limit": 3})
    assert result == {"hits": []}
    assert seen["method"] == "GET"
    assert seen["authorization"] is None
    assert seen["url"].startswith("https://patch.gg/api/v1/assets/search?")
    assert "stone+wall" in seen["url"]
    assert 0 < seen["timeout"] <= 20


def test_asset_candidates_preserve_license_and_verification_boundary():
    result = patch_api.asset_candidates({
        "total": 1,
        "untrusted_fields": ["hits.title"],
        "hits": [{
            "id": "kenney:smoke.glb", "title": "Smoke", "source": "Kenney",
            "type": "model", "license": "CC0-1.0", "ai": False,
            "prep": {"state": "ready"}, "fit": {"triangles": 380, "mb": 0.02, "variant": "web"},
        }],
    })
    assert result["candidate_only"]
    assert result["untrusted_fields"] == ["hits.title"]
    a = result["items"][0]
    assert a["license_spdx"] == "CC0-1.0"
    assert a["triangles"] == 380
    assert a["local_byte_verified"] is False
    assert a["in_game_verified"] is False
    assert a["evidence_state"] == "EXTERNAL_CANDIDATE"


def test_repo_candidates_never_claim_build():
    result = patch_api.repo_candidates({
        "data": [{"handle": "patch/elements", "engine": "three.js",
                  "code_license": "MIT", "clone_url": "https://git.patch.gg/patch/elements.git"}]
    })
    assert result["candidate_only"]
    assert result["items"][0]["build_verified"] is False
    assert result["items"][0]["handle"] == "patch/elements"


def test_asset_detail_keeps_license_evidence_and_hashes_without_bytes():
    record = {
        "id": "kenney:blaster-kit/smoke.glb", "title": "Smoke",
        "license": {"spdx": "CC0-1.0", "name": "CC0", "duties": [],
                    "evidence": {"where": "License.txt", "url": "https://kenney.nl"}},
        "credit": '"Smoke" by Kenney, CC0',
        "source": {"name": "Kenney", "ref": "blaster-kit/smoke.glb"},
        "variants": [{"name": "web", "size": 19968,
                      "files": [{"name": "smoke.glb", "sha256": "abc123",
                                 "size": 19968, "role": "model",
                                 "url": "https://assets.patchusercontent.com/blob"}]}],
    }
    with mock_patch.object(patch_api, "public_get", return_value=record) as get:
        result = patch_api.asset_detail("kenney:blaster-kit/smoke.glb")
    get.assert_called_once_with("/assets/kenney%3Ablaster-kit%2Fsmoke.glb")
    assert result["license"]["spdx"] == "CC0-1.0"
    assert result["credit"] == '"Smoke" by Kenney, CC0'
    assert result["variants"][0]["files"][0]["sha256"] == "abc123"
    assert "url" not in result["variants"][0]["files"][0]
    assert result["downloaded"] is False
    assert result["evidence_state"] == "EXTERNAL_CANDIDATE"


def test_asset_id_rejects_path_traversal_and_http_urls():
    for value in ("", "../secret", "kenney:/../files", "https://example.org/x"):
        with pytest.raises(ValueError):
            patch_api.asset_detail(value)
