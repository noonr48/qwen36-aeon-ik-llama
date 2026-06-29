#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'USAGE'
usage: scripts/qwen36-rys-rtr-bench.sh <model.gguf> [out-dir]

Runs the Qwen3.6 RYS runtime-repack A/B speed probe with llama-bench.

Environment overrides:
  BENCH_BIN                      benchmark binary (default: build/bin/llama-bench)
  QWEN36_RYS_BENCH_SPLIT_MODE    split mode (default: layer)
  QWEN36_RYS_BENCH_PROMPT        prompt tokens (default: 512)
  QWEN36_RYS_BENCH_GEN           generated tokens (default: 128)
  QWEN36_RYS_BENCH_BATCH         batch size (default: 256)
  QWEN36_RYS_BENCH_UBATCH        ubatch size (default: 64)
  QWEN36_RYS_BENCH_REPS          repetitions (default: 5)

Set CUDA_VISIBLE_DEVICES outside this script when pinning GPUs.
Prefer GPU UUIDs, or set CUDA_DEVICE_ORDER=PCI_BUS_ID when using numeric IDs.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

if [[ $# -lt 1 ]]; then
    usage >&2
    exit 1
fi

model="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bench_bin="${BENCH_BIN:-${repo_root}/build/bin/llama-bench}"
out_dir="${2:-${repo_root}/tmp/qwen36-rys-rtr/$(date -u +%Y%m%dT%H%M%SZ)}"

split_mode="${QWEN36_RYS_BENCH_SPLIT_MODE:-layer}"
n_prompt="${QWEN36_RYS_BENCH_PROMPT:-512}"
n_gen="${QWEN36_RYS_BENCH_GEN:-128}"
n_batch="${QWEN36_RYS_BENCH_BATCH:-256}"
n_ubatch="${QWEN36_RYS_BENCH_UBATCH:-64}"
reps="${QWEN36_RYS_BENCH_REPS:-5}"

if [[ ! -x "$bench_bin" ]]; then
    echo "error: benchmark binary is not executable: $bench_bin" >&2
    echo "build it with: cmake --build build --config Release --target llama-bench" >&2
    exit 1
fi

if [[ ! -f "$model" ]]; then
    echo "error: model file not found: $model" >&2
    exit 1
fi

mkdir -p "$out_dir"

{
    printf 'utc_start=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'model=%s\n' "$model"
    printf 'bench_bin=%s\n' "$bench_bin"
    printf 'cuda_visible_devices=%s\n' "${CUDA_VISIBLE_DEVICES:-}"
    printf 'cuda_device_order=%s\n' "${CUDA_DEVICE_ORDER:-}"
    printf 'split_mode=%s\n' "$split_mode"
    printf 'prompt_tokens=%s\n' "$n_prompt"
    printf 'generated_tokens=%s\n' "$n_gen"
    printf 'batch=%s\n' "$n_batch"
    printf 'ubatch=%s\n' "$n_ubatch"
    printf 'repetitions=%s\n' "$reps"
    if command -v nvidia-smi >/dev/null 2>&1; then
        nvidia-smi --query-gpu=index,uuid,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits || true
    fi
} > "${out_dir}/run-env.txt"

common=(
    -m "$model"
    -ngl 999
    -sm "$split_mode"
    -b "$n_batch"
    -ub "$n_ubatch"
    -ctk f16
    -ctv f16
    -fa 1
    -gr 1
    -p "$n_prompt"
    -n "$n_gen"
    -r "$reps"
    -o json
)

clean_json_stdout() {
    local raw="$1"
    local json="$2"

    sed -n '/^[[:space:]]*\[/,$p' "$raw" > "$json"
    if [[ ! -s "$json" ]]; then
        echo "error: could not find JSON array in benchmark output: $raw" >&2
        return 1
    fi
}

echo "writing results to: $out_dir"
echo "baseline: -rtr 0"
"$bench_bin" "${common[@]}" -rtr 0 \
    > "${out_dir}/baseline-rtr0.raw" \
    2> "${out_dir}/baseline-rtr0.log"
clean_json_stdout "${out_dir}/baseline-rtr0.raw" "${out_dir}/baseline-rtr0.json"

echo "runtime repack: -rtr 1"
"$bench_bin" "${common[@]}" -rtr 1 \
    > "${out_dir}/runtime-repack-rtr1.raw" \
    2> "${out_dir}/runtime-repack-rtr1.log"
clean_json_stdout "${out_dir}/runtime-repack-rtr1.raw" "${out_dir}/runtime-repack-rtr1.json"

if command -v jq >/dev/null 2>&1; then
    jq -r '.[] | [.repack, .split_mode, .test, .n_batch, .n_ubatch, .avg_ts, .stddev_ts] | @tsv' \
        "${out_dir}/baseline-rtr0.json" \
        "${out_dir}/runtime-repack-rtr1.json" \
        > "${out_dir}/summary.tsv"
    cat "${out_dir}/summary.tsv"
else
    echo "jq not found; raw JSON results were written."
fi

{
    printf 'baseline log repack lines:\n'
    grep -Eai 'repack|repacked' "${out_dir}/baseline-rtr0.log" || true
    printf '\nruntime-repack log repack lines:\n'
    grep -Eai 'repack|repacked' "${out_dir}/runtime-repack-rtr1.log" || true
} > "${out_dir}/repack-audit.txt"
