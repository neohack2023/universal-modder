# Patch Elements Inferno — real HD 520 GPU experiment

Date: 2026-11-16 (EST)
State: SOURCE-BOUNDED / LOCAL EXECUTION VERIFIED / NOT AIOS CANON
Scope: Drive-registered pc-game-re-modding; Host02 local execution receipts; GitHub source is implementation truth.
Sources: https://git.patch.gg/patch/elements.git at commit 46c4142; source MIT license; upstream https://github.com/Humpalumps/ultra-elements.

## Question and method
Can actual Patch Elements Inferno fire/smoke/combustion render via standard Edge on the Intel HD Graphics 520 at low settings, and what added GPU time does it take relative to the same uncast Elements scene?
Host: DaltonsLaptop574, Intel HD Graphics 520 driver 22.20.16.4836, WebGL2 -> ANGLE -> D3D11.
Real code: createElements() with actual elements.render(dt) and Inferno casts on frames 9, 77 using deterministic seeds.
Controls: 640x360, q=low, pixelRatio 0.6, Q.auto.emission 0.42, Q.auto.steps 0.65, fixed arena/camera, autoQuality disabled. Uncast baseline kept all settings and warmSpell but omitted casts.
Instrumentation: EXT_disjoint_timer_query_webgl2 around the full Elements frame every 12 frames, asynchronous polling; requestAnimationFrame pacing; CPU submission; WebGL context loss/error; canvas screenshots; display reset Event 4101 query and Windows adapter status.

## Results
| Metric | Uncast baseline | Two Inferno casts |
| --- | ---: | ---: |
| Frames | 132 | 132 |
| GPU samples | 11 | 11 |
| GPU timer median | 5.145750 ms | 7.171916 ms |
| GPU timer p95 | 5.828833 ms | 7.944749 ms |
| rAF median | 16.7 ms | 16.7 ms |
| rAF p95 | 16.8 ms | 16.9 ms |
| WebGL context losses | 0 | 0 |
| Recorded JS errors | 0 | 0 |

Measured single-run median delta: +2.026166 ms (39.4% higher GPU time), inferno compared with no casts. Both conditions completed. Driver status still OK. No Windows display-reset event 4101 returned for the inspection window.
Visual inspection of actual Edge screenshots: empty arena before cast; fire column, scorched ground, smoke and sparks in frames 67 and 98. JPEG center crop differs from baseline; separately retained photographs prove visible change.
A first cold attempt hit the original 2.5s first-frame safety abort. It also had a CORS collector naming defect, so no valid telemetry was collected. Corrected the collector and used a 10s first-frame limit on subsequent complete tests; first-frame cold-start risk remains unresolved.

## Evidence and hashes
Host02 receipt root: C:/AIOS/10_SCRATCH/UNIVERSAL_MODDER_DEEP_PASS_20261116/elements_bench_receipts/
- inferno_v01.json SHA256 97d5aa8ddfa43693f6248ff8f6f93bbaadea67d57da1761b1133e0df72eb5607
- uncast_baseline_v01.json SHA256 437e4acb70d132c2dbe1606f310649eaf0f179ced39f84eae4a5bd52c3d8f864
- inferno_v01_frame67.jpg SHA256 e0861492c6a991a2489a92a1cb63a6a2ee9af94663a94ed27cd1c54dac1a370f
- inferno_v01_frame98.jpg SHA256 f060ff568752ee4bb97a6fed7800743a64d10d6c190be9f33f36739786908a92
- uncast_baseline_frame98.jpg SHA256 016fd00bf9314d5b8b7dba1b9e63be95786c1d2f36ef77dca0880b098959a828
- comparison_v01.json, evaluated by evaluate_elements_visuals.py, retained outside the repository
Harness scripts retained in same scratch root; no original source, installed games or driver binaries changed.

## Interpretation and limits
Status: LOW_TIER_WEBGL2_RENDERING_FEASIBLE_ON_THIS_HOST (small evidence sample).
This supports a genuine, visible, low-tier combustion-effect rendering test with incremental GPU cost. It does NOT demonstrate an isolated combustion solver speedup, production stability, 60fps game performance, D3D12 support, UnderdogRuntime integration, or cross-game portability.
One full run per condition; only eleven GPU samples each. Query surrounds full Elements renderer including post-processing and scene. Vsync masks possible headroom. GPU memory/temperature and shader module-level timings not measured. No driver-reset event observed is not a reliability guarantee.

## Next experimental gate
Three paired A/B repeats with exact per-query frame labels, first-run cold compilation timing, isolated FluidVolume and particle timing, and GPU memory-pressure monitoring. Then a controlled low-to-medium quality sweep. Compare against existing Underdog benchmarks using matched scenes and metrics; do not claim math innovation from this one system test.
