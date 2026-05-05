# Qwen3.6 AEON RYS ckpt386 Q4NL Deploy Sweep Notes

Date: 2026-05-05

Scope:
- Model target: `Qwen3.6-27B-AEON-RYS-15-20`
- Adapter: checkpoint 386 LoRA merged into the base model at multiple strengths
- Deploy format: `IQ4_NL` GGUF with imatrix
- Server/runtime: custom `ik_llama.cpp`, temp `0.7`, graph split, flash attention, Jinja chat template, DeepSeek reasoning format, context `65536`
- Eval GPUs: non-5060 pairs only

Completed deploy-format Q4NL results:
- Base AEON Q4NL: 1/5 pass, mean 0.55
- s0.075: 3/5 pass, mean 0.90; missed web-race first-success and kill-excess targeted-kill logic
- s0.10: 4/5 pass, mean 0.95; missed search-timeout handler passthrough
- s0.125: 2/5 pass, mean 0.775; missed PR detail field usage, timeout passthrough, and web-race
- s0.15: 3/5 pass, mean 0.875
- s0.20: 5/5 pass, mean 1.0; PR-details hit the full 600s timeout
- s0.25 first run: 5/5 pass, mean 1.0; faster overall than s0.20

Final Q4NL score table:
- base: 1/5 pass, mean 0.550, elapsed 2660s, timeoutish 4
- s0.05: 2/5 pass, mean 0.600, elapsed 2418s, timeoutish 3
- s0.075: 3/5 pass, mean 0.900, elapsed 1638s, timeoutish 0
- s0.10: 4/5 pass, mean 0.950, elapsed 1106s, timeoutish 0
- s0.125: 2/5 pass, mean 0.775, elapsed 1190s, timeoutish 0
- s0.15: 3/5 pass, mean 0.875, elapsed 1186s, timeoutish 0
- s0.20: 5/5 pass, mean 1.000, elapsed 1568s, timeoutish 1
- s0.25 first run: 5/5 pass, mean 1.000, elapsed 1328s, timeoutish 0
- s0.25 repeat: 1/5 pass, mean 0.750, elapsed 1343s, timeoutish 0

Interpretation so far:
- Q4NL is the deployment target; BF16 results are scouting context only.
- LoRA clearly improves over base Q4NL.
- s0.25 and s0.20 are the only single-run 5/5 points.
- s0.25 looked like the leading candidate after the first run, but the repeat immediately exposed instability on the commits schema check.
- The s0.25 repeat also missed PR-detail stat usage, so the first s0.25 5/5 result is not stable enough by itself.
- s0.20 has perfect verifier quality in one run but had a full timeout on PR-details, so its control/latency is weaker than the first s0.25 run.
- s0.10 is the strongest stable-looking single run without any full timeouts: 4/5, mean 0.95, elapsed 1106s.
- s0.20 is the best verifier-quality single run but needs a repeat because of the 600s PR-details timeout.
- s0.25 needs caution: first run was perfect, repeat was only 1/5, mean 0.75.
- No Q4NL eval servers or Claw runners remained after the final s0.05 summary; only the pre-existing ComfyUI process was still visible in `nvidia-smi`.

Key artifact paths:
- Q4NL artifacts: `server:/home/benbi/qwen36_ms_swift_lora/evals/q4nl_strength_sweep_20260505/gguf_iq4nl`
- s0.25 first run summary: `server:/home/benbi/qwen36_ms_swift_lora/evals/q4nl_s025_followup_prod_20260505_t07_graph_fa_c65536_pair03/summary.md`
- s0.20 summary: `server:/home/benbi/qwen36_ms_swift_lora/evals/q4nl_s020_followup_prod_20260505_t07_graph_fa_c65536_pair49/summary.md`
- s0.05 summary: `server:/home/benbi/qwen36_ms_swift_lora/evals/q4nl_s005_followup_prod_20260505_t07_graph_fa_c65536_pair03/summary.md`
- s0.25 repeat summary: `server:/home/benbi/qwen36_ms_swift_lora/evals/q4nl_s025_repeat2_prod_20260505_t07_graph_fa_c65536_pair49/summary.md`

Stability phase:
- Started after the first deploy sweep to decide the long-term deployment candidate.
- `s0.10-repeat2` launched on GPU pair 0/3, port 8120:
  `server:/home/benbi/qwen36_ms_swift_lora/evals/q4nl_s010_repeat2_prod_20260505_t07_graph_fa_c65536_pair03`
- `s0.20-repeat2` launched on GPU pair 4/9, port 8121:
  `server:/home/benbi/qwen36_ms_swift_lora/evals/q4nl_s020_repeat2_prod_20260505_t07_graph_fa_c65536_pair49`
- Both use IQ4_NL GGUF, temp 0.7, graph split, flash attention, Jinja, DeepSeek reasoning format, c65536, and non-5060 bwrap GPU binding.
- First repeat task results:
  - `s0.10-repeat2` commits scored 0.875; it had the branch schema/docs but missed sending branch through the GitHub `sha` request parameter.
  - `s0.20-repeat2` commits scored 0.875; request/schema checks were right but `npm run build` failed.
- PR-details repeat results:
  - `s0.10-repeat2` PR-details passed 1.0 in 320s.
  - `s0.20-repeat2` PR-details scored 0.5; it did not fetch/use the PR detail endpoint fields in this repeat.
