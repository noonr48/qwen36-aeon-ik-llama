# qwen36-aeon-ik-llama

A specialized `ik_llama.cpp` fork and release package for the Qwen3.6-27B AEON RYS `15,20` branch.

Public release codename: `MaxThinkCoder`.

This repo exists for one concrete target:
- run the Qwen3.6-27B AEON-derived `15,20` RYS model well in GGUF form
- keep long-context hybrid/recurrent serving stable
- keep the highest-performing custom IQ4_NL quant usable
- tune for the six `RTX 5060 Ti` deployment that was actually used in the experiment

## Public release files

The public Hugging Face release uses two clearly separated artifact names:

1. `Qwen3.6-27B-AEON-RYS-MaxThinkCoder-IQ4_NL-ik-llama-custom-mixed.gguf`
- primary release file
- for this custom `ik-llama` fork
- uses the custom mixed tensor layout validated in the real deployment
- recommended if you want the actual fast path from this experiment

2. `Qwen3.6-27B-AEON-RYS-MaxThinkCoder-IQ4_NL-standard-typed-fallback.gguf`
- secondary fallback file
- standard-typed compatibility artifact
- useful for patched `llama.cpp` / research comparison work
- not the main recommendation for end users

## Why the main focus was `ik-llama`

The mainline target in this release was always the custom `ik-llama` path.

Why:
- in earlier RYS experiments, the `ik-llama` quant path consistently looked better at preserving reasoning/output quality than standard `llama.cpp`-style quantization
- for this `Qwen3.6` branch, the real BF16-vs-Q4 validation was run against the custom `ik-llama` quant, not the fallback
- the runtime optimization work was also centered on the custom fork, because that is where the best speed and the best long-context stability landed

So the release should be read as:
- `ik-llama-custom-mixed` = main quality/performance target
- `standard-typed-fallback` = compatibility and research artifact

The fallback exists because some users will still want a more standard-typed file, not because it was the primary quality target in this experiment.

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
- `Qwen3.6-27B-AEON-RYS-MaxThinkCoder-IQ4_NL-ik-llama-custom-mixed.gguf`

Characteristics:
- AEON-derived / uncensored source branch
- 69-layer `15,20` RYS variant
- English-first imatrix calibration corpus
- custom `ik-llama` mixed quant path
- tuned around programming, reasoning, and academic-style work inside a Q4-class footprint

## Imatrix calibration focus

The quantization was not calibrated on generic chat filler. The imatrix corpus was:
- file: `/home/benbi/qwen36_official_base/imatrix/qwen36_reasoning_calibration_v2.txt`
- size: `4,736,109` characters across `87,507` lines
- coarse blank-line chunks: `15,540`

Heuristic chunk breakdown from the actual file:
- `math_reasoning`: `5,688` chunks, `1,706,070` chars (`36.0%`)
- `code_technical`: `3,518` chunks, `1,343,392` chars (`28.4%`)
- `experiment_docs`: `808` chunks, `224,169` chars (`4.7%`)
- `writing_chat`: `387` chunks, `164,097` chars (`3.5%`)
- `other`: `5,139` chunks, `1,249,396` chars (`26.4%`)

Important note:
- the `other` bucket is mostly technical continuation text split off from scripts, methodology notes, and structured reasoning material
- so the simple heuristic undercounts the true technical/reasoning share

Practical read:
- the corpus was heavily biased toward math-style reasoning, code, technical prose, and experiment artifacts
- it was only lightly biased toward generic social chat
- this is why the release is best framed as a programming / reasoning / academic-work Q4, not a general-chat personality tune

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

Comparison on the same standard-typed GGUF:

| runtime | split mode | decode tok/s | prompt tok/s | note |
|---|---|---:|---:|---|
| custom `ik-llama` fork | `graph` | `38.90` | `162.86` | fastest validated path |
| patched upstream-style `llama.cpp` | `layer` | `22.51` | `187.18` | same GGUF, slower decode |

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

Long-context comparison:

| runtime / file | context target | decode tok/s | prompt tok/s |
|---|---|---:|---:|
| custom fork + `ik-llama-custom-mixed` | `409600`, `np=2`, `f32/f32` KV | `39.37` | `164.98` |
| patched upstream-style fallback + `standard-typed-fallback` | `409600`, `np=2`, `f32/f32` KV | `22.36` | `161.11` |

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
CUDA_VISIBLE_DEVICES=<six 5060 Ti GPUs> ./build_50_speed/bin/llama-server   -m Qwen3.6-27B-AEON-RYS-MaxThinkCoder-IQ4_NL-ik-llama-custom-mixed.gguf   -ngl 999 -fa on   -ctk f32 -ctv f32   -sm graph   -np 2 -c 409600   -cram 61440   -b 512 -ub 128   --jinja --reasoning-format deepseek
```

## Hugging Face

The model release is published at:
- https://huggingface.co/jackasda211233/Qwen3.6-27B-AEON-RYS-15-20-GGUF

That README links back to this fork and explicitly maps:
- `ik-llama-custom-mixed` -> custom fork, main recommendation
- `standard-typed-fallback` -> compatibility/research artifact

## Scope

This repo is specialized.

If you want the highest-confidence path for this exact model, use this fork plus the `ik-llama-custom-mixed` GGUF.
If you want maximum compatibility work, treat the `standard-typed-fallback` GGUF as secondary and benchmark it on your own runtime branch.
