# qwen36-aeon-ik-llama

A specialized `ik_llama.cpp` fork for the exact Q4NL RYS model built in this experiment.

Primary target model:
- `Qwen3.6-27B-AEON-RYS-MaxThinkCoder-IQ4_NL-ik-llama-custom-mixed.gguf`

Model release:
- `https://huggingface.co/jackasda211233/Qwen3.6-27B-AEON-RYS-15-20-GGUF`

Source model it was derived from:
- `https://huggingface.co/AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored`

## At a glance

- this fork is specialized for the released Q4NL RYS model above
- main runtime target:
  custom `ik-llama`
- not a stock `llama.cpp` target
- project focus:
  preserve as much capability as possible inside a Q4-class RYS model for programming, reasoning, and academic work

## Speed snapshot

Exact comparison hardware:
- `6x NVIDIA GeForce RTX 5060 Ti`

| runtime | tested file | ctx | np | KV | decode tok/s | prompt tok/s | note |
|---|---|---:|---:|---|---:|---:|---|
| custom `ik-llama` fork | internal standard-typed comparison file | `4096` | `1` | `f16` | `38.90` | `162.86` | apples-to-apples comparison run |
| patched upstream-style `llama.cpp` | same internal standard-typed comparison file | `4096` | `1` | `f16` | `22.51` | `187.18` | internal comparison only |
| custom `ik-llama` fork | released custom-mixed file | `409600` | `2` | `f32/f32` | `39.37` | `164.98` | actual deployment target |

## What this fork is for

This fork exists for one concrete target:
- run the released custom-mixed Q4NL RYS model well
- keep long-context hybrid/recurrent serving stable
- support the custom mixed GGUF layout used by the release file
- tune for the six `RTX 5060 Ti` deployment that was actually used in the experiment

## Why no public `llama.cpp` file

We are not publishing a separate standard `llama.cpp` model file as part of this release.

Why:
- the main model this project is about needs the forked `ik-llama` runtime
- the internal standard-typed comparison path was only validated on a patched upstream-style `llama.cpp`, not on clean stock mainline
- because a special runtime was still required either way, we did not think it was worth presenting a second public file as if plain `llama.cpp` support were the point of the project

So the intended path is:
- use this fork
- use the released `ik-llama-custom-mixed` GGUF

## Hyper-focused project

This was a deliberately narrow project.

The target was not “best general chat model”.
The target was:
- strongest Q4-class English-first model we could get for coding, reasoning, and academic work
- derived from the AEON uncensored branch
- quantized/calibrated with a corpus heavily biased toward reasoning math, code, technical prose, and experiment artifacts

## Why the fork exists

This is not a generic llama.cpp fork.

The released model path depended on:
1. Qwen3.6 hybrid/recurrent loader fixes for non-4-aligned RYS variants
2. graph-split serving fixes for long-context recurrent/hybrid runs
3. quantization/runtime support for the custom mixed GGUF tensor layout used by the release model

Without those changes, stock upstream runtimes hit real failures in the experiment.

## Supported GPUs

The tested build used:
- `CMAKE_CUDA_ARCHITECTURES=86;120`

That covered the tested hardware:
- `RTX 3090` class Ampere (`SM 8.6`)
- the `RTX 50-series` cards on the experiment machine (`SM 12.0`)

If you use other NVIDIA architectures, rebuild for your own SM targets.
