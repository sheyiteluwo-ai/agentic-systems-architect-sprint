# day25_error_recovery.py
# Day 25 — Error Recovery — Retry Logic
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Friday 15 May 2026
# Stack: CrewAI · OpenAI · Tenacity

"""
Day 25 Goal: Handle agent failures gracefully.
Add retry logic. Test pipeline when one agent fails.

What we build:
    1. RetryAgent — wraps any agent call with retry logic
    2. FallbackChain — if agent A fails, try agent B
    3. CircuitBreaker — stops retrying after threshold
    4. ErrorRecoveryPipeline — full pipeline with recovery

Retry strategies:
    Exponential backoff — 1s, 2s, 4s, 8s between retries
    Max retries — stops after N attempts
    Fallback — switches to backup model/approach
    Circuit breaker — opens after repeated failures

Use Case: Magic Circle law firm pipeline that keeps
    working even when individual agents fail.

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

import os
import json
import time
import random
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


# ── Retry Decorator ───────────────────────────────────────────────────────────

def with_retry(max_attempts: int = 3, backoff_base: float = 1.0,
               fallback=None):
    """
    Decorator that adds retry logic with exponential backoff.

    Args:
        max_attempts: maximum number of attempts
        backoff_base: base seconds for exponential backoff
        fallback: function to call if all retries fail
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(1, max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 1:
                        print(
                            f"      ✅ Succeeded on attempt {attempt}"
                        )
                    return result

                except Exception as e:
                    last_error = e
                    wait = backoff_base * (2 ** (attempt - 1))

                    if attempt < max_attempts:
                        print(
                            f"      ⚠️  Attempt {attempt} failed: "
                            f"{str(e)[:50]}"
                        )
                        print(f"      ⏳ Retrying in {wait:.1f}s...")
                        time.sleep(wait)
                    else:
                        print(
                            f"      ❌ All {max_attempts} attempts "
                            f"failed: {str(e)[:50]}"
                        )

            # All retries exhausted
            if fallback:
                print(f"      🔄 Activating fallback...")
                return fallback(*args, **kwargs)

            raise last_error

        return wrapper
    return decorator


# ── Circuit Breaker ───────────────────────────────────────────────────────────

class CircuitBreaker:
    """
    Circuit breaker that stops calling a failing service
    after too many failures.

    States:
        CLOSED   — normal operation, calls go through
        OPEN     — too many failures, calls blocked
        HALF_OPEN — testing if service recovered
    """

    def __init__(self, failure_threshold: int = 3,
                 recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"

    def call(self, func, *args, **kwargs):
        """Calls the function through the circuit breaker."""

        # Check if circuit should be tested for recovery
        if self.state == "OPEN":
            time_since_failure = (
                time.time() - self.last_failure_time
            )
            if time_since_failure >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                print(f"      🔌 Circuit HALF_OPEN — testing recovery")
            else:
                remaining = self.recovery_timeout - time_since_failure
                raise Exception(
                    f"Circuit OPEN — blocked for {remaining:.1f}s more"
                )

        try:
            result = func(*args, **kwargs)

            # Success — reset on HALF_OPEN
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                print(f"      ✅ Circuit CLOSED — service recovered")

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                print(
                    f"      🔴 Circuit OPEN after "
                    f"{self.failure_count} failures"
                )

            raise e

    @property
    def status(self) -> dict:
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "threshold": self.failure_threshold
        }


# ── Fallback Chain ────────────────────────────────────────────────────────────

class FallbackChain:
    """
    Tries multiple approaches in order.
    Falls back to next if current fails.
    """

    def __init__(self, name: str):
        self.name = name
        self.handlers = []

    def add_handler(self, func, label: str):
        """Adds a handler to the fallback chain."""
        self.handlers.append((label, func))
        return self

    def execute(self, *args, **kwargs) -> dict:
        """Tries each handler in order until one succeeds."""
        errors = []

        for label, func in self.handlers:
            try:
                print(f"      Trying [{label}]...")
                result = func(*args, **kwargs)
                print(f"      ✅ [{label}] succeeded")
                return {
                    "result": result,
                    "handler_used": label,
                    "attempts": len(errors) + 1
                }
            except Exception as e:
                errors.append({"handler": label, "error": str(e)[:80]})
                print(f"      ❌ [{label}] failed: {str(e)[:50]}")

        raise Exception(
            f"All handlers failed in chain '{self.name}': "
            f"{json.dumps(errors)}"
        )


# ── LLM Callers With Simulated Failures ──────────────────────────────────────

def call_primary_llm(prompt: str, fail_rate: float = 0.0) -> str:
    """Primary LLM call — GPT-4o."""
    from openai import OpenAI

    # Simulate failure for testing
    if random.random() < fail_rate:
        raise Exception("Simulated primary LLM timeout")

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a concise legal adviser."
            },
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


def call_fallback_llm(prompt: str) -> str:
    """Fallback LLM — GPT-4o-mini (cheaper, faster)."""
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a concise legal adviser."
            },
            {"role": "user", "content": prompt}
        ]
    )
    return f"[FALLBACK] {response.choices[0].message.content.strip()}"


def call_static_fallback(prompt: str) -> str:
    """Last resort — returns a safe static response."""
    return (
        "[STATIC FALLBACK] The system is temporarily unavailable. "
        "Please consult a qualified legal adviser for this matter. "
        "Your query has been logged for follow-up."
    )


# ── Error Recovery Pipeline ───────────────────────────────────────────────────

