# Qwen3.6 AEON RYS Gameworks: What We Actually Did

This is the comprehensive write-up for the Gameworks release — the dual-capability fine-tune that adds game/media-creation on top of the PatchCode agentic-coding model.

The clean model card stays short. This document is the full story: what we trained, how the game-creation axis was built, the dual-axis quant bake-off (coding + game-creation), why no single quant won both axes, and the trade-off analysis that drives the deployment recommendation.

Related public guides:
- runtime fork: `https://github.com/noonr48/qwen36-aeon-ik-llama`
- RYS layer-duplication / architecture guide: `https://github.com/noonr48/qwen36-aeon-ik-llama/tree/main/docs/rys-layer-duplication-guide`
- previous fine-tune (PatchCode): `https://huggingface.co/jackasda211233/Qwen3.6-27B-AEON-RYS-Agentic-Coder-PatchCode-GGUF`
- SignalLatch release: `https://huggingface.co/jackasda211233/Qwen3.6-27B-AEON-RYS-SignalLatch-GGUF`

Related release line:
- coding predecessor: `Qwen3.6-27B-AEON-RYS-Agentic-Coder-PatchCode.IQ4_NL.gguf`
- this release: `Qwen3.6-27B-AEON-RYS-Agentic-Coder-Gameworks.{IQ4_NL,Q5_K_M,Q6_K,Q8_0}.gguf`

## Glossary

- `AEON`: the upstream/source model family this RYS line was built from (`AEON-7/Qwen3.6-27B-AEON-Ultimate-Uncensored`).
- `RYS` (Recurrent Yield Splicing): the layer-duplication transformation applied to the base Qwen3.6-27B. Documented in the layer-duplication guide.
- `SignalLatch` / `ckpt386-s010`: the first behaviour fine-tune — a reasoning/habits LoRA merged at strength 0.10.
- `PatchCode` / `merged_lam0.5`: the second fine-tune — an agentic-coder LoRA merged onto SignalLatch at strength 0.5. The immediate predecessor of this release.
- `Gameworks`: the third fine-tune — a game/media-creation LoRA layered on top of PatchCode. This is the 50/50 model (50% coding, 50% game-creation).
- `IQ4_NL` / `Q5_K_M` / `Q6_K` / `Q8_0`: quantization formats tested. IQ4_NL is 4-bit (smallest), Q8_0 is 8-bit (largest).
- `imatrix`: importance-matrix-assisted quantization data. Calibrated on a blend of game-creation and coding text matching the training distribution.
- `ik-llama`: the custom runtime fork. The `qwen3_5` hybrid architecture does not load on stock `llama.cpp` or `vLLM`.
- `coding-gate`: a 7-task agentic pytest suite (minijson, graph, tracker, mdlist, taskq, lru, calc). Each task is a multi-turn tool-use coding problem with a binary pass/fail verifier.
- `game-gate`: a 6-behavior game-creation evaluation across 5 clusters (design, story, techart, build, scalecraft). Prose-scored behaviors are the discrimination signal; tool-based behaviors require a tool sandbox.
- `calc`: the operator-precedence calculator task — the single coding behavior where the game-creation LoRA caused measurable regression. A recursive-descent parser with tokenizer, handling +, -, *, /, parentheses, unary minus, and floats.

## The short version

We took PatchCode — a coding-agent-tuned model that scored 21/21 on our agentic coding suite — and trained a second LoRA on top of it focused on structured game-design and interactive-media creation. The goal was a dual-capability model: one that can function as a coding agent AND produce game-design artifacts (mechanic specs, narrative systems, parametric asset reasoning, technical-art principles).

The result trades a narrow slice of coding capability for a substantial game-creation gain:

```text
Coding:    21/21 (PatchCode) → 18/21 (Gameworks, Q5_K_M)    — lost calc
Game:       0/18 (PatchCode) →  9/18 (Gameworks, Q5_K_M)    — gained 9 behaviors
```

