---
kind: game
title: "TDR 2000 with Rust damage hooks: a Wreckfest-inspired merge that loaded but did not arm"
game: "Carmageddon TDR 2000"
games_also: ["Wreckfest"]
game_version: "Local Windows PE32 TDR2000.exe SHA-256 364e84c340358c5b8da545f6f084a13cfc86f8db7a49eb5455eca1fd9f24fd94; Wreckfest exact executable version not pinned"
platform: windows
engine: native
route: native-hook
tools: ["Rust 1.99.0 i686-pc-windows-msvc", "Frida 17.22.1", "Ultimate ASI Loader", "pefile", "Ghidra", "universal-modder um win"]
anti_cheat: "Offline single-player lab only; no online/anti-cheat intervention"
status: in-progress
agents: ["ChatGPT (GPT-6)"]
humans: []
date: 2026-10-18
links: ["https://github.com/neohack2023/universal-modder"]
tags: [tdr2000, carmageddon, wreckfest, rust, x86, native-hook, frida, asi, physics, deformation, observability, mashup]
---

# TDR 2000 with Rust damage hooks: a Wreckfest-inspired merge that loaded but did not arm

> An isolated copy of the user's actual Carmageddon TDR 2000 executable launched with a 32-bit Rust ASI and reached Hollowood Free Driving. A Rust bridge ran inside the real process, but the separate Frida contact/damage hook installer failed with `Error: invalid abi specified`. This is an **in-progress host-engine feature port**, not a playable Wreckfest physics merger. The guest Wreckfest executable was used as a research source, not run as a second concurrent physics engine.

## Setup

- Owned TDR Windows 32-bit executable identified by full SHA-256 in front matter. The working lab has isolated, rollback-safe cloned game folders. Never substitute Dethrace: it is Carmageddon 1997 lineage, **not** TDR 2000 source.
- Owned Wreckfest install and independent static research under the local PC-game RE lab. Its build identifier/hash was not captured for this field note, so engine-level parity must remain unverified.
- Rust and Cargo 1.99.0 with `i686-pc-windows-msvc`; Frida Python 17.22.1; an ASI loader in the disposable TDR copy. Local project: `PC_GAME_RE_LAB_01/MERGES/TDR2000_WRECKFEST_RUST_V01/`.
- Repo contains **no** original executables, ASI binaries, extracted assets, decompiled function bodies, or local game data.

## Route and why

- **Native-hook** and Rust `cdylib` is the bounded path: TDR owns contacts, world state, vehicles, deformable mesh updates, rendering and gameplay cadence; Rust supplies independent candidate computations; the hook adapter may change a bounded native damage argument.
- Not a recompilation of either whole commercial engine. Two simultaneous authoritative solvers on the same rigid body would double-apply impulses.
- The Rust deformation and damage curve are independent hypotheses inspired by Wreckfest's subsystem concepts, not reconstructed Wreckfest algorithm parity.

## How the game works (what we had to learn)

- In the hash-pinned TDR build, the PE image base is `0x00400000`. Static reconstruction identifies `FUN_0050F060` as contact bookkeeping and `FUN_00492070` as a vehicle damage entry; caller signature and field semantics need runtime confirmation before broadly changing state.
- `DAT_005CD864` in the owned TDR clone has raw bytes `AB AA AA 3D`, float32 approximately `0.08333333582`. In-process Rust read this value and computed example inertia XX `25.0`. This proves access and calculation, **not** full engine parity.
- The existing TDR research includes inverse inertia, contact friction, Eagle4 detachable panels and render/collision geometry, and Hollowood mesh405's 103 mapped render-to-collision vertex pairs. A point-pair map does not supply full triangle or collision topology.
- Prior fixed-cadence investigation observed AI changes when TDR's 25 Hz simulation was doubled, so preserve stock gameplay timing until deterministic behavioral evidence supports a change.
- Wreckfest research identifies separate soft-body deformation, geometry synchronization, surface effect and skidmark subsystem candidates. Their semantics have not been validated against original runtime outputs.

## Build steps

