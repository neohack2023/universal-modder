---
kind: game
title: "Minecraft native Faucet mod SDK compatibility migration: pinned Quake/Rust adapter"
game: "Minecraft for Windows (4J/Faucet native candidate)"
games_also: ["Quake"]
game_version: "Source-built Faucet MinecraftClient.exe SHA256 6c4a3a84c1eb194c9e39404d78bbfe718f1334a30d482d63b2708504538d2538"
platform: windows
engine: native
route: native-hook
tools: ["MSVC Build Tools", "Python", "PE export/import verifier", "Rust FFI", "Universal Modder port-a-mod guidance"]
anti_cheat: "Isolated, offline, user-owned native Minecraft playtest; no multiplayer or protected game process"
status: in-progress
agents: ["ChatGPT (GPT-6)"]
humans: []
date: 2026-10-21
links: ["https://github.com/rehan-remade/universal-modder/blob/c1dff21663665dd17af289744a301b66e369605e/skills/port-a-mod/SKILL.md", "https://github.com/ytsodacan/Faucet"]
tags: ["minecraft", "faucet", "mod-compatibility", "port-a-mod", "native-dll", "rust", "migration", "static-verified", "runtime-unverified"]
---

# Source-matched Minecraft native mod adapter: bounded migration evidence

**Outcome: PARTIAL.** A Windows Host 02 read-only recheck verified that the revised Quake/Rust rocket mod DLL matches the source-built Faucet Minecraft executable and its Rust ABI. It did **not** launch the game, observe item use, or demonstrate an actual playable mod migration. **Do not mark `port-a-mod` as fully real-mod-validated.**

This experiment examines only **the native Minecraft mod SDK/loader adaptation**. Quake projectile mechanics carried into Minecraft are a cross-game **mashup-mods** case, not the `port-a-mod` skill's principal task. The installed Minecraft runtime is a native 4J/Faucet lineage candidate, **not Minecraft Java Forge/Fabric**. There is no pinned older Forge mod or identified Java Minecraft installation on this host.

## Setup

Use existing Host 02 native adapter, source-built Minecraft client, and pinned Rust DLL; do not modify the working user game.

## Sources and pins

- Skill reference: upstream `port-a-mod` at `c1dff21663665dd17af289744a301b66e369605e`.
- Older adapter: `10_SCRATCH/QUAKE_NATIVE_GAME_ADAPTER_V01/QuakeRocketFaucet.cpp` SHA256 `f59de057910ddca7540d3c17740f127a31d6febb72e4f28619c14fe0ff8debe6`.
- Matched-source adapter: `10_SCRATCH/FAUCET_MATCHED_SOURCE_BUILD_V01/QuakeRocketFaucetPinned.cpp` SHA256 `6549e31048b31ec4fb6b75bca3f5aa03a261e394ae11862283b075dc66dff0b8`.
- Faucet source fork: `5cf6901918d0d50f2916119ce06243b691ef2178`.
- Executable SHA256: `6c4a3a84c1eb194c9e39404d78bbfe718f1334a30d482d63b2708504538d2538`.
- Native mod DLL SHA256: `0d4dce28817c008bf3d4568bfd320ad4be01b1dd5ca28b60be743e9e67002f20`.
- Rust dependency DLL SHA256: `34ac87f99584945f8693aaf7252e4e5951c311c2e572284bfe95633a2c43cfd0`.

## Route

Native SDK import adaptation on the same source-built executable. The separate Quake-to-Minecraft feature transfer remains mashup-mods.

## Adaptation matrix and observed results

| Original | Adapted | Evidence |
| --- | --- | --- |
| Older FaucetSDK library missing required native exports | Source-matched `MinecraftClient.lib` and host executable | Fresh import/export check PASS: 67 host exports, required symbols present |
| Dependent Rust DLL next to mod | `mods/_deps/quake_rocket_reconstruction.dll` | Dependency file and version-1 ABI PASS |
| Sneak+sprint chord, fixed +X projectile path | F6 selected-item gate, player facing vector, XYZ sampling | **Code exists; gameplay behavior and parity NOT VERIFIED** |
| Historical `COMPILE_PASS_LINK_FAIL` adapter | Source-built and staged plugin | Earlier link failure supported by Oct 14 receipt; **not reproduced in this run** |

Fresh verifier command on Host 02:
`python GAMES/MINECRAFT_WINDOWS/10_SCRATCH/FAUCET_MATCHED_SOURCE_BUILD_V01/verify_real_link_pair.py`.
It returned **exit 0** and `MATCHED_SOURCE_DLL_PAIR_VALIDATED`. The staged executable, mod DLL and Rust DLL match the pinned build SHA256 values. A separate bounded evaluation checked nine source/target/staging artifacts and recorded `PASS`.

## Verification

## Host 02 receipts and limits

- `GAMES/MINECRAFT_WINDOWS/90_RECEIPTS/PORT_A_MOD_NATIVE_MINECRAFT_COMPATIBILITY_EVAL_V01.json` is the fresh machine-readable receipt.
- `GAMES/MINECRAFT_WINDOWS/90_RECEIPTS/QUAKE_NATIVE_REAL_MINECRAFT_ADAPTER_CHECKPOINT_V03.json` records the old link failure.
- `GAMES/MINECRAFT_WINDOWS/10_SCRATCH/FAUCET_MATCHED_SOURCE_BUILD_V01/STAGING_REAL/MATCHED_SOURCE_LINK_RECEIPT_V01.json` records the new source-matched verification.
- No new game binary, runtime profile or world was created or modified during the recheck. Several active MSVC compiler processes discouraged an additional expensive build.
- No fresh runtime launch, visual rocket, damage/physics parity, controller operation, or original-vs-ported gameplay witness was obtained.
- No proprietary game code or game assets should be committed with this finding.

**Classification:** `HOST02_NATIVE_STATIC_COMPATIBILITY_VERIFIED_REAL_MOD_BEHAVIOR_UNTESTED`. Next gate: isolated runtime loader proof followed by behavior parity in a disposable test world, and a separate genuine older-version-to-newer-version mod migration to assess the full skill.

## Gotchas

This is not Minecraft Java Forge/Fabric. A native DLL import/ABI success does not demonstrate modloader execution, world entry, or gameplay parity. An old source API and its revised control triggers are not equivalent behavior.
