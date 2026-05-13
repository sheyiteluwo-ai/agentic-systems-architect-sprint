# day18_claude_integration.py
# Day 18 — Add Claude as Second Model
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Wednesday 13 May 2026
# Stack: Anthropic Claude · OpenAI GPT-4o · Model Routing

"""
Day 18 Goal: Integrate Claude API alongside GPT-4o.
Build model routing logic that selects the right model
for the right task.

Models:
    GPT-4o  → structured output, JSON, fast summaries
    Claude  → long documents, nuanced reasoning, sensitive topics

Routing Logic:
    task_type == "structured"  → GPT-4o
    task_type == "analytical"  → Claude
    task_type == "sensitive"   → Claude
    task_type == "summary"     → GPT-4o

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


# ── Model Clients ─────────────────────────────────────────────────────────────

def get_gpt4o_response(prompt: str, system: str = None) -> str:
    """Calls OpenAI GPT-4o and returns the response."""
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content.strip()


def get_claude_response(prompt: str, system: str = None) -> str:
    """Calls Anthropic Claude and returns the response."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    kwargs = {
        "model": "claude-opus-4-5",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    return response.content[0].text.strip()


# ── Model Router ──────────────────────────────────────────────────────────────

class ModelRouter:
    """
    Routes legal tasks to the most appropriate model.

    Routing rules:
        structured  → GPT-4o  (follows format instructions precisely)
        analytical  → Claude  (deeper reasoning, nuanced analysis)
        sensitive   → Claude  (cautious, balanced, considers edge cases)
        summary     → GPT-4o  (fast, concise, well-structured)
    """

    ROUTING_RULES = {
        "structured": "gpt-4o",
        "analytical": "claude",
        "sensitive":  "claude",
        "summary":    "gpt-4o",
    }

    def route(self, task_type: str, prompt: str,
              system: str = None) -> dict:
        """
        Routes a task to the appropriate model and returns
        the response with metadata.
        """
        model = self.ROUTING_RULES.get(task_type, "gpt-4o")

        print(f"\n  🔀 ROUTER: task_type='{task_type}' → {model.upper()}")
        print(f"     Prompt: {prompt[:60]}...")

        start = datetime.now(timezone.utc)

        if model == "gpt-4o":
            response = get_gpt4o_response(prompt, system)
        else:
            response = get_claude_response(prompt, system)

        duration_ms = round(
            (datetime.now(timezone.utc) - start).total_seconds() * 1000, 1
        )

        print(f"     ✅ Response: {len(response)} chars | {duration_ms}ms")

        return {
            "task_type": task_type,
            "model_used": model,
            "prompt_preview": prompt[:100],
            "response": response,
            "duration_ms": duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ── Comparison Test ───────────────────────────────────────────────────────────

def compare_models(prompt: str) -> dict:
    """
    Sends the same prompt to both models and compares responses.
    Useful for evaluating which model performs better on a task.
    """
    print(f"\n  ⚖️  COMPARING MODELS")
    print(f"     Prompt: {prompt[:60]}...")

    system = (
        "You are a senior legal adviser at a Magic Circle law firm. "
        "Be precise, authoritative, and practical."
    )

    gpt4o_response  = get_gpt4o_response(prompt, system)
    claude_response = get_claude_response(prompt, system)

    return {
        "prompt": prompt,
        "gpt4o_response":  gpt4o_response,
        "claude_response": claude_response,
        "gpt4o_length":    len(gpt4o_response),
        "claude_length":   len(claude_response),
    }


# ── Main Demo ─────────────────────────────────────────────────────────────────

def run_demo():
    print("\n" + "="*65)
    print("  DAY 18 — CLAUDE INTEGRATION + MODEL ROUTING")
    print("  Date: Wednesday 13 May 2026")
    print("  Models: GPT-4o + Claude")
    print("="*65)

    router = ModelRouter()

    # ── Test 1: Structured task → GPT-4o ─────────────────────────────────────
    print("\n── TEST 1: STRUCTURED OUTPUT (→ GPT-4o) ─────────────────")
    result1 = router.route(
        task_type="structured",
        prompt=(
            "List the 5 key obligations under the UK Worker Protection "
            "Act 2023 as a numbered list. Be concise."
        ),
        system="You are a UK employment law specialist."
    )
    print(f"\n  GPT-4o Response Preview:")
    print(f"  {result1['response'][:300]}...")

    # ── Test 2: Analytical task → Claude ─────────────────────────────────────
    print("\n── TEST 2: ANALYTICAL REASONING (→ Claude) ──────────────")
    result2 = router.route(
        task_type="analytical",
        prompt=(
            "Analyse the tension between employer flexibility and worker "
            "protection in UK employment law. What are the unresolved "
            "conflicts and how should a Magic Circle firm advise clients?"
        ),
        system="You are a senior UK employment law partner."
    )
    print(f"\n  Claude Response Preview:")
    print(f"  {result2['response'][:300]}...")

    # ── Test 3: Sensitive task → Claude ──────────────────────────────────────
    print("\n── TEST 3: SENSITIVE TOPIC (→ Claude) ───────────────────")
    result3 = router.route(
        task_type="sensitive",
        prompt=(
            "A vulnerable employee has raised a discrimination complaint. "
            "What are the employer's legal obligations and risks?"
        ),
        system="You are a cautious, balanced UK employment law adviser."
    )
    print(f"\n  Claude Response Preview:")
    print(f"  {result3['response'][:300]}...")

    # ── Test 4: Summary task → GPT-4o ────────────────────────────────────────
    print("\n── TEST 4: FAST SUMMARY (→ GPT-4o) ──────────────────────")
    result4 = router.route(
        task_type="summary",
        prompt=(
            "Summarise the UK Worker Protection Act 2023 in 3 bullet "
            "points for a non-legal audience."
        )
    )
    print(f"\n  GPT-4o Response Preview:")
    print(f"  {result4['response'][:300]}...")

    # ── Test 5: Direct comparison ─────────────────────────────────────────────
    print("\n── TEST 5: HEAD-TO-HEAD COMPARISON ──────────────────────")
    comparison = compare_models(
        "What is the most important thing UK employers must do "
        "to comply with the Worker Protection Act 2023?"
    )
    print(f"\n  GPT-4o ({comparison['gpt4o_length']} chars):")
    print(f"  {comparison['gpt4o_response'][:250]}...")
    print(f"\n  Claude ({comparison['claude_length']} chars):")
    print(f"  {comparison['claude_response'][:250]}...")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "="*65)
    print("  DAY 18 COMPLETE — MODEL ROUTING VERIFIED")
    print("="*65)
    print(f"  Tasks routed:      4")
    print(f"  GPT-4o tasks:      2 (structured + summary)")
    print(f"  Claude tasks:      2 (analytical + sensitive)")
    print(f"  Comparison test:   ✅ Both models responded")
    print("="*65)

    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  I built a model router that sends structured and")
    print("  summary tasks to GPT-4o and analytical or sensitive")
    print("  tasks to Claude. Different models have different")
    print("  strengths. Hardcoding one model is an architectural")
    print("  mistake. A router lets you use the best model for")
    print("  each task without changing your agent code.")
    print("  " + "-"*56 + "\n")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_demo()
