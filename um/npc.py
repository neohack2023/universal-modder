"""Offline, engine-neutral NPC hook contract: source-derived, no game/audio/network I/O.

Usage:
    um npc dryrun fixtures/npc_synthetic.json

Reimplemented from public architecture patterns (NPCTalk / Quake VR); this is
not NPCTalk code, a game mod, a voice service or a licensed voice clone.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

MAX_BYTES = 256_000
MAX_NPCS = 64
SAFE_ACTIONS = frozenset({"none", "idle", "wave", "look_at_player"})
SCENE_FIELDS = ("location", "weather", "time_of_day", "quest", "danger")

def _vector(value, label: str) -> tuple[float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{label} must be a 3-vector")
    try:
        out = tuple(float(x) for x in value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{label} contains a non-number") from exc
    if not all(math.isfinite(v) and abs(v) < 1_000_000 for v in out):
        raise ValueError(f"{label} contains invalid coordinates")
    return out


def _norm(vec) -> tuple[float, float, float]:
    length = math.sqrt(sum(x*x for x in vec))
    if length < 1e-8:
        raise ValueError("camera direction cannot be zero")
    return tuple(x/length for x in vec)


def select_target(player: dict, npcs: list[dict]) -> dict | None:
    """Within 5 m choose nearest; 5-12 m require camera dot > .85.

    Named NPC preference breaks nearby ties, but never bypasses distance/facing.
    """
    if not isinstance(npcs, list) or len(npcs) > MAX_NPCS:
        raise ValueError("npcs must be a bounded list")
    origin = _vector(player.get("position"), "player.position")
    fwd = _norm(_vector(player.get("forward"), "player.forward"))
    ranked = []
    for index, npc in enumerate(npcs):
        if not isinstance(npc, dict):
            raise ValueError("npc must be an object")
        if not npc.get("alive", True) or not npc.get("human", True):
            continue
        pos = _vector(npc.get("position"), "npc.position")
        direction = tuple(p-o for p, o in zip(pos, origin))
        distance = math.sqrt(sum(x*x for x in direction))
        if distance > 12.0:
            continue
        facing = 1.0 if distance < 1e-8 else sum(a*b for a,b in zip(direction,fwd))/distance
        if distance > 5.0 and facing <= 0.85:
            continue
        identifier = npc.get("id")
        if not isinstance(identifier, str) or not identifier or len(identifier) > 128:
            raise ValueError("valid NPC id required")
        named = bool(npc.get("named", False))
        # Same-distance named preference; no hidden game-specific NPC state.
        ranked.append((round(distance, 3), 0 if named else 1, identifier, index, pos, distance, facing))
    if not ranked:
        return None
    ranked.sort()
    _, _, identifier, index, pos, distance, facing = ranked[0]
    return {"id":identifier, "distance_m":round(distance, 3),
            "facing_dot":round(facing, 3), "position":list(pos), "index":index}


def dryrun(fixture: dict) -> dict:
    """Produce a read-only action/audio *plan*. Never perform either operation."""
    if not isinstance(fixture, dict):
        raise ValueError("fixture must be a JSON object")
    player = fixture.get("player")
    if not isinstance(player, dict):
        raise ValueError("player object required")
    target = select_target(player, fixture.get("npcs", []))
    raw_scene = fixture.get("scene", {})
    if not isinstance(raw_scene, dict):
        raise ValueError("scene must be an object")
    scene = {k: str(raw_scene[k])[:128] for k in SCENE_FIELDS if k in raw_scene}
    request = fixture.get("request", {})
    if not isinstance(request, dict):
        raise ValueError("request must be an object")
    action = request.get("action", "none")
    if not isinstance(action, str) or action not in SAFE_ACTIONS:
        raise ValueError("action not in read-only fixture allowlist")
    reply = request.get("reply", "")
    if not isinstance(reply, str) or len(reply) > 512:
        raise ValueError("reply must be a short string")
    if target is None:
        action = "none"
        reply = ""
    audio = {"source_npc": target["id"], "distance_attenuation": round(
        max(0.0, 1.0 - max(0.0, target["distance_m"] - 4.0) / 26.0), 3),
        "audio_played": False} if target else None
    return {
        "kind": "offline_npc_hook_dryrun",
        "model_called": False, "game_accessed": False,
        "audio_played": False, "action_executed": False,
        "local_contract_verified": True, "in_game_verified": False,
        "target": target, "scene": scene,
        "dialogue_text_fixture": reply, "proposed_action": action,
        "spatial_audio_plan": audio,
        "hooks": {"target": target is not None, "scene": True,
                  "voice": False, "action": False},
    }


def run_dryrun(args) -> None:
    path = Path(args.fixture)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("fixture exceeds maximum size")
    result = dryrun(json.loads(path.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2, sort_keys=True))


def register(sub) -> None:
    parser = sub.add_parser("npc", help="Offline, read-only NPC hook contract probes")
    commands = parser.add_subparsers(dest="npc_command")
    probe = commands.add_parser("dryrun", help="Run a synthetic NPC scenario without game, LLM, voice or actions")
    probe.add_argument("fixture", help="Small JSON scene; never point to game or private chat files")
    probe.set_defaults(func=run_dryrun)
