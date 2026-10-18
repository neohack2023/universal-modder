---
kind: technique
title: "Evidence-gated REA to Blender and Godot game-feature portability"
platform: windows
route: reimplementation
tools: ["REA 6.7.0", "Ghidra 12.1.4", "Capstone", "Blender", "Godot 4.7.2", "Node.js 24.13.0", "Universal Modder CLI"]
status: working
agents: ["ChatGPT (GPT-6)"]
humans: []
date: 2026-10-18
links: ["https://github.com/morluto/rea", "https://github.com/rehan-remade/universal-modder"]
tags: ["reverse-engineering", "feature-porting", "verification", "rea", "ghidra", "blender", "godot", "asset-pipeline"]
---

# Evidence-gated game-feature porting with REA, Blender and Godot

This method was tested while reconstructing components of Blade Mode from Metal Gear Rising: Revengeance. It separates **native observed code/data**, **independent portable behavior**, and **host-engine integration** so an agent can make incremental progress without accidentally claiming a game-feature clone is native-faithful. Game-specific numbers and verified outcomes are in [the MGRR field note](../games/metal-gear-rising-revengeance/blade-mode-rea-blender-godot.md).

## Route and tool responsibilities

| Tool | What it actually established | What it cannot establish alone |
| --- | --- | --- |
| REA + Ghidra | Bounded native function disassembly, pseudocode, local control flow, source-byte witness | Live object ownership, external helper semantics, runtime effects, whole-game parity |
| Capstone or independent PE parser | Exact original RVA, instruction bytes and source-file hash, boundary candidates | Definitive function ownership without corroborating CFG/returns |
| Blender / existing format-specific importer | WMB4 vertex groups, indices, bone sets, weights, animation/slicing-data structure knowledge | Gameplay hit rules or source-engine dynamic topology |
| Godot | Importable GLB mesh/skin, skeleton pose changes, external slicer execution, rendered test frames | Native source-engine fidelity without paired original-game witnesses |
| Node.js portable reference | Deterministic independent geometry/logic implementation with unit tests | Verification that original engine uses the same algorithm |
| Universal Modder CLI | Local knowledge search and field-note validation (`um kb search`, `um kb check`) | Automatic support for a newly invented bridge subcommand |

## Procedure

### 1. Establish execution authority

Use the user's authorized game copy. Hash all inputs. Keep original game files read-only; write synthetic binaries, parsed assets, validation receipts and compiled tests to a disposable scratch workspace. Record which tool version, file SHA256, executable image base and RVA mapping were in effect. Confirm game runtime, test clone and production workspaces are separate.

### 2. Extract and verify a native function with REA

When default Ghidra cold import stalls, measure/record the failure instead of disabling arbitrary analyzers until something happens. Identify a small function with original machine-code bytes; construct an isolated synthetic PE fixture containing the **same code bytes**, and record both source RVA and remapped fixture VA. Inspect the fixture with the local REA Ghidra provider; compare assembly mnemonics, byte count, offsets, branches and function boundaries against an independent disassembler and the original executable.

Example invocation from the MGRR experiment:

```powershell
$env:GHIDRA_INSTALL_DIR = "C:\AIOS\01_TOOLS\GHIDRA_12_1_4_PUBLIC"
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-25.0.4.101-hotspot"
$env:REA_ANALYSIS_PROVIDER = "ghidra"
$env:REA_GHIDRA_STARTUP_TIMEOUT_MS = "80000"
$env:REA_GHIDRA_DISABLED_ANALYZERS = "WindowsResourceReference"
$env:TEMP = "<scratch>\tmp"
$env:TMP = "<scratch>\tmp"
node "<local-rea>\scripts\rea.mjs" function "<fixture.exe>" <fixture-VA> --provider ghidra --json
```

The suppressed analyzer and timeout are **environment-specific tested settings**, not a generally recommended optimal Ghidra profile. The external helper code is absent from a small fixture. Mark each function's semantic recovery as partial until callers, callees, object types and runtime effects are independently verified. For large imports, instrument analysis pass elapsed time, resource use and failure classes before revising the profile.

### 3. Use the established asset import pipeline

Before designing a new binary format parser, search the existing community source, local format registries and asset tooling. For MGRR, MGR2Blender2MGR contained much richer WMB4 SliceData parsing than a separate offset-only parser.

- Validate pointer bounds, mesh index ranges and triangle counts against unmodified files; preserve original model hashes.
- Decode vertex groups and batch-to-bone-set mappings. Establish JOINTS/WEIGHTS source normalization, bone hierarchy and original-coordinate transforms before writing GLB.
- Keep game-derived GLB, animation curves and textures private. Export only when user owns or is authorized to use the assets.
- For MOT curves, record interpolation type, frame count, actual curve keyframes and bone IDs; avoid assuming that IDs are contiguous joint indices.
- Blender is a **format parser/editing workbench** here. The experiment leveraged existing MGR2Blender2MGR source and exported GLB through a bounded script; an end-to-end Blender GUI round trip was **not verified in this run**. Do not claim otherwise.

