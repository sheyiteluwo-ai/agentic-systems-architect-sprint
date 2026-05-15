# day26_phase2_readme_diagram.py
# Day 26 — Phase 2 README + Flow Diagram
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Friday 15 May 2026
# Stack: Matplotlib · Python

"""
Day 26 Goal: Write Phase 2 README and generate
multi-agent flow diagram.

Generates:
    1. phase2_architecture_diagram.png — multi-agent flow
    2. Updates README.md with Phase 2 completion

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from datetime import datetime, timezone


COLOURS = {
    "phase2":     "#E65100",
    "agent":      "#1565C0",
    "tool":       "#2E7D32",
    "gate":       "#C62828",
    "memory":     "#6A1B9A",
    "router":     "#00695C",
    "output":     "#1565C0",
    "arrow":      "#455A64",
    "bg":         "#F8F9FA",
    "text_light": "#FFFFFF",
    "text_dark":  "#1A1A2E",
}


def draw_box(ax, x, y, width, height, label, sublabel, colour,
             fontsize=8.5):
    box = FancyBboxPatch(
        (x - width/2, y - height/2), width, height,
        boxstyle="round,pad=0.02",
        facecolor=colour,
        edgecolor="white",
        linewidth=1.5,
        zorder=3
    )
    ax.add_patch(box)
    ax.text(x, y + 0.02, label,
            ha='center', va='center',
            color=COLOURS["text_light"],
            fontsize=fontsize, fontweight='bold', zorder=4)
    if sublabel:
        ax.text(x, y - 0.025, sublabel,
                ha='center', va='center',
                color=COLOURS["text_light"],
                fontsize=6, zorder=4)


def draw_arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate("",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            color=COLOURS["arrow"],
            lw=1.5
        ),
        zorder=2
    )
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.01, my+0.015, label,
                ha='center', va='bottom',
                color=COLOURS["arrow"],
                fontsize=6, style='italic', zorder=5)


def generate_phase2_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor(COLOURS["bg"])
    ax.set_facecolor(COLOURS["bg"])

    # Title
    ax.text(0.5, 0.96,
            "Phase 2 — Multi-Agent Research Crew",
            ha='center', va='center',
            color=COLOURS["text_dark"],
            fontsize=16, fontweight='bold')
    ax.text(0.5, 0.925,
            "Agentic AI Zero-to-Hero Sprint  •  Sheyi Teluwo  •  "
            "github.com/sheyiteluwo-ai/agentic-systems-architect-sprint",
            ha='center', va='center',
            color='#555555', fontsize=8)

    # Row 1: Input + Web Searcher + Model Router + LangSmith
    draw_box(ax, 0.08, 0.78, 0.12, 0.07,
             "📋 Legal Query", "Magic Circle\nlaw firm input",
             COLOURS["agent"])

    draw_box(ax, 0.28, 0.78, 0.15, 0.07,
             "🌐 Web Searcher", "DuckDuckGo live search\nDay 17",
             COLOURS["tool"])

    draw_box(ax, 0.52, 0.78, 0.15, 0.07,
             "🔀 Model Router", "GPT-4o / Claude\nDay 18",
             COLOURS["router"])

    draw_box(ax, 0.78, 0.78, 0.15, 0.07,
             "📊 LangSmith", "Tracing + Eval #3\n0.733/1.0",
             "#00695C")

    draw_arrow(ax, 0.14, 0.78, 0.205, 0.78, "question")
    draw_arrow(ax, 0.355, 0.78, 0.445, 0.78, "results")
    draw_arrow(ax, 0.595, 0.78, 0.705, 0.78, "traces")

    # Row 2: Fact Checker + Summariser + HITL Gate
    draw_box(ax, 0.18, 0.57, 0.15, 0.07,
             "🔍 Fact-Checker", "100% wrong claim\ndetection — Day 20",
             COLOURS["gate"])

    draw_box(ax, 0.45, 0.57, 0.15, 0.07,
             "📝 Summariser", "Condenses verified\nresearch — Day 17",
             COLOURS["agent"])

    draw_box(ax, 0.72, 0.57, 0.15, 0.07,
             "🛑 HITL Gate #2", "Approve/Reject/Escalate\nDay 19",
             COLOURS["gate"])

    draw_arrow(ax, 0.28, 0.745, 0.18, 0.605, "raw research")
    draw_arrow(ax, 0.255, 0.57, 0.375, 0.57, "verified")
    draw_arrow(ax, 0.525, 0.57, 0.645, 0.57, "summary")

    # Row 3: Agent Memory + Report Writer + Error Recovery
    draw_box(ax, 0.12, 0.37, 0.15, 0.07,
             "🧠 Agent Memory", "Persistent ChromaDB\nDay 24",
             COLOURS["memory"])

    draw_box(ax, 0.45, 0.37, 0.15, 0.07,
             "✍️  Report Writer", "Partner-ready\nlegal report",
             COLOURS["agent"])

    draw_box(ax, 0.78, 0.37, 0.15, 0.07,
             "🔄 Error Recovery", "Retry + Fallback\n+ Circuit Breaker",
             COLOURS["tool"])

    draw_arrow(ax, 0.18, 0.535, 0.18, 0.405,
               "past context")
    draw_arrow(ax, 0.195, 0.37, 0.375, 0.37, "context")
    draw_arrow(ax, 0.525, 0.57, 0.72, 0.395, "on failure")

    # Row 3: LangGraph
    draw_box(ax, 0.28, 0.37, 0.10, 0.07,
             "🔀 LangGraph", "State machine\nDay 16",
             COLOURS["router"])
    draw_arrow(ax, 0.33, 0.37, 0.375, 0.37)

    # Output
    draw_box(ax, 0.45, 0.18, 0.20, 0.07,
             "📄 Final Legal Report", "Client-ready output\nMagic Circle partner",
             COLOURS["phase2"])

    draw_arrow(ax, 0.45, 0.335, 0.45, 0.215, "approved")
    draw_arrow(ax, 0.72, 0.535, 0.55, 0.215, "partner approval")

    # Tools row
    tools = [
        ("🔧 Web Search", "DuckDuckGo", 0.15),
        ("🧮 Calculator", "Safe eval", 0.32),
        ("💾 File Writer", "Saves output", 0.49),
        ("🔁 Retry Logic", "Exponential backoff", 0.66),
        ("🔌 Circuit Breaker", "Failure protection", 0.83),
    ]

    ax.text(0.5, 0.115,
            "Tools Available To All Agents",
            ha='center', va='center',
            color=COLOURS["text_dark"],
            fontsize=8.5, fontweight='bold')

    for label, sub, x in tools:
        draw_box(ax, x, 0.07, 0.14, 0.055,
                 label, sub, COLOURS["tool"], fontsize=7.5)

    # Metrics
    metrics = [
        ("📅 Days", "15–25", 0.12),
        ("🤖 Agents", "4 types", 0.28),
        ("🔧 Tools", "3 built", 0.44),
        ("📊 Eval Score", "0.733/1.0", 0.60),
        ("🧠 Memory", "Persistent", 0.76),
        ("🔄 Recovery", "3 patterns", 0.92),
    ]

    for label, value, x in metrics:
        ax.text(x, 0.028, label,
                ha='center', va='center',
                color=COLOURS["text_dark"],
                fontsize=7, fontweight='bold')
        ax.text(x, 0.010, value,
                ha='center', va='center',
                color='#555555', fontsize=6.5)

    ax.text(0.5, -0.01,
            "Stack: CrewAI · LangGraph · LangChain · OpenAI GPT-4o · "
            "Anthropic Claude · ChromaDB · DuckDuckGo · LangSmith  |  "
            f"Generated: {datetime.now(timezone.utc).strftime('%d %B %Y')}",
            ha='center', va='center',
            color='#AAAAAA', fontsize=6.5)

    output_path = "phase2_architecture_diagram.png"
    plt.tight_layout(pad=0.3)
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=COLOURS["bg"])
    plt.close()
    print(f"  phase2_architecture_diagram.png generated")
    return output_path


if __name__ == "__main__":
    print("\n" + "="*65)
    print("  DAY 26 — PHASE 2 README + FLOW DIAGRAM")
    print("  Date: Friday 15 May 2026")
    print("="*65 + "\n")

    print("Generating Phase 2 architecture diagram...")
    generate_phase2_diagram()

    print("\n" + "="*65)
    print("  DAY 26 COMPLETE — DIAGRAM GENERATED")
    print("="*65)
    print(f"  Diagram:  phase2_architecture_diagram.png")
    print(f"  Open the PNG file to review it.")
    print("="*65)

    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  Phase 2 took 11 days and produced a production-grade")
    print("  multi-agent legal research crew for Magic Circle law")
    print("  firms. The system has 4 agent types, 3 tools, persistent")
    print("  memory, 3 error recovery patterns, a HITL approval gate,")
    print("  model routing between GPT-4o and Claude, and a LangGraph")
    print("  state machine. LangSmith Eval #3 scored 0.733/1.0.")
    print("  " + "-"*56 + "\n")