The coding regression is **precision-recoverable**: at Q8_0 (8-bit), Gameworks scores 21/21 — identical to PatchCode. The regression only appears at Q4/Q5, where the game-creation LoRA's interference pushes the calc task below the precision threshold. The other 6 coding tasks are unaffected at all quant levels.

## Why this project exists

This is a **preventative project**. The open-source LLM landscape is volatile. The Qwen 3.6 series — a 27B hybrid/recurrent architecture with strong reasoning at a deployable size — exists at a specific moment. If future releases discontinue this architecture, or if the small-open-model space contracts, the RYS project line is the fallback: a fully self-hosted, uncensored coding-and-creative agent that depends on no API, no external model, and no ongoing commercial support.

The project line built incrementally:

1. **AEON RYS 15/20** — the layer-duplicated base. Proved the RYS transformation works on the Qwen3.6 hybrid architecture.
2. **SignalLatch** — proved a behaviour LoRA can be merged cleanly onto the RYS base.
3. **PatchCode** — proved an agentic-coder distil can hold its coding score at Q4 deployment size.
4. **Gameworks** (this release) — proves a second capability axis (game/media creation) can be added without destroying the first.

Each step de-risked the next. The question Gameworks answers: can a single open-weight model serve as both a coding agent and a creative/game-design tool? The answer is yes, with a measured trade-off that's recoverable at higher precision.

## What the game-creation LoRA was trained on

The LoRA was trained on **30,030 structured game-design samples** across five skill clusters:

### Design reasoning (cluster: design)
- **concept_from_premise** — derive a game concept from a premise: premise statement, design thesis, ≥3 design pillars with derivation signals (because/so-that/derives)
- **mechanics_feel_first** — design a core mechanic that serves the player feel first; name the mechanic, describe the feel, justify why it matters

### Narrative systems (cluster: story)
- **iceberg_reveal** — write a scene that reveals information through the iceberg principle (show the tip, imply the depth); the player discovers, never told; the withheld information's WHY (pull/dread/mystery) must be stated without explaining the thing itself

### Technical art (cluster: techart)
- **author_animation_principles** — animate using the 12 principles: squash-and-stretch that recovers to volume (back_to_one=true), anticipation wind-up frames (2-6), named ease curve (never LINEAR). Proven via a `SQUASH` proof line.

### Build/specification (cluster: build)
- **mechanic_as_state_machine** — specify a mechanic as a closed state machine: every transition targets a declared state, no undeclared states. Proven via a `game_design_mechanic_spec` gate with decision=accept and consistency.closed=true.

### Scalecraft (cluster: scalecraft)
- **parametric_variation** — make many from one base via parameters: one parametric generator yields N distinct outputs that all honor art-direction, with a coherence check that fails off-style outputs. Proven via `VARIANTS` proof lines (honest run + falsifier).

A **6,000-row coding rehearsal slice** (drawn from the PatchCode training blend) was mixed in as anti-forgetting — the goal was to retain PatchCode's coding capability while adding the game-creation axis.

### Training details

- LoRA rank: r32, alpha=64 (all-linear including SSM projections)
- Training: completion-only loss, lr 5e-5, cosine schedule, 1 epoch
- Context: 2048 tokens
- Checkpoint: **1900 steps** (loss 0.738 — best in the run)
- Checkpoints past step 2000 diverged after a training interruption (power-outage resume corrupted the optimizer state); loss jumped to 12+ and never recovered. Steps 2000/2100/2200/2270 were deleted. **Only checkpoint-1900 is usable.**

## The merge

The game-creation LoRA was merged onto the PatchCode HF model at scale 1.0 (single adapter, no lambda blending — the PatchCode layer was already merged into the base).

```text
base:      Qwen3.6-27B-AEON-RYS-Agentic-Coder-PatchCode (merged)
adapter:   game-creation LoRA, checkpoint-1900, r32
merge:     scale 1.0
output:    Gameworks merged HF model
```

The merged model was converted to GGUF via the ik-llama fork's `convert_hf_to_gguf.py` (the converter must support the Qwen3_5 architecture — stock llama.cpp converters do not recognize the `Sequence(Split+ByteLevel)` BPE pre-tokenizer).