- Completed repeat2 stability results:
  - `s0.10-repeat2`: 2/5 pass, mean 0.825, elapsed 1217s. Misses: commits branch-through-sha, search-timeout handler passthrough, web-race first-success.
  - `s0.20-repeat2`: 2/5 pass, mean 0.825, elapsed 1089s. Misses: commits build, PR-detail endpoint/fields, search-timeout handler passthrough.
  - Two-run combined: `s0.10` = 6/10 pass, mean 0.887; `s0.20` = 7/10 pass, mean 0.912.
  - Next action: run repeat3 for both s0.10 and s0.20 before choosing the long-term deploy strength.
- Repeat3 launched:
  - `s0.10-repeat3` on pair 0/3, port 8120:
    `server:/home/benbi/qwen36_ms_swift_lora/evals/q4nl_s010_repeat3_prod_20260505_t07_graph_fa_c65536_pair03`
  - `s0.20-repeat3` on pair 4/9, port 8121:
    `server:/home/benbi/qwen36_ms_swift_lora/evals/q4nl_s020_repeat3_prod_20260505_t07_graph_fa_c65536_pair49`
- Repeat3 early results:
  - `s0.10-repeat3` commits passed 1.0, but PR-details scored 0.5 because it did not fetch/use PR detail endpoint fields.
  - `s0.20-repeat3` commits scored 0.75; it missed branch output metadata and branch-through-sha.
  - `s0.10-repeat3` search-timeout passed 1.0.
  - `s0.20-repeat3` PR-details scored 0.625; it fetched the detail endpoint but did not use detail additions/deletions/changed_files.

Completed repeat3 stability results:
- `s0.10-repeat3`: strict score 3/5 pass, mean 0.750, elapsed 1195s.
  - Passed commits, search-timeout, and web-race.
  - PR-details scored 0.5 because it did not fetch/use PR detail endpoint fields.
  - Kill-excess scored 0.25, but the Claw log shows the API request failed immediately after 3 attempts. Server log shows `terminate called after throwing an instance of 'std::runtime_error'` with `Invalid diff` during/after the prior web-race task. Treat this row as a runtime/server stability incident, not a normal model-output miss.
- `s0.20-repeat3`: 1/5 pass, mean 0.725, elapsed 1300s.
  - Passed kill-excess only.
  - Missed commits branch output/branch-through-sha, PR-detail field usage, timeout passthrough, and web-race first-success.

Final stability comparison:
- `s0.10`: 3 runs, strict 9/15 pass, mean 0.842.
- `s0.10` crash-adjusted: 9/14 pass, mean 0.884 if the invalid kill-excess task is excluded because the server crashed before the model could attempt it.
- `s0.20`: 3 runs, 8/15 pass, mean 0.850.
- `s0.25`: 2 runs, 6/10 pass, mean 0.875, but the second run collapsed to 1/5 after a perfect first run.

Long-term deployment recommendation:
- Pick `s0.10` IQ4_NL as the tentative long-term deployment strength if we need to deploy now.
- Reject `s0.20` as the default despite its first 5/5 run. It degraded across repeats and repeatedly missed PR-detail/timeout behavior.
- Reject `s0.25` as the default. Its first 5/5 did not reproduce; repeat2 fell to 1/5.
- Keep the label tentative. The LoRA improves substantially over base Q4NL, but temp 0.7 remains high-variance, and the `ik_llama.cpp` invalid-diff crash should be treated as a deployment runtime issue to fix or guard before sustained production use.
- After repeat3, no Q4NL eval servers or Claw runners remained. `nvidia-smi` only showed the pre-existing ComfyUI process on the 5090.

Final artifact paths:
- `s0.10-repeat3`: `server:/home/benbi/qwen36_ms_swift_lora/evals/q4nl_s010_repeat3_prod_20260505_t07_graph_fa_c65536_pair03/summary.md`
- `s0.20-repeat3`: `server:/home/benbi/qwen36_ms_swift_lora/evals/q4nl_s020_repeat3_prod_20260505_t07_graph_fa_c65536_pair49/summary.md`

ik_llama fork status:
- The server fork at `server:/home/benbi/ik_llama.cpp` is on upstream `main` version `61 (0147cf48)` plus a dirty local patch stack.
- Relevant local changes include Qwen3.6/Qwen3Next GGUF conversion/model metadata support, linear-attention LoRA conversion handling, graph-split recurrent prompt/checkpoint stabilization, Jinja/DeepSeek reasoning serving flags, slot-pinned model aliases, tool-call dedupe, and the chat diff crash fix for non-monotonic partial tool-call parsing.
- The built `llama-server` used for the Q4NL deploy sweep is `server:/home/benbi/ik_llama.cpp/build/bin/llama-server`, built 2026-05-03 15:24 local server time. It exposes the required flags: `--jinja`, `--reasoning-format`, `--reasoning-budget`, `-fa`, `-sm graph`, `--ctx-checkpoints`, `-cram`, `--lora`, and `--lora-scaled`.
- The chosen deployment path is not a live runtime LoRA adapter. It is a strength-merged IQ4_NL GGUF: `Qwen3.6-27B-AEON-RYS-15-20-ckpt386-s010-IQ4_NL-imatrix.gguf`.
- Live/native LoRA adapter support exists and was tested separately, but the deploy configuration uses flash attention and graph split. Current `llama_lora_adapter_set` still rejects LoRA with flash attention, so merged GGUF is the correct long-term serving path for this setup.
- Before treating this as reproducible production infrastructure, commit or archive the dirty `ik_llama.cpp` patch stack. The source currently shows many uncommitted changes in `common/chat*.cpp`, `examples/server/*`, conversion scripts, GGUF Python metadata/mapping files, `include/llama.h`, and `src/llama-*`.
