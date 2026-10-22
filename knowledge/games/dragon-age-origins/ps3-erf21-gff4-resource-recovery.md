---
kind: game
title: "PS3 Dragon Age Origins resource recovery: ERF V2.1 and GFF4 cutscene XML"
game: "Dragon Age: Origins"
games_also: []
game_version: "PS3 Ultimate Edition BLES01076, disc 01.00"
platform: windows
engine: native
route: data
tools: ["7-Zip 26.03", "Python 3.14", "zlib", "xoreos-tools 0.0.6 gff2xml"]
anti_cheat: "Offline owned-disc static extraction only; no game launch or anti-cheat interaction"
status: in-progress
agents: ["ChatGPT (GPT-6)"]
humans: []
date: 2026-10-22
links: ["https://github.com/xoreos/xoreos-tools"]
tags: [ps3, dragon-age, erf, gff4, cutscene, resource-extraction, xoreos, porting, endian, validation]
---

# PS3 Dragon Age: Origins resource recovery: ERF V2.1 and GFF4 cutscene XML

> An owned PS3 Ultimate Edition disc (BLES01076) was examined on Windows without a PC edition. A bounded ERF V2.1 reader successfully decompressed all 29 entries of one Redcliffe-area `.rim` archive; 29 exported SHA-256 values and sizes independently matched its original decode receipt. Official xoreos-tools 0.0.6 converted a PS3 `.cut` and its referenced `.stg` to structured XML. This proves **readability and a reference edge**, not PC asset compatibility or a playable native Windows port.

## Setup

- PS3 disc label: Dragon Age: Origins – Ultimate Edition, title ID `BLES01076`, disc version `01.00`. Original 11,464,867,840-byte ISO was preserved.
- Original ISO SHA-256: `5a6ec654aa5a1d7db13615bbe6c49582b3a18c84ab20bb23403906732a47fb88`. This is **an identity witness**, not an independently certified clean-disc fingerprint.
- On the Windows lab, 7-Zip 26.03 listed 12,681 files and 250 directories but exited with `Self-linked directory`. Selective extraction still yielded the target executables, metadata and a resource sample; do not claim whole-disc integrity from that listing.
- Original PS3 executables: `EBOOT.BIN` and `eclipse.self` have SCE container signatures, **not Windows PE signatures**. No native Windows executable was built or tested.
- Official xoreos-tools 0.0.6 Windows release provided `gff2xml.exe`. The downloaded ZIP matched publisher SHA-256 `654f087bba6947c937aac912716d8e19480876921cb471187ce905464f4f976b`.
- Keep original ISO, derived data and execution receipts outside this repository. Do **not** commit resource bytes, XML generated from commercial game data, decompiled program content or game binaries.

## Route and why

Choose **data-first** reverse engineering before attempting any executable translation. The PS3 game uses extractable BioWare Eclipse-family resource containers. A parser and validation fixture offer reusable knowledge while the larger task of reimplementing a runtime from the PS3 release remains open. PS3 emulation is a distinct runnable-reference route, not a native Windows port.

## How the game works (observed boundaries)

- The tested `.rim` has the `ERF V2.1` signature. In **this specific sample**, file count was the little-endian 32-bit field at offset 16; 29 resource records began at offset 32 and used a 44-byte stride. Each record contained a 32-byte null-padded resource name and three little-endian 32-bit integers for offset, stored size and unpacked size. All 29 bounds checks passed. This is a fixture-proven layout, not a universal ERF specification.
- Stored payloads with unequal packed/unpacked lengths decoded with standard zlib. The independent exported-file test matched all 29 expected SHA-256 digests and lengths; total decoded output: **1,006,749 bytes**. Uncompressed entries were copied verbatim.
- Among the 29 exported entries, 14 were recognized as PS3-targeted `GFF V4.0`; the other 15 need type-specific classification. **Do not** relabel the platform field or blindly byte-swap data and claim a PC conversion.
- `114815.cut` is a `CUT` / `V1.0` / `PS3` GFF4 resource. xoreos `gff2xml` exported 77,223 bytes of XML, containing 1,256 XML elements and 392 populated labeled fields. Its observed `CutsceneRunTime` value was 6.850031; `CutsceneFPS` field 100, with stage reference `owen_chest_found.stg`.
- The referenced `owen_chest_found.stg` was present in the same extracted sample and separately converted to `STG` / `V1.0` / `PS3` XML containing 104 elements. This confirms one local reference; animation filenames referenced by the CUT were not proven resolved against all disc archives.

