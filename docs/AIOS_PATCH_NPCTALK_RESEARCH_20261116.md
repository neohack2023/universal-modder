# AIOS research candidate: Patch, Cloud Blender, Elements, NPCTalk (2026-11-16)

Status: **SOURCE_BOUNDED / LOCAL_TESTED_SLICES / NOT_CANON / NOT_PUBLISHED**.
Scope: Drive PROJECT_SCOPE_REGISTRY `pc-game-re-modding` (Drive authority); GitHub `neohack2023/universal-modder` owns implementation; Host02 owns local test receipts. Notion is not consulted.

## Source pins (do not equate source with execution)
- Our Universal Modder: `https://github.com/neohack2023/universal-modder` @ `aea36260863c3c91f6ca42f5f2a3b88f2cded89f` before this research branch.
- Upstream Universal Modder: `https://github.com/rehan-remade/universal-modder` @ `3c4ac6c38e411b8c543bce217eae197039516bfc`.
- NPCTalk: `https://github.com/christos-antono/NPCTalk` @ `764da63ab709a4d5cf60fdcef34c30ec91b5e61f`.
- Patch Elements: `https://git.patch.gg/patch/elements.git` @ `46c4142`.
- Ultra Elements: `https://github.com/Humpalumps/ultra-elements` @ `698b720`.
- Public Patch schema: `https://patch.gg/api/v1/openapi.json`, SHA-256 `9dc173fb4b487d814895ef799367eaa2a4c636479e5a4e84fbea64087e1f72a1`.
- Documentation: `https://docs.patch.gg/mcp-server`, `https://patch.gg/blender`, `https://patch.gg/patch/elements`.

## What our repo already owns
- `tools/aios_evidence_bridge.py` indexes field notes by SHA-256, metadata and cited URL, **CANDIDATE_ONLY** by default.
- Fork-only bridge + three tests are useful custom work. Preserve it; do not wholesale reset to upstream.
- Tracked-file comparison: our fork 531 vs upstream 924; many more upstream examples, knowledge items, skills and tests. The upstream HEAD differs; this is a file-level inventory, not a history/merge safety proof.
- Baseline with compatible NumPy: 101 passed, 1 failed, 1 skipped (known MGRR field-note schema failure). Dedicated bridge suite: 3 passed.
- New `um patch` public catalog adapter in this local branch: assets, single-asset metadata, repos, blender-costs; no authentication or writes. `tools/tests/test_patch_catalog.py` checks read-only behavior, path safety, SPDX/credit/hash preservation and candidate flags.
- OpenCode plugin group list is synchronized with the new CLI group. Final scoped regression: **107 passed, 1 skipped, 1 previously known MGRR metadata failure deselected**, `git diff --check` clean. Targeted new adapter + existing bridge: **9 passed**.

## Patch public API (live GETs, Host02)
- Schema: 141 selected endpoints across projects, assets, Blender and repos (not necessarily all API endpoints).
- `GET /assets/search?q=smoke&limit=3`: HTTP 200, 135 total; `kenney:blaster-kit/smoke.glb`, CC0-1.0, ready, 380 triangles, ~0.02 MB prepared WebGL variant; **candidate**, not imported or downloaded.
- `GET /assets/{id}`: HTTP 200; includes structured license evidence (upstream License.txt citation), exact credit text including Patch modifications, original source/revision, preview/web variant file SHA-256 and sizes (9,464 and 19,968 bytes). New `um patch asset <id>` exposes only metadata, not download links or bytes.
- `GET /repos/search?q=elements&limit=3`: HTTP 200, public repo `patch/elements`, engine three.js, MIT, clone URL as pinned above.
- `GET /blender`: HTTP 200, Blender 5.2.0; Cycles/Eevee/Workbench; L40S and L4. Session tiers 50/100/200 credits per hour; GPU session L40S/L4 200/100; render L40S/L4/CPU 250/150/50. These are **API-listed rate categories**, not a verified invoice or combined cost estimate.
- Patch MCP uses scopes `read`, `publish`, `compute`; stop/cancel of cloud tasks are compute actions. Do not grant compute or publish by default. Public API catalog GETs need no key.
- A project's source can be a Git repo and its publication recipe can describe dependencies. This may map to our reversible package manifests; it does not make Patch an AIOS authority.
- Public fields can be untrusted user text. Preserve `untrusted_fields`, SPDX license, creator credit, hashes and source reference. No automatic ingestion into canon or game installs.

