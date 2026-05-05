# Merged GGUF LoRA Practical Canvas Summary

- Date: 2026-05-03
- Base model: Qwen3.6-27B-AEON-RYS-15-20
- Serving path: merged HF to GGUF BF16 to ik-llama llama-server with jinja and deepseek reasoning format
- Task: isolated Krita-like canvas demo with layers, brushes, transforms, and stub image generation hook

| Variant | rc | elapsed | verify | score | Notes |
|---|---:|---:|---|---:|---|
| ckpt350_s025_bf16_gguf | 124 | 900s | true | 0.9167 | pass; layers model check missed |
| ckpt386_s025_bf16_gguf | 124 | 900s | true | 1.0 | full pass |

Conclusion: both merged GGUF LoRA finalists passed the practical task. The earlier negative result applies to the HF/PEFT serving path, not to merged GGUF LoRA on ik-llama.