def run_recovery_demo():
    print("\n" + "="*65)
    print("  DAY 25 — ERROR RECOVERY — RETRY LOGIC")
    print("  Date: Friday 15 May 2026")
    print("  Tests: Retry + Fallback Chain + Circuit Breaker")
    print("="*65)

    results = []

    # ── Test 1: Retry with exponential backoff ────────────────────────────────
    print("\n── TEST 1: RETRY WITH EXPONENTIAL BACKOFF ──────────────")
    print("  Scenario: Primary LLM call succeeds first time")

    @with_retry(max_attempts=3, backoff_base=1.0)
    def reliable_call(prompt):
        return call_primary_llm(prompt, fail_rate=0.0)

    start = time.time()
    result1 = reliable_call(
        "In one sentence: what is the key obligation of the "
        "Worker Protection Act 2023?"
    )
    duration = round(time.time() - start, 2)
    print(f"  ✅ Response: {result1[:100]}...")
    print(f"  Duration: {duration}s")
    results.append({
        "test": "retry_success",
        "result": result1[:100],
        "duration_s": duration
    })

    # ── Test 2: Fallback chain ────────────────────────────────────────────────
    print("\n── TEST 2: FALLBACK CHAIN ──────────────────────────────")
    print("  Scenario: Primary fails → fallback LLM → static fallback")

    PROMPT = "Summarise employer obligations under UK employment law."

    chain = FallbackChain("legal_query")
    chain.add_handler(
        lambda p: (_ for _ in ()).throw(Exception("Simulated failure")),
        "primary_gpt4o"
    )
    chain.add_handler(call_fallback_llm, "fallback_gpt4o_mini")
    chain.add_handler(call_static_fallback, "static_fallback")

    start = time.time()
    fallback_result = chain.execute(PROMPT)
    duration = round(time.time() - start, 2)

    print(f"\n  Handler used: {fallback_result['handler_used']}")
    print(f"  Attempts: {fallback_result['attempts']}")
    print(f"  Response: {str(fallback_result['result'])[:100]}...")
    results.append({
        "test": "fallback_chain",
        "handler_used": fallback_result["handler_used"],
        "attempts": fallback_result["attempts"],
        "duration_s": duration
    })

    # ── Test 3: Circuit breaker ───────────────────────────────────────────────
    print("\n── TEST 3: CIRCUIT BREAKER ─────────────────────────────")
    print("  Scenario: Service fails repeatedly → circuit opens")

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5.0)

    def failing_service(prompt):
        raise Exception("Service unavailable")

    blocked_count = 0
    for i in range(1, 6):
        try:
            breaker.call(failing_service, "test prompt")
        except Exception as e:
            if "Circuit OPEN" in str(e):
                blocked_count += 1
                print(
                    f"  Call {i}: Blocked by circuit breaker ✅"
                )
            else:
                print(
                    f"  Call {i}: Failed normally "
                    f"(count: {breaker.failure_count})"
                )

    print(f"\n  Circuit breaker status: {breaker.status}")
    print(f"  Calls blocked: {blocked_count}")
    results.append({
        "test": "circuit_breaker",
        "final_state": breaker.state,
        "failure_count": breaker.failure_count,
        "calls_blocked": blocked_count
    })

    # ── Test 4: Full recovery pipeline ───────────────────────────────────────
    print("\n── TEST 4: FULL RECOVERY PIPELINE ─────────────────────")
    print("  Scenario: Real legal query with full error recovery")

    recovery_chain = FallbackChain("full_recovery")
    recovery_chain.add_handler(
        lambda p: call_primary_llm(p, fail_rate=0.0),
        "gpt-4o-primary"
    )
    recovery_chain.add_handler(call_fallback_llm, "gpt-4o-mini-fallback")
    recovery_chain.add_handler(call_static_fallback, "static-last-resort")

    start = time.time()
    final = recovery_chain.execute(
        "What are the three most important things a UK employer "
        "must do to comply with the Worker Protection Act 2023?"
    )
    duration = round(time.time() - start, 2)

    print(f"\n  Handler used: {final['handler_used']}")
    print(f"  Response: {str(final['result'])[:200]}...")
    results.append({
        "test": "full_recovery_pipeline",
        "handler_used": final["handler_used"],
        "duration_s": duration
    })

    # ── Save and summarise ────────────────────────────────────────────────────
    summary = {
        "date": datetime.now(timezone.utc).isoformat(),
        "sprint_day": 25,
        "tests_run": 4,
        "patterns_implemented": [
            "Exponential backoff retry",
            "Fallback chain",
            "Circuit breaker",
            "Full recovery pipeline"
        ],
        "results": results
    }

    with open("day25_recovery_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*65)
    print("  DAY 25 COMPLETE — ERROR RECOVERY VERIFIED")
    print("="*65)
    print(f"  Tests run:       4")
    print(f"  Patterns built:  Retry + Fallback + Circuit Breaker")
    print(f"  Summary saved:   day25_recovery_summary.json")
    print("="*65)

    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  I built three error recovery patterns for my")
    print("  multi-agent pipeline: exponential backoff retry,")
    print("  a fallback chain that switches from GPT-4o to")
    print("  GPT-4o-mini to a static response, and a circuit")
    print("  breaker that stops calling a failing service")
    print("  after 3 failures. In a Magic Circle law firm")
    print("  context, a system that fails silently is worse")
    print("  than one that fails loudly with a safe fallback.")
    print("  " + "-"*56 + "\n")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_recovery_demo()