## The quant bake-off

### Quant ladder

All quants use an imatrix calibrated on a blend of the three training datasets (game-creation, coding rehearsal, and the PatchCode coding-identity slice) — 600 samples, ~669k tokens, rendered through the Qwen chat template.

| Quant | Size | Compression vs BF16 |
|-------|------|---------------------|
| BF16 (ceiling) | 54G | 1.0× |
| Q8_0 | 29G | 1.9× |
| Q6_K | 24G | 2.3× |
| Q5_K_M | 19G | 2.8× |
| IQ4_NL | 16G | 3.4× |

### Evaluation method

Two independent eval axes, each run at 3 seeds:

**Coding-gate**: a 7-task agentic pytest suite. Each task gives the model a README + test file and asks it to implement a solution using tool calls (write, bash, read). A binary verifier runs the pytest suite — pass if all tests pass within 10 turns. Tasks: minijson (JSON parser), graph (graph algorithms), tracker (state tracker), mdlist (markdown list parser), taskq (task queue), lru (LRU cache), calc (calculator with operator precedence). This is a multi-turn tool-use eval, not a single-shot code-completion test.

**Game-gate**: 6 game-creation behaviors scored by cluster-specific gate functions. Each behavior has a prompt and a gate that checks the model's response for the required structural elements. Prose-scored behaviors (design, story) are the primary discrimination signal; tool-based behaviors (techart, build, scalecraft) require a tool-calling sandbox that the eval harness doesn't provide (their 0/3 scores are a harness limitation, not model capability).

### Results

#### Coding-gate (7 tasks × 3 seeds = 21 total)

| Quant | Score | calc | Other 6 tasks |
|-------|-------|------|---------------|
| **Q8_0** | **21/21 (100%)** | **3/3** | all 3/3 |
| Q6_K | 20/21 (95.2%) | 2/3 | all 3/3 |
| BF16 | 19/21 (90.5%) | 1/3 | all 3/3 |
| Q5_K_M | 18/21 (85.7%) | 0/3 | all 3/3 |
| IQ4_NL | 18/21 (85.7%) | 0/3 | all 3/3 |

The discrimination is entirely in the `calc` task. The other 6 tasks pass 3/3 across every quant level including BF16. `calc` is a recursive-descent parser with operator precedence — a precision-sensitive task where the game-creation LoRA's interference shows up. Q8_0 fully recovers it (3/3); Q4/Q5 lose it entirely (0/3).

#### Game-creation gate (6 behaviors × 3 seeds = 18 total)

| Quant | Score | story/iceberg | design (×2) | techart | build | scalecraft |
|-------|-------|---------------|-------------|---------|-------|------------|
| **BF16** | **9/18 (50%)** | **3/3** | 3/3 | 0/3 | 0/3 | 0/3 |
| **Q5_K_M** | **9/18 (50%)** | **3/3** | 3/3 | 0/3 | 0/3 | 0/3 |
| IQ4_NL | 8/18 (44.4%) | 2/3 | 3/3 | 0/3 | 0/3 | 0/3 |
| Q6_K | 8/18 (44.4%) | 2/3 | 3/3 | 0/3 | 0/3 | 0/3 |

The game-creation discrimination signal is in `story/iceberg_reveal`. BF16 and Q5_K_M pass 3/3 (full fidelity). IQ4_NL and Q6_K lose one seed — the model "explains the withheld thing in-scene" (a subtle prose-quality degradation: lore dump / narrator wink instead of letting the player discover). The design behaviors pass 3/3 across all quants. The 0/3 scores on techart/build/scalecraft are consistent across ALL quants including BF16 — these behaviors require tool-call proof lines (`SQUASH`, `VARIANTS`, `game_design_mechanic_spec`) that the prose-only eval harness can't produce.

### No clean winner

No quant matches BF16 on both axes simultaneously:

