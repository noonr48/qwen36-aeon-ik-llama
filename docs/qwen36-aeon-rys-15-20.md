# Qwen3.6 AEON RYS 15,20 Release Notes

## Model intent

This release is the outcome of a layer-window search on Qwen3.6-27B AEON, followed by quantization screening.

The goal was not just to add layers. The goal was to find a Q4-sized artifact that preserved useful reasoning and output quality better than naive depth edits.

## What was tried

The experiment scanned and compared multiple RYS windows and meshes.

Strong AEON candidates included:
- `15,20`
- `11,14`
- `31,34`
- `24,32`
- `30,35`
- several mesh combinations

What mattered in the end:
- `15,20` won the balanced AEON validation slice
- `11,14` looked strongest on the reasoning-first probe
- `15,20` held up better as a practical IQ4_NL release target

## Why the release target is not `11,14`

`11,14` remained an important research branch, but for release work there were two practical problems:
- it was the less forgiving quantization target
- the deployment/runtime path was more troublesome

So the public Q4 release centered on `15,20` instead.

## Runtime conclusions

Four conclusions came out of the runtime work:

1. stock upstream compatibility was not enough
- the non-4-aligned hybrid pattern needed loader fixes
- the main custom quant needed the fork’s custom tensor support

2. graph split mattered
- the custom fork’s graph-split path was substantially faster than patched upstream layer split on the same standard-typed GGUF

3. long-context stability needed explicit fixes
- recurrent checkpoints had to be disabled on graph split
- prompt batching across slots had to be serialized for recurrent/hybrid models under graph split to keep the `200k/slot` FP32 deployment stable

4. MTP is worth exposing, but not as the default path
- a true MTP GGUF was added for people testing Qwen3.6/Qwen3.5 MTP support in `ik_llama.cpp`
- the artifact keeps `qwen35.nextn_predict_layers = 1` and the `blk.69.nextn.*` tensors
- the best checked MTP path reached about `35.06 tok/s` on `3x RTX 3090`, while the non-MTP graph-split path reached about `48.64 tok/s`
- practical quality checks also favored the original non-MTP file because it showed fewer long-output repeat penalties

## Practical recommendation

If someone wants to use this exact model family seriously:
- use the custom fork in this repo
- use the main custom quant release
- treat the MTP GGUF as an experimental/runtime-testing artifact
- rebuild for your own SM targets if your GPU architecture differs
- do not assume stock upstream `llama.cpp` will behave the same on this non-4-aligned Qwen3.6 hybrid variant