1. Search `um kb search "Carmageddon"` and `um kb search "Wreckfest"`, then scan the owned installations. Record executable hashes and store versions. Keep a `MODLOG.md` outside this public repository.
2. Make an isolated, disposable TDR clone and save rollback hashes. Do not modify the original installation; avoid copying game content into Git.
3. Independently implement contact/inertia/impact-candidate primitives in a Rust workspace. The previous Rust library ran 10 unit tests; a later bridge's two bounded gain/passthrough tests passed. These are **synthetic tests**, not game parity.
4. Build a 32-bit Rust `cdylib` and stage it as a loader-managed ASI. Export only small, typed functions and counters. Keep the game as owner of all mesh and physics state.
5. Pin the exact PE executable hash and target entry bytes before installing any native hook. Use a Frida launcher from outside the game clone; keep hook installation and its telemetry separate from DLL initialization.
6. On launch, capture a bridge-loaded receipt, hook-install success/failure, contact/damage call counters, native exception context and a tail of TDR's own debug log. Treat absence of a hook-armed event as **not merged**, even if the menu or race works.
7. Stage rollback by removing the V02 ASI or using the prior clone. Validate the next build against actual gameplay only when authorized by the owner.

## Verification

- **Real run:** V02 TDR process loaded the Rust ASI. The in-process receipt recorded `RUST_DLL_LOADED_IN_REAL_TDR_PROCESS`, inertia factor `0.08333333582`, example inertia XX `25.0`, `engine_hooks_enabled: false` and `game_state_mutated: false`.
- **Real run:** TDR's debug log recorded loading `assets\\tracks\\hollowood_race1` in Free Driving. Earlier UI capture confirmed the main-menu → Free Driving selector transition and Hollowood Start loading screen using real game-relative mouse input.
- **Failure:** runtime event `hook_install_blocked` with `Error: invalid abi specified`. No `tdr_wreckfest_merge_armed` event, contact counter or modified-damage witness occurred. A proposed ABI correction was not deployed during the observed run.
- **Synthetic/static:** Rust tests and disk module/export/hash checks passed, but these do not establish native gameplay change.
- **Not verified:** Wreckfest original solver parity, actual Wreckfest vehicle deformation transferred into TDR, any live Rust-modified damage, reliable collision or visible before/after dents, continuous in-game post-hook gameplay, performance or multiplayer safety.

## Gotchas

1. **Game loads without crashing, but no merged damage.** **Cause:** Rust's ASI loaded while the Frida adapter failed to create native function bindings (`invalid abi specified`), so no hook installed. **Fix:** correct the ABI declaration to a convention supported by the installed Frida version, repin script SHA and require an explicit hook-armed event plus changed argument counters; this fix was **not yet verified**.
2. **Unit tests all pass but there is no engine merge.** **Cause:** Rust calculations used synthetic inputs and a candidate policy, not original executable outputs. **Fix:** label separately unit-test, binary-oracle parity, live module loaded, native-hook armed, native function called and visually verified gameplay.
3. **Menu pointer does not follow absolute Windows cursor.** **Cause:** TDR uses a game-owned relative DirectInput cursor and the capture/display scales differed. **Fix:** relative mouse movement with foreground and screenshot verification. The Free Driving selector and Hollowood loading transition were observed.
4. **A grass-road point map is mistaken for a complete track.** **Cause:** the 103 render-to-collision vertex correspondences lack face topology and runtime collision bounds. **Fix:** import faces, collision ownership and bounds as independent acceptance gates.
5. **Damage code and assets are conflated.** **Cause:** changing an Eagle4 archive's detachable panel data does not prove a live Wreckfest soft-body solver ran. **Fix:** require original game in-process event witnesses and separate archive verification from runtime physics.
6. **A hook fails silently on another build.** **Cause:** fixed addresses without a matching original executable hash, image base and instruction prefix. **Fix:** fail closed on mismatches, emit a structured receipt, and keep old and new cloned builds isolated.

## Assets

Native TDR Eagle4 and Hollowood assets remain in the user's local owned-game workbench. The public repository contains only this procedural note.

## Open questions

- Confirm supported Frida native-function ABI for the actual 32-bit bridge and obtain `tdr_wreckfest_merge_armed`, then counters.
- Confirm native damage argument calling convention and original TDR input/output behavior with trace/fixture witnesses.
- Find Wreckfest's actual deformation coefficient/mesh ownership semantics using original runtime evidence before describing a faithful feature port.
- Capture exact Wreckfest game build and distinguish Wreckfest-original methods from candidate approximations.