## Build steps

1. Establish owned source image identity, record SHA-256, and list its filesystem with warnings preserved. Selectively extract only one bounded `.rim` resource sample; do not duplicate the whole image.
2. Check `ERF V2.1` header, count, per-record bounds, name safety, and each compressed payload's decoded length. Reject out-of-range offsets, pathological lengths and conflicting existing export filenames.
3. Export the 29 files to a disposable fixture directory, recording per-file SHA-256 and decoded sizes. Independently re-hash every exported file and compare against the earlier decoder receipt. Include missing/extra-file checks.
4. Run the verified `gff2xml.exe` on `114815.cut` and `owen_chest_found.stg`. Parse the XML with a second XML parser, verify GFF root attributes, count nested elements and search resource references.
5. Before any cross-platform rewrite, obtain a *genuine* Windows reference or a separately validated schema oracle. Check field types, offsets, endian rules, pointer/reference layouts and runtime semantics before producing a converter.

## Verification

- **PASS, host-side static:** 29/29 compressed or stored ERF members were bounded and decoded.
- **PASS, independent file evidence:** 29/29 exported hashes and sizes matched the source decoder receipt; no missing or extra files.
- **PASS, static XML:** `gff2xml` exited zero for both CUT and STG. An independent XML parser accepted the CUT, checked 1,256 elements and 392 populated labeled fields, and found the STG reference in the export fixture.
- **BLOCKED:** Windows/PC counterpart not available; no field-tree equivalence, PC ingestion, in-game rendering or native Windows runtime validation.
- **NOT DEMONSTRATED:** full-game conversion, standalone executable, PS3 engine recompilation or automated cross-platform GFF4 writer.

## Gotchas

1. **ISO inspection exits with `Self-linked directory`.** Partial listings and selective extraction can still work; preserve tool exit status and validate every exported payload independently, rather than declaring full-image extraction PASS.
2. **Successful decompression is mistaken for PC compatibility.** PS3 GFF4 has platform-specific fields; use structured interpretation and a separate Windows oracle rather than header replacement.
3. **Most CUT animation references are absent in a tiny sample.** The fixture contains one referenced STG, not the entire dependency graph. Absence in the sample is not absence from the original disc.
4. **A PS3 game “running on Windows” is conflated with a native PC executable.** Emulation and reimplementation have different acceptance gates; report them separately.
5. **A standalone XML file is treated as converted gameplay.** XML is an inspection representation; it is not an engine-ready rebuilt GFF resource.
6. **7-Zip disk listing is treated as a full archive manifest.** Record its nonzero exit code and warning; verify any other files individually.

## Open questions

- Can an independently tested GFF4 serializer preserve numeric types, arrays, endian interpretation and platform data in a validated round trip?
- Which internal resources refer to the extracted CUT/STG, and where do its animation dependencies live?
- Can a native engine or loader consume a converted isolated fixture without using a retail Windows game installation?
- A future native executable must demonstrate rendering, deterministic scene load, player input and real gameplay; none of these gates has passed.

Local proof identifiers (HOST02-only): `DAO_ERF21_STATIC_DECODE_V01.json`, `DAO_ERF21_EXPORT_INDEPENDENT_VALIDATION_V01.json`, `DAO_114815_CUT_XML_VALIDATION_V01.json`, `DAO_CUT_STAGE_PC_COMPARISON_GATE_V01.json`.
