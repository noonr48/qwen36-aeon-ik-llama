#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'USAGE'
usage: scripts/qwen36-rys-rtr-suite.sh <models.tsv> [out-dir]

Runs qwen36-rys-rtr-bench.sh for each model listed in a tab-separated file:
  label<TAB>/absolute/path/to/model.gguf

Blank lines and lines beginning with # are ignored. Environment overrides are
passed through to qwen36-rys-rtr-bench.sh.
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

models_tsv="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bench_script="${QWEN36_RYS_BENCH_SCRIPT:-${repo_root}/scripts/qwen36-rys-rtr-bench.sh}"
out_dir="${2:-${repo_root}/tmp/qwen36-rys-rtr/suite-$(date -u +%Y%m%dT%H%M%SZ)}"

if [[ ! -f "$models_tsv" ]]; then
    echo "error: model list not found: $models_tsv" >&2
    exit 1
fi

if [[ ! -x "$bench_script" ]]; then
    echo "error: benchmark script is not executable: $bench_script" >&2
    exit 1
fi

mkdir -p "$out_dir"
cp "$models_tsv" "${out_dir}/models.tsv"

summary="${out_dir}/suite-summary.tsv"
printf 'label\tstatus\trepack\tsplit_mode\ttest\tn_batch\tn_ubatch\tavg_ts\tstddev_ts\n' > "$summary"

while IFS=$'\t' read -r label model_path extra || [[ -n "${label:-}" ]]; do
    [[ -z "${label// }" ]] && continue
    [[ "$label" == \#* ]] && continue

    if [[ -n "${extra:-}" ]]; then
        echo "warning: ignoring extra fields for label: $label" >&2
    fi

    safe_label="$(printf '%s' "$label" | tr -cs 'A-Za-z0-9_.-' '_')"
    model_out="${out_dir}/${safe_label}"
    mkdir -p "$model_out"

    echo "running: $label"
    if "$bench_script" "$model_path" "$model_out" > "${model_out}/bench-run.log" 2>&1; then
        status="ok"
    else
        status="failed"
        echo "failed: $label; see ${model_out}/bench-run.log" >&2
    fi

    if [[ -f "${model_out}/summary.tsv" ]]; then
        awk -v label="$label" -v status="$status" 'BEGIN { OFS="\t" } { print label, status, $0 }' \
            "${model_out}/summary.tsv" >> "$summary"
    else
        printf '%s\t%s\t\t\t\t\t\t\t\n' "$label" "$status" >> "$summary"
    fi
done < "$models_tsv"

cat "$summary"
