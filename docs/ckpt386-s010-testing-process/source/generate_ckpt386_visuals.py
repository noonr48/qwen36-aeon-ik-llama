#!/usr/bin/env python3
from __future__ import annotations

import html
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


COLORS = {
    "ink": "#1f2933",
    "muted": "#5f6f7a",
    "line": "#c9d2d9",
    "paper": "#f7f9fb",
    "white": "#ffffff",
    "blue": "#2f6f9f",
    "teal": "#248f7b",
    "green": "#2f8f57",
    "gold": "#b98020",
    "red": "#b85042",
    "purple": "#6d5fa8",
    "gray": "#dde5ea",
    "soft_blue": "#e8f2f7",
    "soft_teal": "#e7f5f1",
    "soft_green": "#eaf6ee",
    "soft_gold": "#fbf1df",
    "soft_red": "#f8e9e6",
    "soft_purple": "#efedf8",
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def wrap(text: str, width: int = 28) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if current and len(candidate) > width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def text_block(
    x: int,
    y: int,
    text: str,
    *,
    size: int = 28,
    weight: int = 500,
    color: str = COLORS["ink"],
    width: int = 32,
    line_h: int | None = None,
    anchor: str = "start",
) -> str:
    line_h = line_h or int(size * 1.28)
    lines = wrap(text, width)
    out = [
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
        f'font-family="Inter, Arial, sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="{color}">'
    ]
    for idx, line in enumerate(lines):
        dy = 0 if idx == 0 else line_h
        out.append(f'<tspan x="{x}" dy="{dy}">{esc(line)}</tspan>')
    out.append("</text>")
    return "\n".join(out)


def card(
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    body: str,
    *,
    fill: str = COLORS["white"],
    stroke: str = COLORS["line"],
    accent: str = COLORS["blue"],
    title_size: int = 28,
    body_size: int = 21,
    body_width: int = 34,
) -> str:
    return "\n".join(
        [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2"/>',
            f'<rect x="{x}" y="{y}" width="10" height="{h}" rx="5" fill="{accent}"/>',
            text_block(x + 30, y + 48, title, size=title_size, weight=800, color=COLORS["ink"], width=body_width),
            text_block(x + 30, y + 90, body, size=body_size, weight=450, color=COLORS["muted"], width=body_width),
        ]
    )


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = COLORS["muted"], width: int = 4) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="{width}" stroke-linecap="round" marker-end="url(#arrow)"/>'
    )