## Patch Elements and actual GPU boundary
- 39 WebGL2/three.js effects, with GPU particles, FLIP fluid, combustion, volume raymarching and procedural weather/ground reactions. MIT adaptation of Ultra Elements.
- Patch Elements static production build passed on Host02 with Node/Vite: 39 spells, 411 per-spell settings, 29 spell modules, 83 modules transformed, 1.84 MB dist. Bundler warned that a JS chunk exceeds 500 kB; no in-game speed claim follows from a build.
- `elements.js` owns the THREE frame loop, HDR/PostFX and warm-up; dynamically loaded Vite spell modules, floor y=0, bounded arena/target assumptions. Not a native D3D11 or D3D12 drop-in.
- Local normal-Edge (no debugging interface) WebGL2 preflight on Intel HD Graphics 520, ANGLE Direct3D11: 150 rendered frames; median requestAnimationFrame interval 16.7 ms; p95 17.0 ms; 16,384 max texture; timer-query extension advertised. This **does not** benchmark Elements or GPU time. Receipt SHA-256 `50e26655ef71cb3e236fd2ee786cc08d3026a60c3fe81e179ff85a18c893a49a` at Host02 scratch root.
- Next controlled Elements test: shader warm-up, one effect at a time, GPU-disjoint timer readings, visual screenshots, peak memory and crash/driver-reset monitoring. Stop on GPU instability.
- Avoid disabling Windows Smart App Control or installing Patch Desktop just to evaluate this stack. Public REST/CLI and local sources are sufficient for discovery.

## NPCTalk
- Repo has eight agent skills, Python `npctalk` commands, streaming voice-server designs and GTA V C# example (21 C# source files). Source-bound four game seams: choose target NPC, collect current scene, play spatialized voice, dispatch a restricted action.
- 25/25 Python tests passed using compatible existing NumPy. Does not validate latency, speaker identity, generated voice quality, or a launched GTA V game.
- GTA V project targets .NET Framework 4.8 and references ScriptHookVDotNet3/NAudio; Host02 lacked the .NET SDK for this check. No C# build or game injection performed.
- Integration proposal: optional `npc-voice` adapter contract after engine recon. Keep LLM dialogue, STT/TTS, game-specific action allowlists, consent for voice likeness, and offline/game tests separate.
- Never publish game voice clips/transcripts or someone else's likeness without rights. Multiplayer anti-cheat avoidance and no game-binary mutation remain mandatory.

## X and Discord
- X status `2111023814687731780`: normal Edge accessibility displayed Patch's Tesla Roadster in a Rocket League-style **browser** car-soccer post. Treat as a browser recreation/cross-game design reference; **not** evidence of patching Rocket League's actual executable.
- Three provided Discord channel URLs opened in Edge but displayed Discord login. No message bodies extracted or authorized authentication attempted. Keep as UNVERIFIED_CHANNEL_SOURCE.

## Handoff and promotion gates
1. Retain this research in the `pc-game-re-modding` lane as external candidate evidence, not Drive canon. Keep the local test artifacts separate from source code.
2. Test actual Patch Elements on Intel HD 520 with controlled GPU timings; compare to independently measured prior Underdog workload only when configurations are equivalent.
3. Bring NPCTalk's game-independent four-hook contract into an optional adapter; first validation should use a fake NPC target and synthetic dialogue, not game binaries or cloned voice.
4. Add asset-list output to the existing AIOS candidate-evidence ingestion path with SPDX and hash checks; do not create a parallel durable database.
5. Fix the existing MGRR field note against source evidence separately. It fails a schema test and must not be papered over with invented verification.
6. Publishing a branch, PR, Patch project or release requires explicit approval and security review.
