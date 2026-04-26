# qwen36-aeon-ik-llama

A specialized `ik_llama.cpp` fork and release notes for the Qwen3.6-27B AEON RYS `15,20` experiment.

This repo exists for one concrete target:
- run the Qwen3.6-27B AEON-derived `15,20` RYS model well in GGUF form
- keep long-context hybrid/recurrent serving stable
- keep the high-performing custom IQ4_NL quant usable
- tune for the six `RTX 5060 Ti` deployment that was actually used in the experiment

## What is special here

This is not a generic llama.cpp fork.

The published model path depends on three kinds of changes:
1. Qwen3.6 hybrid/recurrent loader fixes for non-4-aligned RYS variants
2. graph-split serving fixes for long-context recurrent/hybrid runs
3. quantization/runtime support for the custom mixed GGUF tensor layout used by the main `ik-llama` release model

Without those changes, stock upstream runtimes hit real failures in this experiment:
- stock upstream `llama.cpp` rejected the custom mixed quant with `invalid ggml type 140`
- even the standard-typed fallback quant initially failed loader assumptions on the non-4-aligned `15,20` layer pattern
- upstream tensor split also hit a warmup assert on this hybrid model path

## Why `15,20`

This was not chosen blindly.

AEON-specific strict validation put `15,20` at the top of the balanced shortlist:
- `15,20`: `0.809394`
- `31,34`: `0.809010`
- `11,14`: `0.808214`
- AEON base: `0.799945`
- `30,35`: `0.796181`

The deeper-reasoning `11,14` branch was also strong, but `15,20` was the cleaner quantization target and the better release candidate for a practical Q4 deployment.

## Main release model

Primary release target:
- `Qwen3.6-27B-AEON-RYS-15-20-IQ4_NL-ik-llama.gguf`

This is the main model the fork is for.

Characteristics:
- AEON-derived / uncensored source branch
- 69-layer `15,20` RYS variant
- English-first calibration corpus
- custom `ik-llama` mixed quant path
- tuned around programming, reasoning, and academic-style work within Q4 constraints

## Release variants

There are two useful GGUF variants for this model family:

1. `ik-llama` custom quant
- fastest and best-supported path in this repo
- uses the custom mixed GGUF tensor extension accepted by this fork
- this is the recommended runtime/model combination

2. standard-typed fallback quant
- uses upstream-compatible tensor types only
- useful as a fallback artifact and comparison point
- still experimental for this exact non-4-aligned hybrid `15,20` layout
- not the main recommendation

## Actual benchmark snapshot

All numbers below came from the real six `RTX 5060 Ti` system.

### Same standard-typed GGUF, same prompt, different runtime

Config:
- 6x `RTX 5060 Ti`
- `ctx=4096`
- `np=1`
- `KV=f16`
- prompt: 24 tokens
- generation: 128 tokens

Results:
- custom fork, `split-mode graph`: `38.90 tok/s` decode, `162.86 tok/s` prompt
- patched upstream-style `llama.cpp`, `split-mode layer`: `22.51 tok/s` decode, `187.18 tok/s` prompt

Decode speedup for the custom fork on the same standard-typed GGUF:
- about `1.73x`

### Long-context deployment target

Custom fork main deployment:
- model: custom `ik-llama` quant
- `ctx=409600`
- `np=2`
- `204800` tokens per slot
- `KV=f32/f32`
- `cache-ram=61440`
- `split-mode graph`

Measured result:
- `39.37 tok/s` decode
- `164.98 tok/s` prompt on the short probe

Patched upstream-style fallback on the standard-typed quant at the same long-context serve target:
- `22.36 tok/s` decode
- `161.11 tok/s` prompt on the short probe

### Failure notes that matter

Observed upstream limitations during this release prep:
- stock upstream `llama.cpp` rejected the custom quant: `invalid ggml type 140` on `blk.3.attn_v.weight`
- stock upstream loader assumptions also broke on the standard-typed fallback until the recurrent-layer detection patch was applied
- upstream `split-mode tensor` aborted during warmup on this hybrid model path

## Quality snapshot

From the actual `15,20` BF16 vs custom IQ4_NL validation:

- `math_16`: `0.8421 -> 0.7897`
- `eq_16`: `0.7123 -> 0.7111`
- `math_4`: `0.4851 -> 0.5170`
- `gsm8k_5`: `0.8800 -> 0.8800`

Summary:
- mixed general/reasoning overall mean: `0.7299 -> 0.7244`
- overall delta: about `-0.0055`
- that is under `1%` overall on this small mixed probe

Interpretation:
- general arithmetic does drop
- EQ-style output stayed essentially flat
- the tiny reasoning probes did not show collapse
- this is why `15,20` became the practical Q4 release target

## Supported GPUs

The tested build on the experiment machine used:
- `CMAKE_CUDA_ARCHITECTURES=86;120`

That covered the tested hardware:
- `RTX 3090` class Ampere (`SM 8.6`)
- `RTX 50-series` cards on the experiment box (`SM 12.0`)

Do not treat the shipped binary configuration as universal.

If you use other NVIDIA architectures, rebuild for your own SM targets, for example:

```bash
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=89
cmake --build build -j
```

For mixed machines:

```bash
cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=86\;89\;120
cmake --build build -j
```

## Build notes

The speed-tuned deployment binary used in the experiment was built with:
- `GGML_CUDA_COMPRESSION_MODE=speed`
- `GGML_CUDA_FORCE_MMQ=OFF`
- `GGML_CUDA_FORCE_CUBLAS=OFF`

The winning six-GPU serve shape used:

```bash
CUDA_VISIBLE_DEVICES=<six 5060 Ti GPUs> ./build_50_speed/bin/llama-server   -m Qwen3.6-27B-AEON-RYS-15-20-IQ4_NL-ik-llama.gguf   -ngl 999 -fa on   -ctk f32 -ctv f32   -sm graph   -np 2 -c 409600   -cram 61440   -b 512 -ub 128   --jinja --reasoning-format deepseek
```

## Hugging Face

The model release is intended to live on Hugging Face with a README that links back to this fork and explains the difference between:
- the main `ik-llama` custom quant
- the fallback standard-typed quant

## Scope

This repo is specialized.

If you want the highest-confidence path for this exact model, use this fork plus the main custom quant.
If you want maximum generic compatibility, treat the standard-typed fallback as experimental and benchmark it yourself on your runtime branch.
