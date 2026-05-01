# Qwen3.6 AEON RYS MTP Notes

## Recommendation

Use the non-MTP GGUF as the default:
- `Qwen3.6-27B-AEON-RYS-MaxThinkCoder-IQ4_NL-ik-llama-custom-mixed.gguf`

Use the MTP GGUF only when the goal is to test MTP itself:
- `Qwen3.6-27B-AEON-RYS-MaxThinkCoder-MTP-IQ4_NL-experimental-mtp-imatrix.gguf`

The MTP file is worth publishing because it gives people a real Qwen3.6 RYS artifact with the MTP tail preserved. It is not replacing the main file because the non-MTP path was still faster and cleaner in our practical checks.

## What changed

The MTP GGUF keeps the next-token-prediction tail instead of stripping it during conversion/quantization:
- `qwen35.nextn_predict_layers = 1`
- `blk.69.nextn.*` tensors are present

The current fork is synced forward to the newer `ik_llama.cpp` MTP work and includes the local Qwen3.6 RYS changes used during testing:
- Qwen3.6 hybrid/recurrent layer-count handling for non-4-aligned RYS variants
- MTP graph reuse support
- MTP-aware imatrix collection so the MTP tail is covered during calibration
- experimental runtime adaptive gating and GPU-side argmax were tested locally; neither made MTP faster than no-MTP for this model
- graph-split recurrent guards for the long-context server path
- server-side identical `tool_calls` deduplication

## Tested runtime flags

The fastest MTP path we found on the `3x RTX 3090` check used graph split and a conservative draft depth:

```bash
-sm graph -mtp --draft-max 1 --draft-p-min 0.0 --draft-min 0 -b 128 -ub 32 -ctk f16 -ctv f16 -fa on -gr
```

The draft depth matters. Larger speculative settings can look attractive on paper, but the real result depends on acceptance rate, graph reuse cost, and how the recurrent/hybrid model behaves during longer outputs.

## Speed result

Same practical check, same class of runtime path:

| path | split | decode tok/s | prompt tok/s | note |
|---|---|---:|---:|---|
| experimental MTP GGUF | graph split, `-mtp --draft-max 1` | `38.16` | `196.17` | structurally valid MTP, about `65.2%` draft acceptance |
| adaptive MTP experiment | graph split, adaptive gate | `45.36` | `208.79` | closer, but still slower than no-MTP |
| recommended non-MTP GGUF | graph split | `48.68` | `214.97` | faster and cleaner in practical tests |

The result is not that MTP is useless. The result is narrower: for this specific RYS model, quant, prompt mix, and tested runtime path, the MTP file did not beat the original non-MTP release.

The 768-token check had the same direction: adaptive MTP reached about `46.95 tok/s`, while the no-MTP path reached about `48.71 tok/s`.

## Quality read

The non-MTP release stays as the standard file because it was better on the things that matter for normal use:
- higher practical reliability
- fewer long-output repeat penalties
- faster decode in the final runtime comparison
- simpler runtime path

The MTP release is useful when someone wants to inspect MTP behavior, tune draft settings, improve runtime support, or run independent measurements.