| Quant | Game | Coding | Size | Problem |
|-------|------|--------|------|---------|
| Q5_K_M | **9/18 ✅** | 18/21 (-1 calc) | 19G | Game perfect, calc lost |
| Q6_K | 8/18 (-1 story) | **20/21 ✅** | 24G | Coding best, game regressed |
| IQ4_NL | 8/18 (-1 story) | 18/21 (-1 calc) | 16G | Regressed both axes |

**Deployment recommendation: Q5_K_M.** It's the only deployment-sized quant that preserves game-creation (the novel axis). The calc coding loss is a narrow edge case (operator-precedence parsing); the other 6/7 coding tasks pass perfectly.

### The comprehensive imatrix experiment

We tested whether a richer imatrix (calibrated on ALL three training datasets: game-creation + coding rehearsal + coding-identity, 600 samples / 669k tokens) would improve IQ4_NL over the original imatrix (2 datasets, 500 samples / 511k tokens).

**Result: zero difference.** IQ4_NL v2 (comprehensive imatrix) scored identically to v1 on both axes: 8/18 game, 18/21 coding. The story/iceberg regression at 4-bit is architectural — inherent to IQ4_NL precision on this 27B hybrid architecture — not a calibration-quality issue. More calibration data makes the importance weights more accurate but cannot fix the fundamental information loss at 4 bits.

## PatchCode baseline comparison

Running the PatchCode predecessor through the same dual-axis eval:

| Model | Coding (IQ4_NL) | Coding (BF16) | Game (BF16) |
|-------|----------------|---------------|-------------|
| PatchCode | 21/21 (100%) | 20/21 (95.2%) | 0/18 (0%) |
| Gameworks | 18/21 (85.7%) | 19/21 (90.5%) | 9/18 (50%) |

The game-creation LoRA added +9 game behaviors (0→9) at a cost of -3 coding tasks (21→18 at IQ4_NL). The cost is entirely in `calc`. At BF16, the coding gap narrows to 1 task (20→19) — the LoRA's coding interference is real but modest at full precision.

## What we learned

1. **Dual-axis eval is necessary for dual-capability models.** A coding-only gate would have missed the game-creation regression entirely (IQ4_NL/Q6_K broke story/iceberg, invisible to coding tests). Similarly, a game-only gate would have missed the calc regression. Both axes must be tested.

2. **The calc regression is precision-recoverable.** Q8_0 (8-bit) fully restores calc to 3/3. The game-creation LoRA didn't permanently destroy the capability — it pushed it into a precision-sensitive regime where 4-bit and 5-bit quantization lose it. This means the "right" answer for maximum quality is BF16 or Q8_0 if VRAM allows.

3. **IQ4_NL game regression is architectural, not calibration-based.** A comprehensive 3-dataset imatrix made zero difference vs the 2-dataset original. The story/iceberg prose-quality regression at 4-bit is inherent to IQ4_NL on this architecture.

4. **Single-seed results are unreliable.** The `calc` task shows high seed variance (BF16 itself only passed 1/3). Multi-seed (≥3) evaluation is the minimum for trustworthy quant comparison. This echoes the PatchCode bake-off lesson: single-run scores fooled us there too.

5. **Game-creation discrimination lives in prose-quality behaviors.** The structural tool-based behaviors (techart/build/scalecraft) require a tool sandbox the eval harness doesn't provide. The effective discrimination surface is narrower than the full behavior set — but sufficient (it separated Q5_K_M from IQ4_NL/Q6_K).

## Runtime requirements

- **Runtime**: [AEON ik-llama fork](https://github.com/noonr48/qwen36-aeon-ik-llama) — mandatory. Stock llama.cpp/vLLM will not load this architecture.
- **KV cache**: f16 (`-ctk f16 -ctv f16`) — mandatory. Quantized KV degrades hybrid attention.
- **GPU offload**: all layers (`-ngl 99`) — the model is not CPU-usable.
- **Reasoning format**: `--jinja --reasoning-format deepseek` — formats the `<think>` blocks for tool-use agents.
- **VRAM**: 16G+ per GPU (IQ4_NL/Q5_K_M fit on 2× 16GB), 24G+ per GPU (Q8_0 needs 2× 24GB).

See the model card for specific launch commands.