def svg_shell(width: int, height: int, title: str, subtitle: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth">
      <path d="M2,2 L10,6 L2,10 Z" fill="{COLORS["muted"]}"/>
    </marker>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#17212b" flood-opacity="0.12"/>
    </filter>
  </defs>
  <rect width="{width}" height="{height}" fill="{COLORS["paper"]}"/>
  {text_block(56, 68, title, size=34, weight=850, color=COLORS["ink"], width=62)}
  {text_block(56, 112, subtitle, size=21, weight=450, color=COLORS["muted"], width=92)}
  {body}
</svg>
'''


def write_asset(name: str, width: int, height: int, title: str, subtitle: str, body: str) -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    svg_path = ASSETS / f"{name}.svg"
    png_path = ASSETS / f"{name}.png"
    svg_path.write_text(svg_shell(width, height, title, subtitle, body), encoding="utf-8")
    converter = shutil.which("rsvg-convert")
    if converter:
        subprocess.run([converter, "-w", str(width), "-h", str(height), str(svg_path), "-o", str(png_path)], check=True)


def story_arc() -> None:
    boxes = [
        (70, 170, 250, 180, "Start", "AEON RYS 15/20 already existed as the Q4NL deployment target.", COLORS["soft_blue"], COLORS["blue"]),
        (365, 170, 250, 180, "Tune", "A small ckpt386 behavioral LoRA nudged agent behavior.", COLORS["soft_teal"], COLORS["teal"]),
        (660, 170, 250, 180, "Messy tests", "Direct adapter and early probes were useful, but not the deploy path.", COLORS["soft_gold"], COLORS["gold"]),
        (955, 170, 250, 180, "Deploy test", "Merged IQ4_NL GGUF showed the real production shape.", COLORS["soft_green"], COLORS["green"]),
        (1250, 170, 250, 180, "Pick", "s0.10 was less flashy than s0.20/s0.25, but held up better.", COLORS["soft_purple"], COLORS["purple"]),
    ]
    pieces = []
    for x, y, w, h, title, body, fill, accent in boxes:
        pieces.append(f'<g filter="url(#shadow)">{card(x, y, w, h, title, body, fill=fill, accent=accent, body_width=22)}</g>')
    for x in [320, 615, 910, 1205]:
        pieces.append(arrow(x + 12, 260, x + 38, 260))
    pieces.append(text_block(72, 425, "The headline lesson", size=28, weight=800, color=COLORS["ink"], width=28))
    pieces.append(text_block(72, 465, "The best-looking first run was not automatically the release. Repeats mattered more than the exciting row.", size=24, weight=500, color=COLORS["muted"], width=95))
    write_asset(
        "story_arc_casual",
        1570,
        560,
        "The story was not a straight line",
        "We had to separate useful scouting results from the exact thing we planned to upload.",
        "\n".join(pieces),
    )


def runtime_path() -> None:
    y = 185
    boxes = [
        (80, y, 245, 190, "AEON RYS 15/20", "Existing Q4NL model line and HF-format base.", COLORS["soft_blue"], COLORS["blue"]),
        (380, y, 245, 190, "ckpt386 LoRA", "10,800 examples, r=8, alpha=32, behavior-focused.", COLORS["soft_teal"], COLORS["teal"]),
        (680, y, 245, 190, "Merge at s0.10", "Low-strength merge kept the nudge without overpowering the base.", COLORS["soft_gold"], COLORS["gold"]),
        (980, y, 245, 190, "IQ4_NL + imatrix", "Quantized as the practical upload artifact.", COLORS["soft_green"], COLORS["green"]),
        (1280, y, 245, 190, "ik-llama runtime", "Jinja template, DeepSeek format, graph split, flash attention.", COLORS["soft_purple"], COLORS["purple"]),
    ]
    pieces = []
    for x, yy, w, h, title, body, fill, accent in boxes:
        pieces.append(f'<g filter="url(#shadow)">{card(x, yy, w, h, title, body, fill=fill, accent=accent, body_width=22)}</g>')
    for x in [325, 625, 925, 1225]:
        pieces.append(arrow(x + 15, 267, x + 40, 267))
    pieces.append(card(205, 455, 520, 150, "Why not live LoRA?", "The tested production profile uses flash attention. Live LoRA is not the supported serving path here.", fill=COLORS["white"], accent=COLORS["red"], body_width=54))
    pieces.append(card(850, 455, 520, 150, "What gets uploaded?", "A full merged GGUF at s0.10. The file is the upload artifact, not a separate adapter.", fill=COLORS["white"], accent=COLORS["green"], body_width=54))
    write_asset(
        "technical_deploy_path",
        1600,
        690,
        "The actual deploy route",
        "The release candidate is a merged GGUF, not a runtime adapter recipe.",
        "\n".join(pieces),
    )


def testing_ladder() -> None:
    rows = [
        ("1", "Behavior probes", "Small response tests showed full-strength LoRA was too aggressive.", COLORS["blue"], "scouting"),
        ("2", "Canvas demo", "Krita-like app task tested whether the model could build a coherent demo.", COLORS["teal"], "practical"),
        ("3", "Merged GGUF check", "BF16 merged GGUF showed the adapter could work in the ik-llama lane.", COLORS["gold"], "format"),
        ("4", "Q4NL sweep", "s0.05 through s0.25 were tested in the deploy quantization.", COLORS["green"], "deployment"),
        ("5", "Repeats", "s0.20/s0.25 looked great once; s0.10 was the better default.", COLORS["purple"], "selection"),
    ]
    pieces = []
    start_y = 165
    for idx, (num, title, body, color, label) in enumerate(rows):
        y = start_y + idx * 105
        pieces.append(f'<circle cx="115" cy="{y+38}" r="34" fill="{color}"/>')
        pieces.append(text_block(115, y + 49, num, size=28, weight=850, color=COLORS["white"], width=3, anchor="middle"))
        pieces.append(f'<rect x="175" y="{y}" width="1130" height="78" rx="12" fill="{COLORS["white"]}" stroke="{COLORS["line"]}" stroke-width="2"/>')
        pieces.append(text_block(205, y + 34, title, size=26, weight=850, color=COLORS["ink"], width=24))
        pieces.append(text_block(520, y + 33, body, size=21, weight=450, color=COLORS["muted"], width=68))
        pieces.append(f'<rect x="1340" y="{y+17}" width="145" height="42" rx="21" fill="{color}"/>')
        pieces.append(text_block(1412, y + 45, label, size=18, weight=800, color=COLORS["white"], width=14, anchor="middle"))
        if idx < len(rows) - 1:
            pieces.append(f'<line x1="115" y1="{y+72}" x2="115" y2="{y+102}" stroke="{COLORS["line"]}" stroke-width="5" stroke-linecap="round"/>')
    write_asset(
        "testing_ladder_full_process",
        1600,
        760,
        "The testing ladder",
        "Each stage answered a different question. Only the last stages answered the upload question.",
        "\n".join(pieces),
    )


def strength_selection() -> None:
    rows = [
        ("base", 0.550, "1/5", "4 timeouts", COLORS["red"]),
        ("s0.10", 0.950, "4/5 first, 9/15 repeats", "selected", COLORS["green"]),
        ("s0.20", 1.000, "5/5 first, 8/15 repeats", "degraded", COLORS["gold"]),
        ("s0.25", 1.000, "5/5 first, 6/10 repeats", "collapsed", COLORS["purple"]),
    ]
    pieces = []
    pieces.append(text_block(80, 170, "First-run mean score", size=24, weight=800, color=COLORS["ink"], width=28))
    x0 = 360
    for idx, (label, mean, passes, note, color) in enumerate(rows):
        y = 205 + idx * 105
        bar_w = int(mean * 650)
        pieces.append(text_block(90, y + 35, label, size=28, weight=850, color=COLORS["ink"], width=10))
        pieces.append(f'<rect x="{x0}" y="{y}" width="650" height="42" rx="21" fill="{COLORS["gray"]}"/>')
        pieces.append(f'<rect x="{x0}" y="{y}" width="{bar_w}" height="42" rx="21" fill="{color}"/>')
        pieces.append(text_block(x0 + 685, y + 32, f"{mean:.3f}", size=24, weight=850, color=COLORS["ink"], width=8))
        pieces.append(text_block(x0 + 805, y + 31, passes, size=21, weight=700, color=COLORS["ink"], width=26))
        pieces.append(text_block(x0 + 1075, y + 31, note, size=21, weight=650, color=COLORS["muted"], width=16))
    pieces.append(card(85, 650, 1350, 130, "Selection rule", "Do not pick the loudest single row. Pick the strength that improves base and survives repeats well enough to deploy.", fill=COLORS["white"], accent=COLORS["green"], body_width=96))
    write_asset(
        "strength_selection_scoreboard",
        1600,
        860,
        "Why s0.10 won the release slot",
        "s0.20 and s0.25 had perfect first runs; repeat stability changed the decision.",
        "\n".join(pieces),
    )


def base_vs_s010() -> None:
    tasks = [
        ("commits branch", 0.75, 1.00),
        ("PR details", 1.00, 1.00),
        ("kill excess", 0.25, 1.00),
        ("search timeout", 0.25, 0.75),
        ("web race", 0.50, 1.00),
    ]
    pieces = []
    x0 = 360
    pieces.append(text_block(x0, 168, "previous Q4NL", size=20, weight=800, color=COLORS["red"], width=16))
    pieces.append(text_block(x0 + 335, 168, "ckpt386 s0.10", size=20, weight=800, color=COLORS["green"], width=16))
    for idx, (task, base, tuned) in enumerate(tasks):
        y = 210 + idx * 95
        pieces.append(text_block(85, y + 30, task, size=24, weight=800, color=COLORS["ink"], width=18))
        pieces.append(f'<rect x="{x0}" y="{y}" width="280" height="34" rx="17" fill="{COLORS["gray"]}"/>')
        pieces.append(f'<rect x="{x0}" y="{y}" width="{int(base * 280)}" height="34" rx="17" fill="{COLORS["red"]}"/>')
        pieces.append(f'<rect x="{x0 + 335}" y="{y}" width="280" height="34" rx="17" fill="{COLORS["gray"]}"/>')
        pieces.append(f'<rect x="{x0 + 335}" y="{y}" width="{int(tuned * 280)}" height="34" rx="17" fill="{COLORS["green"]}"/>')
        pieces.append(text_block(x0 + 648, y + 28, f"{base:.2f} -> {tuned:.2f}", size=20, weight=800, color=COLORS["ink"], width=14))
    pieces.append(card(1180, 230, 370, 220, "Operational change", "The base model often ran into full-timeout behavior. s0.10 finished more patches cleanly in the deploy-format run.", fill=COLORS["soft_green"], accent=COLORS["green"], body_width=32))
    pieces.append(card(1180, 500, 370, 155, "Still not solved", "Search-timeout behavior improved but did not fully pass in the first s0.10 run.", fill=COLORS["soft_gold"], accent=COLORS["gold"], body_width=32))
    write_asset(
        "base_vs_s010_task_scores",
        1600,
        760,
        "Where the selected tune actually helped",
        "The useful gain was not just a mean score. It changed several concrete patch behaviors.",
        "\n".join(pieces),
    )


def technical_caveats() -> None:
    pieces = []
    pieces.append(card(90, 175, 410, 180, "Claim we can make", "On this Q4NL coding-agent matrix, s0.10 improved the previous AEON RYS Q4NL deployment.", fill=COLORS["soft_green"], accent=COLORS["green"], body_width=34))
    pieces.append(card(595, 175, 410, 180, "Claim we should avoid", "This is not proof of a universal chat or BF16 upgrade.", fill=COLORS["soft_red"], accent=COLORS["red"], body_width=34))
    pieces.append(card(1100, 175, 410, 180, "Runtime caveat", "One repeat row hit an invalid-diff server crash, so deployment should guard that path.", fill=COLORS["soft_gold"], accent=COLORS["gold"], body_width=34))
    pieces.append(card(230, 430, 500, 150, "Public wording", "Practical coding-agent fine-tuned Q4NL variant of AEON RYS 15/20.", fill=COLORS["white"], accent=COLORS["blue"], body_width=48))
    pieces.append(card(870, 430, 550, 155, "Deployment wording", "Use the merged GGUF with custom qwen36-aeon-ik-llama, Jinja, DeepSeek reasoning, graph split, and flash attention.", fill=COLORS["white"], accent=COLORS["purple"], body_width=54))
    write_asset(
        "claims_and_caveats",
        1600,
        670,
        "Keep the communication honest",
        "The writeup should explain the win clearly without making it bigger than the evidence.",
        "\n".join(pieces),
    )


def release_artifact_card() -> None:
    pieces = []
    pieces.append(card(80, 160, 650, 150, "Selected artifact", "Qwen3.6 27B AEON RYS 15/20, ckpt386 s0.10, IQ4_NL imatrix GGUF.", fill=COLORS["soft_green"], accent=COLORS["green"], body_width=58))
    pieces.append(card(870, 160, 610, 150, "What it is", "ckpt386 behavioral LoRA merged into AEON RYS 15/20 at strength 0.10, then quantized to IQ4_NL with imatrix.", fill=COLORS["soft_blue"], accent=COLORS["blue"], body_width=56))
    pieces.append(card(80, 365, 390, 145, "Runtime", "qwen36-aeon-ik-llama with Jinja and DeepSeek reasoning format.", fill=COLORS["white"], accent=COLORS["purple"], body_width=36))
    pieces.append(card(585, 365, 390, 145, "Test shape", "temp 0.7, graph split, flash attention, context 65536.", fill=COLORS["white"], accent=COLORS["gold"], body_width=36))
    pieces.append(card(1090, 365, 390, 145, "Main caveat", "Selected for this practical Q4NL matrix, not claimed as a universal model upgrade.", fill=COLORS["white"], accent=COLORS["red"], body_width=36))
    write_asset(
        "selected_artifact_card",
        1600,
        620,
        "The upload target",
        "One file, one deployment path, one narrow public claim.",
        "\n".join(pieces),
    )


def results_heatmap() -> None:
    cols = [
        ("base", ["fail", "timeout", "timeout", "timeout", "timeout"]),
        ("s0.10 r1", ["pass", "pass", "pass", "partial", "pass"]),
        ("s0.10 r2", ["partial", "pass", "pass", "partial", "fail"]),
        ("s0.10 r3", ["pass", "fail", "crash", "pass", "pass"]),
        ("s0.20 r1", ["pass", "timeout", "pass", "pass", "pass"]),
        ("s0.20 r2", ["partial", "fail", "pass", "partial", "pass"]),
        ("s0.20 r3", ["fail", "partial", "pass", "partial", "fail"]),
        ("s0.25 r1", ["pass", "pass", "pass", "pass", "pass"]),
        ("s0.25 r2", ["partial", "partial", "pass", "partial", "fail"]),
    ]
    rows = ["commits", "PR details", "kill excess", "timeout", "web race"]
    fill = {
        "pass": COLORS["green"],
        "partial": COLORS["gold"],
        "fail": COLORS["red"],
        "timeout": "#8d6e63",
        "crash": COLORS["purple"],
    }
    label = {
        "pass": "pass",
        "partial": "partial",
        "fail": "fail",
        "timeout": "timeout",
        "crash": "crash",
    }
    pieces = []
    x0, y0 = 270, 185
    cell_w, cell_h = 128, 70
    for ci, (col, _) in enumerate(cols):
        pieces.append(text_block(x0 + ci * cell_w + 58, 155, col, size=17, weight=800, color=COLORS["ink"], width=10, anchor="middle"))
    for ri, row in enumerate(rows):
        y = y0 + ri * cell_h
        pieces.append(text_block(80, y + 44, row, size=23, weight=850, color=COLORS["ink"], width=13))
        for ci, (_, values) in enumerate(cols):
            state = values[ri]
            x = x0 + ci * cell_w
            pieces.append(f'<rect x="{x}" y="{y}" width="110" height="50" rx="12" fill="{fill[state]}" opacity="0.92"/>')
            pieces.append(text_block(x + 55, y + 32, label[state], size=15, weight=850, color=COLORS["white"], width=9, anchor="middle"))
    legend_y = 585
    for i, state in enumerate(["pass", "partial", "fail", "timeout", "crash"]):
        x = 290 + i * 210
        pieces.append(f'<rect x="{x}" y="{legend_y}" width="32" height="24" rx="6" fill="{fill[state]}"/>')
        pieces.append(text_block(x + 45, legend_y + 20, label[state], size=18, weight=700, color=COLORS["muted"], width=12))
    pieces.append(card(80, 655, 1370, 130, "Read the heatmap row-wise", "The selection was not only about first-run score. It was about which strength avoided catastrophic repeats and kept useful behavior across the same five tasks.", fill=COLORS["white"], accent=COLORS["green"], body_width=100))
    write_asset(
        "q4nl_results_heatmap",
        1600,
        830,
        "The repeat matrix at a glance",
        "Green first runs are useful, but repeat behavior is what made the selection hard.",
        "\n".join(pieces),
    )


def main() -> None:
    story_arc()
    runtime_path()
    testing_ladder()
    strength_selection()
    base_vs_s010()
    technical_caveats()
    release_artifact_card()
    results_heatmap()


if __name__ == "__main__":
    main()
