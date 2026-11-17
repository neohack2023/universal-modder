"""Synthetic NPC seams: no game, network, engine or voice dependence."""
import copy
import json
from pathlib import Path

import pytest
from um import npc
from um.cli import GROUPS


def scene(*, dist=3.0, behind=False, named=True):
    return {
        "player": {"position": [0, 0, 0], "forward": [0, 0, 1]},
        "npcs": [
            {"id": "fake_actor_A", "position": [0, 0, -dist if behind else dist],
             "named": named, "alive": True, "human": True},
        ],
        "scene": {"location": "synthetic_town", "weather": "rain",
                  "password": "do-not-expose"},
        "request": {"reply": "Synthetic response: hello.", "action": "wave"},
    }


def test_group_registered():
    assert "npc" in GROUPS


def test_nearby_actor_is_targeted_even_if_behind():
    result = npc.dryrun(scene(behind=True, dist=3.5))
    assert result["target"]["id"] == "fake_actor_A"
    assert result["proposed_action"] == "wave"


def test_far_actor_requires_facing_and_is_bounded():
    assert npc.dryrun(scene(behind=True, dist=6))["target"] is None
    assert npc.dryrun(scene(dist=15))["target"] is None
    assert npc.dryrun(scene(dist=6))["target"]["id"] == "fake_actor_A"


def test_named_actor_wins_equal_distance():
    s = scene(dist=3)
    s["npcs"] = [
        {"id": "unnamed", "position": [0, 0, 3], "named": False},
        {"id": "named", "position": [0, 0, 3], "named": True},
    ]
    assert npc.dryrun(s)["target"]["id"] == "named"


def test_dead_and_nonhuman_candidates_are_excluded():
    s = scene()
    s["npcs"][0]["alive"] = False
    assert npc.dryrun(s)["target"] is None
    s["npcs"][0]["alive"] = True
    s["npcs"][0]["human"] = False
    assert npc.dryrun(s)["target"] is None


def test_no_target_forces_no_action_and_no_dialogue():
    result = npc.dryrun(scene(dist=20))
    assert result["target"] is None
    assert result["proposed_action"] == "none"
    assert result["dialogue_text_fixture"] == ""
    assert result["spatial_audio_plan"] is None


def test_action_allowlist_blocks_unapproved_actions():
    s = scene()
    for action in ("open_door", "delete_save", "fight", "fetch_http"):
        s["request"]["action"] = action
        with pytest.raises(ValueError, match="allowlist"):
            npc.dryrun(s)


def test_scene_whitelist_redacts_unrelated_fields():
    result = npc.dryrun(scene())
    assert result["scene"] == {"location": "synthetic_town", "weather": "rain"}
    assert "do-not-expose" not in json.dumps(result)


def test_provenance_and_side_effect_flags_remain_false():
    result = npc.dryrun(scene())
    for key in ("model_called", "game_accessed", "audio_played",
                "action_executed", "in_game_verified"):
        assert result[key] is False
    assert result["local_contract_verified"] is True
    assert result["spatial_audio_plan"]["audio_played"] is False


def test_invalid_coordinates_and_bounds_fail_closed():
    s = scene()
    for value in ([float("nan"), 0, 1], [0, float("inf"), 1],
                  [0, 0], "3,4,5"):
        s["player"]["position"] = value
        with pytest.raises(ValueError):
            npc.dryrun(s)
    s = scene()
    s["npcs"] *= 65
    with pytest.raises(ValueError):
        npc.dryrun(s)


def test_deterministic_and_no_mutation():
    s = scene()
    original = copy.deepcopy(s)
    assert npc.dryrun(s) == npc.dryrun(s)
    assert s == original


def test_read_only_cli_with_fixture(tmp_path, capsys):
    p = tmp_path / "synthetic.json"
    p.write_text(json.dumps(scene()), encoding="utf-8")
    npc.run_dryrun(type("Args", (), {"fixture": str(p)})())
    actual = json.loads(capsys.readouterr().out)
    assert actual["target"]["id"] == "fake_actor_A"
    assert actual["action_executed"] is False


def test_oversize_fixture_rejected(tmp_path):
    p = tmp_path / "too_big.json"
    p.write_bytes(b" " * (npc.MAX_BYTES + 1))
    with pytest.raises(ValueError, match="maximum size"):
        npc.run_dryrun(type("Args", (), {"fixture": str(p)})())
