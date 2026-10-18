---
kind: game
title: "Extract and validate MGRR Blade Mode components with REA, Blender and Godot"
game: "Metal Gear Rising: Revengeance"
games_also: []
game_version: "PC PE32 x86, executable SHA256 7174741f46ab4c222304b0f1b9291a2281d53368016347e65d2ea404ff07ad34"
platform: windows
engine: unknown
route: reimplementation
tools: ["REA 6.7.0", "Ghidra 12.1.4", "Capstone", "MGR2Blender2MGR", "Godot 4.7.2", "Node.js 24.13.0", "Universal Modder CLI"]
anti_cheat: "Isolated offline single-player research and local user-owned copy; no competitive or networked use"
status: in-progress
agents: ["ChatGPT (GPT-6)"]
humans: []
date: 2026-10-18
links: ["https://github.com/morluto/rea", "https://github.com/rehan-remade/universal-modder"]
tags: ["blade-mode", "rea", "ghidra", "wmb4", "mot", "blender", "godot", "mesh-slicing", "runtime-parity"]
---

# MGRR Blade Mode: verified recovery and cross-engine validation

On a Windows PC game RE lab, we recovered five native Blade Mode state/aim/transform-related x86 routines with REA and Ghidra using exact original instruction bytes in isolated synthetic PE fixtures. Independently, we built a deterministic triangle-plane slicer in Node.js and tested it inside Godot against synthetic geometry and an original MGRR WMB4 cutting-data proxy. We exported Raiden's WMB4 mesh and skin and sampled original MOT skeletal tracks in Godot. **This is a working external reference prototype, not a complete or source-faithful reconstruction of MGRR's collision, dismemberment, fracture or effects engine.**

## Setup

- Windows Host 02, local scratch workspace, read-only original game executable identified by SHA256 in front matter.
- REA `rea-agents@6.7.0` using Ghidra 12.1.4 and a local Java JDK; Node.js 24.13.0. Keep the package and scratch cache local. On this host, a full executable cold import timed out around 185 seconds; avoid retrying without a bounded hypothesis.
- Existing WMB4/MOT parsers from MGR2Blender2MGR, tested Godot 4.7.2 Compatibility renderer. Intel HD 520 used ANGLE fallback for actual 1280x720 render capture.
- The `um` CLI was present; `um kb check` validated the field note. A JSON bridge called by a UM agent is a **custom adapter**, not an official UM Blade Mode subcommand.

## Route and why

Use **native source evidence** (REA/Ghidra + exact bytes), **read-only original asset parsing** (MGR2Blender2MGR) and **isolated engine replay** (Godot + independent Node slicer) as three distinct evidence classes. Never declare source-game parity just because a portable result looks plausible. Only promote after same-input original-game/runtime witnesses agree.

## How the game works (what we had to learn)

### Static executable evidence

The community object layout names field `+0x40C8` `m_nBladeModeType`. Native bytes independently show:

| Original RVA | Evidence | Verified scope |
| --- | --- | --- |
| `0x7CD120` | 322-byte owning entry routine; conditional write of mode value 2 | Exact-byte fixture REA recovery |
| `0x45C4B0` | 13-byte setter; writes supplied value to `+0x40C8` | Exact-byte fixture REA recovery |
| `0x78A040` | 246-byte exit owner; conditionally writes zero | Exact-byte fixture REA recovery |
| `0x4BC5A0` | 1,394-byte mode-2-gated aiming/transform path | Exact-byte fixture REA recovery, helper meaning partial |
| `0x683330` | 1,630-byte downstream spatial/transform handler | Exact-byte fixture REA recovery, not verified as collision |

A historical supervised trace associated **17 exit/zero-write observations** with the recorded player pointer but did **not** capture a confirmed same-player `0 → 2 → 0` activation cycle. Native blade-plane geometry, hit dispatch, triangle fracture, dynamic cap generation and effect triggering remain **unverified**.

### Asset format and geometry

- WMB4 models contain a cutting-data offset at header byte `0x6C` (108). A generic parser detected the offset but had no populated cutting-record schema. **Reuse the richer existing MGR2Blender2MGR WMB4 slicing parser** instead of inferring every field from raw byte patterns.
- Two examined enemy models, `em0110` and `em0112`, exposed **33 Slice6Data geometry entries** in total (19 + 14). All passed in-file bounds, finite coordinate, sampled index and closed-manifold topology checks. Their first entries contain 8 vertices / 12 triangles each. These are source **cut-volume proxy meshes**, not witnessed runtime slice results.
- Four Raiden-related WMB4 meshes were exported for private Godot inspection. Two body models, `pl1010` and `pl0100`, successfully imported **11 and 25 skinned mesh batches** respectively, each bound to a **95-bone Godot Skeleton3D**. The exporter recorded **36,021 weighted vertices** and zero invalid skin references over both.
- Two original `pl0010` MOT clips have **131 and 121 frames**; each contains 240 motion-channel records. All **70 animated bone IDs** used by the decoded tracks exist in the 95-bone character rigs. Quantized Hermite record decoding and candidate ZYX rotation order were used, but source-game playback timing and pose parity remain open.

## Build steps

