# AIOS Discord → Reusable Modding Techniques | 2026-11-16

Status: **OBSERVED_SOURCE_VERIFIED / ENGINEERING_PATTERNS_EXTRACTED / LOCAL_OFFLINE_NPC_CONTRACT_TESTED**. Not a blanket claim that external games/mods work, not an approval to redistribute assets.
Scope and owner: Drive Project Scope Registry `pc-game-re-modding`; Host02 runs execution probes; GitHub owns live implementation facts.
Original Drive source pin: https://docs.google.com/document/d/1UC2C7PJT5hvuUczSYdlN2_kQL_OuGOjhwYAOJM8a2xo/edit

## Exact verified community channels
- [#showcase](https://discord.com/channels/1556608890131714048/1556613031155343420) — forum; visible project posts, not independent in-game verification.
- [#wishlist](https://discord.com/channels/1556608890131714048/1556613035739586663) — tagged mod/port/mashup requests; demand signal, not installed features.
- [#github](https://discord.com/channels/1556608890131714048/1556613044342096004) — upstream GitHub-app announcements for `rehan-remade/universal-modder`; trace from announcement to real GitHub pull request rather than using the bot text as code authority.
- [The Lost Arts Discord thread](https://discord.com/channels/1556608890131714048/1571828259472146442) — Skyrim creator says early-stage NPCs use Ollama, support conversation and generated quests; thread includes a short introduction. No public implementation repository or end-to-end reproducibility proof established by this research.

## Source 1: NPC sidecar + game-hook separation

**Direct public engineering control:** [NPCTalk](https://github.com/christos-antono/NPCTalk) at `764da63ab709a4d5cf60fdcef34c30ec91b5e61f`, esp. `skills/make-npcs-talk/references/{architecture,game-hooks,safety}.md`.

Source-owned design: A game-free dialogue/STT/TTS and action-selection layer plus precisely four game-specific adapters: (1) target selection, (2) scene context, (3) spatialized NPC voice, (4) whitelisted game actions. GTA V story-mode C# sample uses ScriptHookVDotNet/NAudio, not a generic working Skyrim adapter. Skyrim SKSE/Papyrus, Unity BepInEx, Unreal UE4SS, etc. are **suggested** entry points in the source, not demonstrated integrations.

**The Lost Arts comparison:** Its Discord author describes Ollama NPC conversations and dynamically generated quests; that supports a *requirements* link to NPCTalk's architecture, but does not establish the creator's internal code layout, prompt format, model, quest persistence mechanism, or gameplay correctness. Do not infer any of these details.

**Local re-implementation:** `um/npc.py` and `um npc dryrun examples/npc-hook-synthetic.json` implement an engine-neutral offline probe. Bounded synthetic NPC targets with 5 m always-eligible range and 5–12 m facing threshold, scene-key allowlist, dialogue fixture, restricted action *proposal*, spatial audio attenuation *plan*. No game access, speech service, LLM call, audio playback, file modifications, or action execution. These choices are independently implemented based on visible source patterns. It is not a Skyrim mod or a clone of NPCTalk.

**Game-port gate:** First add one adapter for game-specific selection/scene read-only. Second test synthetic replies with fake voice and no executable action. Third test owned game offline and measure target stability, latency, positional audio, subtitles and quest persistence separately; user-authorized install required before integration. Keep game dialogue, licensed voice sources and third-party asset bytes out of the repo.

## Source 2: Quake VR — architecture and deterministic experiments

**Direct technical control:** [vittorioromeo/quakevr](https://github.com/vittorioromeo/quakevr) source at `5187f3e5e01df56ee1350ef3f9425caf828cf390` (master when fetched).
- `docs/vr-port/ARCHITECTURE.md`: C engine <-> C++20 VR module <-> QuakeC rules separation, narrow typed builtin/field/cvar boundaries. State ownership and frame ordering matter more than transplanting a whole engine. Source has tests for QC-to-C++ references and explicit engine-hook owners.
- `docs/vr-port/TESTING.md`: mock headset, fixed frame time, scripted controller/hand poses, seeded particles/world RNG, deterministic state/hash and cross-language verdict conventions; validate gameplay in repeatable synthetic paths before claiming VR hardware support.
- `docs/vr-port/AD_CASTER_CPU_OPTIMIZATION.md`: illustrative exact-output graphics optimization. Source reports 12,264 fixture comparisons, 216,614,502 generated indices, matching shadow atlas hashes, and measured action full-shadow CPU 0.18442 -> 0.17140 ms/frame (one sequential pair); shadow GPU ~unchanged. Techniques: reserve triangle fan indices once, collect candidate brush entities once per render invocation, preserve order, null/edge cases and portal camera context.
- README identifies **GPL-2.0** source licensing and Quake data ownership. Our Universal Modder fork is MIT, so **do not copy GPL engine code** into our fork; use independent interfaces, specifications and test methodology.

**Hardware transfer target:** On Intel HD 520 / Underdog graphics fixtures, implement independent baseline-vs-optimized *candidate surface collection* test with sorted identity, stable geometry index order, matching output hashes, CPU timings; only compare GPU when both settings, resolution and workloads match. Quake VR performance numbers are source benchmarks, not measured on Host02.

## Source 3: Upstream notification → source implementation verification

The [#github feed](https://discord.com/channels/1556608890131714048/1556613044342096004) is a trustworthy source **of what was posted**, not a test pass on our fork.
[Universal Modder upstream](https://github.com/rehan-remade/universal-modder) `main` at `3c4ac6c38e411b8c543bce217eae197039516bfc` when checked.
- [PR #514](https://github.com/rehan-remade/universal-modder/pull/514) — **OPEN**: Touhou Puppet Dance Performance Shard of Dreams Extended, reported single-player `dxgi.dll` proxy hook, per-save randomizer, loose-file overrides and compatibility gotchas. Source author reports in-game verification except PP respec, but no independent Host02 trace. Source mentions GPLv3 code in associated randomizer core; preserve license/attribution.
- [PR #515](https://github.com/rehan-remade/universal-modder/pull/515) — **OPEN**: Fantasy Maiden Wars DoSD, GameMaker GMS2 bytecode, UndertaleModTool CLI with modded `data.win` loaded via `fmw_dosd.exe -game` to keep Steam install vanilla. Author reports some late fixes not yet witnessed in-game. Independently useful recipe: isolate mod payload + exact build identity + reversible launch argument + softlock acceptance tests.

Pull request proposals are not merged upstream, nor included in our fork merely because #github mentioned them. Retain their PR status and commit SHA separately from Discord message dates.

## Source 4: Wishlist → requirements graph (no installed mods assumed)
Verified in [#wishlist](https://discord.com/channels/1556608890131714048/1556613035739586663):
- Dead Island 2 gore system -> GTA V (in-progress claim): decomposition target of damage event, dismemberment asset, particles, decals, and engine-specific physics; requires rights and format checks.
- Fallout: New Vegas + GTA IV: broad mashup, cannot accept before selecting a portable subsystem and exact source/target build.
- PES 6 as host game: actionable missing game adapter; test installation fingerprint, mod-load surface, crowd asset layout and reversible restore. Third-party message says an Old Trafford crowd mod is ready; not tested here.
- Palworld + Fortnite, PS2-style Security Breach demake, WCW Mayhem/Revenge: concept-intake leads, not evidence for game support.

Before any candidate becomes a task, normalize `source_game`, `target_game`, `build`, `engine`, `feature`, `dependency`, `license`, `safe_test`, `rollback`, `evidence_state`.

## Knowledge routing / non-conflation
Source observation = DISCORD_POST_VERIFIED or GITHUB_SOURCE_VERIFIED. Offline contract = HOST02_SYNTHETIC_TESTED. Claimed released / in-progress = THIRD_PARTY_SELF_REPORT. Actual installed game result = HOST02_RUNTIME_VERIFIED only after execution witness. Never equate these.

Use the existing AIOS evidence bridge and project's Drive source bindings, do not create a new global DB. Keep duplicate Discord bot messages linked to one GitHub PR/commit, and keep first-hand post evidence separately addressable. This note is a reusable engineering research packet; game-general canon promotion requires explicit governed validation.
