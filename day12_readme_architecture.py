# day12_readme_architecture.py
# Day 12 — Phase 1 README + Architecture Diagram
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Wednesday 6 May 2026

"""
Day 12 Goal: Generate a professional architecture diagram
for the Phase 1 FCA RAG Knowledge Bot.

The diagram shows the full system flow:
    User → Streamlit UI → FastAPI → RAG Chain → ChromaDB
    → OpenAI GPT-4o → HITL Gate → LangSmith → Response

Output: architecture_diagram.png
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from datetime import datetime, timezone

# ── Colour Palette ────────────────────────────────────────────────────────────
COLOURS = {
    "user":       "#1565C0",   # dark blue
    "ui":         "#1976D2",   # blue
    "api":        "#2E7D32",   # dark green
    "rag":        "#558B2F",   # green
    "vector":     "#E65100",   # orange
    "llm":        "#6A1B9A",   # purple
    "hitl":       "#C62828",   # red
    "langsmith":  "#00695C",   # teal
    "output":     "#1565C0",   # dark blue
    "arrow":      "#455A64",   # grey
    "bg":         "#F8F9FA",   # light grey background
    "text_light": "#FFFFFF",
    "text_dark":  "#1A1A2E",
}


def draw_box(ax, x, y, width, height, label, sublabel,
             colour, fontsize=9):
    """Draws a rounded rectangle box with label and sublabel."""
    box = FancyBboxPatch(
        (x - width/2, y - height/2), width, height,
        boxstyle="round,pad=0.02",
        facecolor=colour,
        edgecolor="white",
        linewidth=1.5,
        zorder=3
    )
    ax.add_patch(box)
    ax.text(x, y + 0.018, label,
            ha='center', va='center',
            color=COLOURS["text_light"],
            fontsize=fontsize,
            fontweight='bold',
            zorder=4)
    if sublabel:
        ax.text(x, y - 0.022, sublabel,
                ha='center', va='center',
                color=COLOURS["text_light"],
                fontsize=6.5,
                zorder=4)


def draw_arrow(ax, x1, y1, x2, y2, label=""):
    """Draws an arrow between two points."""
    ax.annotate("",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            color=COLOURS["arrow"],
            lw=1.5,
            connectionstyle="arc3,rad=0.0"
        ),
        zorder=2
    )
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.01, my + 0.015, label,
                ha='center', va='bottom',
                color=COLOURS["arrow"],
                fontsize=6,
                style='italic',
                zorder=5)


def generate_architecture_diagram():
    """Generates and saves the Phase 1 architecture diagram."""

    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor(COLOURS["bg"])
    ax.set_facecolor(COLOURS["bg"])

    # ── Title ─────────────────────────────────────────────────────────────────
    ax.text(0.5, 0.96,
            "Phase 1 — FCA RAG Knowledge Bot",
            ha='center', va='center',
            color=COLOURS["text_dark"],
            fontsize=16, fontweight='bold')
    ax.text(0.5, 0.915,
            "Agentic AI Zero-to-Hero Sprint  •  Sheyi Teluwo  •  "
            "github.com/sheyiteluwo-ai/agentic-systems-architect-sprint",
            ha='center', va='center',
            color='#555555', fontsize=8)

    # ── Row 1: User + Streamlit ───────────────────────────────────────────────
    draw_box(ax, 0.12, 0.76, 0.14, 0.07,
             "👤 User", "Compliance Officer",
             COLOURS["user"])

    draw_box(ax, 0.35, 0.76, 0.16, 0.07,
             "🖥️ Streamlit UI", "Chat Interface\nHITL Safety Badges",
             COLOURS["ui"])

    draw_arrow(ax, 0.19, 0.76, 0.27, 0.76, "question")
    draw_arrow(ax, 0.27, 0.74, 0.19, 0.74, "answer")

    # ── Row 1: FastAPI ────────────────────────────────────────────────────────
    draw_box(ax, 0.60, 0.76, 0.16, 0.07,
             "⚡ FastAPI", "/query endpoint\nRate limiting · Validation",
             COLOURS["api"])

    draw_arrow(ax, 0.43, 0.76, 0.52, 0.76, "POST /query")
    draw_arrow(ax, 0.52, 0.74, 0.43, 0.74, "JSON response")

    # ── Row 1: LangSmith ─────────────────────────────────────────────────────
    draw_box(ax, 0.87, 0.76, 0.16, 0.07,
             "📊 LangSmith", "Tracing · Evals\nScore: 0.94/1.0",
             COLOURS["langsmith"])

    draw_arrow(ax, 0.68, 0.76, 0.79, 0.76, "traces")

    # ── Row 2: RAG Chain ─────────────────────────────────────────────────────
    draw_box(ax, 0.35, 0.54, 0.16, 0.07,
             "🔗 RAG Chain", "LangChain LCEL\nConversation Memory",
             COLOURS["rag"])

    draw_arrow(ax, 0.60, 0.725, 0.35, 0.575, "invoke")

    # ── Row 2: ChromaDB ───────────────────────────────────────────────────────
    draw_box(ax, 0.12, 0.54, 0.16, 0.07,
             "🗄️ ChromaDB", "Vector Store\n494 FCA Chunks",
             COLOURS["vector"])

    draw_arrow(ax, 0.27, 0.54, 0.20, 0.54, "retrieve")
    draw_arrow(ax, 0.20, 0.52, 0.27, 0.52, "top-3 chunks")

    # ── Row 2: GPT-4o ────────────────────────────────────────────────────────
    draw_box(ax, 0.60, 0.54, 0.16, 0.07,
             "🤖 GPT-4o", "OpenAI LLM\nAnswer Generation",
             COLOURS["llm"])

    draw_arrow(ax, 0.43, 0.54, 0.52, 0.54, "context + query")
    draw_arrow(ax, 0.52, 0.52, 0.43, 0.52, "answer")

    # ── Row 3: FCA Documents ─────────────────────────────────────────────────
    draw_box(ax, 0.12, 0.33, 0.16, 0.07,
             "📄 FCA Documents", "Consumer Duty PDF\n+ 3 Rules .txt files",
             COLOURS["vector"])

    draw_arrow(ax, 0.12, 0.505, 0.12, 0.365, "embed + index")

    # ── Row 3: OpenAI Embeddings ──────────────────────────────────────────────
    draw_box(ax, 0.35, 0.33, 0.16, 0.07,
             "🔢 Embeddings", "text-embedding-3-small\nOpenAI API",
             COLOURS["llm"])

    draw_arrow(ax, 0.20, 0.33, 0.27, 0.33, "chunks")
    draw_arrow(ax, 0.27, 0.31, 0.20, 0.31, "vectors")

    # ── Row 3: HITL Gate ─────────────────────────────────────────────────────
    draw_box(ax, 0.60, 0.33, 0.16, 0.07,
             "🛑 HITL Gate", "5 Compliance Rubrics\nApprove · Escalate · Block",
             COLOURS["hitl"])

    draw_arrow(ax, 0.60, 0.505, 0.60, 0.365, "answer")
    draw_arrow(ax, 0.60, 0.725, 0.60, 0.68, "")

    # ── Row 3: Guardrails ─────────────────────────────────────────────────────
    draw_box(ax, 0.87, 0.33, 0.16, 0.07,
             "🔒 Guardrails", "Faithfulness ≥ 0.7\nSERVE · WARN · BLOCK",
             COLOURS["hitl"])

    draw_arrow(ax, 0.68, 0.33, 0.79, 0.33, "score")

    # ── Production Layer label ────────────────────────────────────────────────
    prod_box = FancyBboxPatch(
        (0.02, 0.19), 0.96, 0.64,
        boxstyle="round,pad=0.01",
        facecolor='none',
        edgecolor='#CCCCCC',
        linewidth=1,
        linestyle='--',
        zorder=1
    )
    ax.add_patch(prod_box)

    # ── Eval Metrics Row ─────────────────────────────────────────────────────
    metrics = [
        ("✅ Correctness", "0.94 / 1.0", 0.15),
        ("🔍 Faithfulness", "0.465 / 1.0", 0.35),
        ("🛡️ Hallucination Rate", "55% blocked/warned", 0.57),
        ("⚡ Rate Limit", "10 req/min", 0.77),
        ("📝 GitHub Commits", "18 commits", 0.92),
    ]

    ax.text(0.5, 0.175,
            "Phase 1 Evaluation Metrics",
            ha='center', va='center',
            color=COLOURS["text_dark"],
            fontsize=9, fontweight='bold')

    for label, value, x in metrics:
        ax.text(x, 0.135, label,
                ha='center', va='center',
                color=COLOURS["text_dark"],
                fontsize=7.5, fontweight='bold')
        ax.text(x, 0.105, value,
                ha='center', va='center',
                color='#555555', fontsize=7)

    # ── Stack Label ───────────────────────────────────────────────────────────
    ax.text(0.5, 0.065,
            "Stack: LangChain · FastAPI · Streamlit · ChromaDB · "
            "LangSmith · OpenAI GPT-4o · Pydantic · SlowAPI · Docker (Day 36)",
            ha='center', va='center',
            color='#777777', fontsize=7.5)

    ax.text(0.5, 0.035,
            f"Generated: {datetime.now(timezone.utc).strftime('%d %B %Y')}  •  "
            "Sprint Day 12/42  •  Phase 1 of 3",
            ha='center', va='center',
            color='#AAAAAA', fontsize=7)

    # ── Save ─────────────────────────────────────────────────────────────────
    output_path = "architecture_diagram.png"
    plt.tight_layout(pad=0.5)
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=COLOURS["bg"])
    plt.close()
    print(f"✅ Architecture diagram saved: {output_path}")
    return output_path


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  DAY 12 — ARCHITECTURE DIAGRAM GENERATOR")
    print("  Date: Wednesday 6 May 2026")
    print("="*60 + "\n")

    path = generate_architecture_diagram()

    print(f"\n  Output file: {path}")
    print("  Open architecture_diagram.png to review.")
    print("\n" + "="*60)
    print("  ✅ Day 12 diagram generation complete")
    print("="*60 + "\n")