1. Work in a private scratch copy. Hash the original PE and each extracted WMB/MOT source. Keep original game, mods and production AIOS untouched.
2. Install REA locally, not globally. With the existing Ghidra Java environment, run `node <local-rea>/scripts/rea.mjs function <exact-byte-synthetic-fixture.exe> <fixture-VA> --provider ghidra --json`. Configure `GHIDRA_INSTALL_DIR`, `JAVA_HOME`, `REA_ANALYSIS_PROVIDER=ghidra`, and local TEMP/TMP. Set bounded startup timeout, and record the disabled analyzers and source offsets. Preserve original instruction bytes and source digest in a receipt.
3. Confirm function boundaries separately. A long decodable run can include *multiple* real functions. Compare each fixture's source bytes with the original executable, plus REA function boundaries, mnemonics, pseudocode and return paths.
4. Parse WMB4 vertex groups, batches, skin weights, bone maps, material references and Slice6Data with established MGR2Blender2MGR routines; verify array bounds and face indices before exporting. Convert to local-only GLB/glTF.
5. Decode MOT channels, including quantized Hermite keys. Map track bone **IDs** to imported skeleton names/indices, subtract source rest translation when applying a Godot *pose offset*, and verify rotation order. Do not assume MOT's frame rate.
6. Test the custom independent Node slicing library with planes, watertightness, volume preservation and deterministic results. Pass typed JSON requests to the custom UM bridge and load the resulting fragments in Godot. The app controls `1`/`2` for skinned Raiden bodies, `3`/`4` for static parts, `M` for MOT playback, `N` for next clip, `C` for the source WMB4 proxy versus synthetic cube, `Space` for cutting, and `R` for reset.
7. Run `godot --headless --editor --path <private-godot-project> --quit` first to import GLB assets; then use explicit test scripts for bindings, source-proxy split, animated vertex deformation and interactive state. A real GUI run using the Compatibility renderer recorded two 1280×720 PNG files, but an independent visual-quality review is still pending.
8. Publish **only** field notes, commands, hashes and independently authored source examples where licensed; keep original executable bytes, original WMB/MOT/GLB data, animation curves and screenshots private.

## Verification

- Five byte-exact *synthetic fixture* REA function dossiers passed. Full-game Ghidra import did **not** pass; the external helper functions have incomplete original-program context.
- **23/23** portable JS reference tests passed (including 50 seeded cut planes, manifold/volume checks and a JSON bridge), plus **1/1** test cutting an original enemy WMB4 proxy mesh.
- Godot imported both skinned models and bound **36/36** mesh batches. Each tested clip moved **70** bone tracks and, across two sampled animation frames, CPU-side skinning measured mesh vertex displacements of approximately **0.179** and **0.092** model units for two clips.
- A Godot interactive test confirmed toggling MOT, switching clips, 2 fragment nodes after a cut, cube restore, and static fallback. The source-geometry cut test input had 12 triangles and yielded 20 triangles in each watertight result; total input volume (approximately 0.0311394854) was conserved.
- A private Godot V06 ZIP was re-extracted into a disposable location and freshly re-imported. Source-proxy slicing and animation skin tests passed again; executable SHA256 remained unchanged.
- **Not verified:** native exact cut topology or collision, live 0-to-2-to-0 activation, MGRR gameplay frame parity, original textures/UV interpolation, runtime skeletal dismemberment or a released cross-game mod.

## Gotchas

1. **Full-game import timed out.** Cause: expensive whole-program analysis. Fix: bound the investigation, instrument analyzer costs and use exact-byte fixture recovery with explicit context limits.
2. **A valid instruction range was mistaken for one function.** Cause: disassembly can cross adjacent functions. Fix: use real function boundaries and recover the owning routine for a field write.
3. **Portable cap triangulation initially failed.** Cause: cap polygon winding mismatch. Fix: triangulate in one canonical orientation, reverse opposing cap faces, and regression-test topology.
4. **Godot claimed a valid skin but a custom CPU validation found zero skinned vertices.** Cause: imported `Skin` bindings resolved via **bone names**, while the tester only used numeric indices (which were `-1`). Fix: resolve `get_bind_name()` with `Skeleton3D.find_bone()`.
5. **MOT positional channels initially displaced the rig.** Cause: source tracks were applied as Godot pose offsets without subtracting bone rest translation. Fix: apply rest-relative offsets and verify deformation at two frames; rotational parity still needs capture.
6. **Headless Godot test success did not prove render quality.** Cause: no visible framebuffer inspection. Fix: run an actual windowed renderer (ANGLE fallback if necessary), capture frames, then visually compare to a native witness.
7. **One community parser showed no cutting data structure.** Cause: it only exposed `cutdataOffset`. Fix: use the richer MGR2Blender2MGR Slice6Data parser and prove entries by pointers, topology and hashes.
8. **UM CLI didn't support a Blade Mode subcommand.** Cause: the bridge was built for this experiment, not added to UM's CLI. Fix: treat it as a custom agent-invoked JSON adapter and validate requests/responses separately.

## Assets

Original game-derived meshes/MOTs were used privately and were not committed to this repository. GLBs used diagnostic materials; WTA/WTP textures, original material assignments and complete skinned fracture are still pending. Do not publish models, source code extracted from the game binary, the private Godot archive or original animation curves.

## Open questions

Obtain original live traces of blade-mode entry and exit with identical player pointers. Follow recovered transforms into true hit/collision dispatch and triangle-buffer mutation. Pair native plane/mesh inputs and outputs with replay in Godot, compare topology and effects, then validate playable use in a separate engine. Recheck MOT rotation, timing, materials and actual visual deformation before promoting this as source-faithful.