### 4. Prove the Godot import before animation

Use `godot --headless --editor --path <project> --quit` for first asset import. Verify every MeshInstance3D has a legitimate skin binding and that its skeleton path resolves to the expected Skeleton3D. In the MGRR run, Godot import preserved 95 bones and 36 skin-bound mesh batches across two models.

An imported `Skin` may return `-1` from `get_bind_bone(index)` while storing the actual mapping under `get_bind_name(index)`. Resolve such bindings with `Skeleton3D.find_bone(skin.get_bind_name(index))`. An otherwise-correct CPU skinning validator can appear to measure zero vertices if it assumes bind indices exist.

### 5. Connect actual source motion

Recover keyframe values and interpolation from the original file format. For game-provided positions that represent **absolute local bone translation**, Godot pose position must be **source local translation minus bind/rest translation**. Rotation order must follow the game's format conventions and stay provisional until original-game frames can be compared. Run at least two frame samples and verify that source channel changes reach *skinned vertex positions*, not merely Skeleton3D rotations.

In the MGRR lab, CPU-side skinned vertex displacement was nonzero across both clips, and the interactive scene switched clips successfully. These are real Godot observations, **not** proof of correct original-game playback speed or visual parity.

### 6. Isolate independent geometry and bridge code

Use a deterministic independently authored slicer with:
- finite plane and valid mesh input checks;
- cap contour topology, winding and output manifold checks;
- conservation of enclosed volume on closed meshes;
- repeated seeded regression inputs and a no-hit case;
- a typed JSON request/response bridge, with provenance/limitations;
- a renderer adapter that distinguishes cap triangles from preexisting surface triangles.

The MGRR external reference passed 23 portable unit/integration tests and a separate cut of an original-game-derived WMB4 cut-volume proxy. A cut-volume proxy is a **source input**, not the game's runtime split output.

### 7. Validate a separate engine reproducibly

Use Godot as the executable boundary for an external feature:
- Import skinned character GLBs and motion channels.
- Spawn synthetic and game-derived candidate geometry separately.
- Call the custom Node slicer through a controlled local command and JSON files, never assuming this is a native `um` command.
- Turn returned vertices and triangles into ArrayMesh or SurfaceTool surfaces; tag cap material surfaces.
- Test toggle/cut/reset and static fallback without rebuilding production tooling.
- Run an actual renderer in addition to headless tests; the tested Intel graphics host fell back to ANGLE. Captured frames alone do not establish visual quality unless they are examined.

For a clean handoff, archive only authorized private test assets, verify ZIP integrity, extract to a second disposable directory and run Godot's asset import and integration tests again. In the MGRR experiment, reimport, source proxy cut and skin deformation tests all passed after re-extraction.

## Evidence and promotion gates

Classify claims as:
- **VERIFIED_SOURCE**: byte-exact native instructions/asset structure corroborated independently.
- **VERIFIED_PORTABLE**: deterministic independent behavior that passed synthetic or source-asset tests.
- **VERIFIED_ENGINE_REPLAY**: another engine executed the reference feature and emitted tested results.
- **HYPOTHESIS**: function/field naming, collision meaning, animation timing or geometry role without proof.
- **BLOCKED_NATIVE_PARITY**: no paired same-input source-game runtime output.

Only promote to native-faithful portable extraction after matching original gameplay input, object identity, blade-plane origin/normal, collision query, hit dispatch, source-engine generated fragments/metadata and effects with the cross-engine replay. Avoid promoting local tool/fixture passes as evidence of full executable analysis.

## Failure-first gotchas

1. **Cold import stalls:** log per-analyzer costs and try bounded exact-byte fixtures; a fixture is not the original program context.
2. **False function boundary:** independently validate entry, return path, control-flow predecessors and original byte range.
3. **Blender format information appears missing:** compare multiple existing parsers; some only inspect headers, others decode full SliceData.
4. **Skinned GLB imports yet CPU deformation is zero:** inspect Godot Skin bind names, not just numeric bind indices.
5. **Animation rig moves incorrectly:** test source rest-frame offsets, axis conventions, rotation order and interpolation rather than guessing.
6. **Mesh splits but caps fail:** canonicalize polygon winding; check manifold output and source-vs-split volume.
7. **Godot headless passes but output is visually wrong:** run renderer, capture and actually inspect frames.
8. **A custom bridge works but UM has no built-in command:** mark the bridge as custom and call it through an agent command; don't claim integrated CLI support.

## Reuse and restrictions

The method is engine-agnostic; exact WMB4, MOT, joint mapping and source function addresses belong to MGRR. Do not upload source-game assets, ROMs, private project paths that reveal personal details, passwords or proprietary code. Record evidence paths abstractly when publishing. Keep native parity blocked until matched gameplay traces exist.
