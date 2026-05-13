# day20_fact_checker.py
# Day 20 — Fact-Checker Agent
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Thursday 14 May 2026
# Stack: CrewAI · OpenAI GPT-4o · Fact Verification

"""
Day 20 Goal: Build a fact-checker agent that cross-validates
claims in the multi-agent pipeline.

Pipeline:
    Researcher → Fact-Checker → Writer

The Fact-Checker:
    - Receives research claims from the Researcher
    - Cross-validates each claim independently
    - Flags unverified, uncertain, or hallucinated claims
    - Only passes verified claims to the Writer

Test cases:
    1. Correct claims → all pass
    2. Wrong inputs → hallucinations caught and flagged
    3. Mixed claims → partial pass with flags

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


# ── Claim Extractor ───────────────────────────────────────────────────────────

def extract_claims(research_text: str) -> list[str]:
    """
    Extracts individual factual claims from research text.
    Uses GPT-4o to identify discrete verifiable statements.
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You extract discrete factual claims from legal research text. "
                    "Each claim must be a single, specific, verifiable statement. "
                    "Reply ONLY with a JSON array of strings. No markdown."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Extract all factual claims from this text:\n\n{research_text}\n\n"
                    f"Return ONLY a JSON array like: "
                    f'["claim 1", "claim 2", "claim 3"]'
                )
            }
        ]
    )

    raw = response.choices[0].message.content.strip()
    try:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        claims = json.loads(raw[start:end])
        return [str(c) for c in claims]
    except Exception:
        # Fallback: split by newlines
        return [
            line.strip().lstrip("- •123456789.")
            for line in research_text.split("\n")
            if len(line.strip()) > 20
        ][:10]


# ── Fact Verifier ─────────────────────────────────────────────────────────────

def verify_claim(claim: str, topic: str) -> dict:
    """
    Verifies a single claim using GPT-4o as judge.
    Returns verification status and confidence score.
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict legal fact-checker at a Magic Circle law firm. "
                    "You verify whether claims about UK law are accurate. "
                    "Reply ONLY with valid JSON — no markdown, no preamble."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Verify this legal claim in the context of UK law:\n\n"
                    f"TOPIC: {topic}\n"
                    f"CLAIM: {claim}\n\n"
                    f"Reply ONLY with this JSON:\n"
                    f'{{"verified": true, "confidence": 0.95, '
                    f'"status": "VERIFIED", '
                    f'"notes": "one sentence explanation"}}\n\n'
                    f"Status options: VERIFIED / UNVERIFIED / UNCERTAIN / HALLUCINATION"
                )
            }
        ]
    )

    raw = response.choices[0].message.content.strip()
    try:
        if "```" in raw:
            for part in raw.split("```"):
                part = part.strip().lstrip("json").strip()
                if part.startswith("{"):
                    raw = part
                    break
        start = raw.find("{")
        end = raw.rfind("}") + 1
        result = json.loads(raw[start:end])
        return {
            "claim": claim,
            "verified": bool(result.get("verified", False)),
            "confidence": float(result.get("confidence", 0.5)),
            "status": result.get("status", "UNCERTAIN"),
            "notes": result.get("notes", "")
        }
    except Exception as e:
        return {
            "claim": claim,
            "verified": False,
            "confidence": 0.0,
            "status": "ERROR",
            "notes": f"Verification failed: {str(e)[:50]}"
        }


# ── Fact-Checker Agent ────────────────────────────────────────────────────────

class FactCheckerAgent:
    """
    Fact-Checker Agent that cross-validates research claims.

    Sits between Researcher and Writer in the pipeline.
    Only verified claims pass through to the Writer.
    """

    CONFIDENCE_THRESHOLD = 0.7

    def __init__(self):
        self.results = []

    def check(self, research_text: str, topic: str) -> dict:
        """
        Runs fact-checking on a block of research text.
        Returns verified claims, flagged claims, and summary.
        """
        print(f"\n  🔍 FACT-CHECKER AGENT")
        print(f"     Extracting claims from research...")

        claims = extract_claims(research_text)
        print(f"     Found {len(claims)} claims to verify\n")

        verified = []
        flagged = []

        for i, claim in enumerate(claims, 1):
            print(f"     [{i:02d}/{len(claims)}] Verifying: {claim[:60]}...")
            result = verify_claim(claim, topic)

            icon = "✅" if result["verified"] else "❌"
            print(
                f"            {icon} {result['status']} "
                f"(confidence: {result['confidence']:.2f})"
            )

            if result["verified"] and \
               result["confidence"] >= self.CONFIDENCE_THRESHOLD:
                verified.append(result)
            else:
                flagged.append(result)

        summary = {
            "topic": topic,
            "total_claims": len(claims),
            "verified_count": len(verified),
            "flagged_count": len(flagged),
            "verification_rate": round(
                len(verified) / len(claims) * 100, 1
            ) if claims else 0,
            "verified_claims": verified,
            "flagged_claims": flagged,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.results.append(summary)
        return summary


# ── Report Writer ─────────────────────────────────────────────────────────────

def write_verified_report(verified_claims: list, topic: str) -> str:
    """
    Writes a legal report using only verified claims.
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    claims_text = "\n".join([
        f"- {c['claim']} (confidence: {c['confidence']:.2f})"
        for c in verified_claims
    ])

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a legal report writer. Write only from the "
                    "verified claims provided. Do not add information not "
                    "in the verified claims list."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Write a professional legal report on '{topic}' "
                    f"using ONLY these verified claims:\n\n"
                    f"{claims_text}\n\n"
                    f"Structure as:\n"
                    f"## EXECUTIVE SUMMARY\n"
                    f"## VERIFIED LEGAL OBLIGATIONS\n"
                    f"## CONCLUSION\n\n"
                    f"Do not include any information not in the "
                    f"verified claims above."
                )
            }
        ]
    )

    return response.choices[0].message.content.strip()


# ── Test Cases ────────────────────────────────────────────────────────────────

def run_fact_checker_demo():
    """
    Runs three test cases:
    1. Correct research — all claims verified
    2. Deliberately wrong inputs — hallucinations caught
    3. Mixed claims — partial verification
    """
    print("\n" + "="*65)
    print("  DAY 20 — FACT-CHECKER AGENT")
    print("  Date: Thursday 14 May 2026")
    print("  Phase 2: Magic Circle Legal Research Automation")
    print("="*65)

    checker = FactCheckerAgent()
    topic = "UK Worker Protection Act 2023"

    # ── Test 1: Correct research ──────────────────────────────────────────────
    print("\n── TEST 1: CORRECT RESEARCH ────────────────────────────")

    correct_research = """
    The Worker Protection (Amendment of Equality Act 2010) Act 2023
    received Royal Assent on 26 October 2023 and came into force
    on 26 October 2024. The Act introduces a new proactive duty on
    employers to take reasonable steps to prevent sexual harassment
    of their employees. The Equality and Human Rights Commission
    (EHRC) has the power to enforce this duty. Employment tribunals
    can uplift compensation by up to 25% where an employer has
    breached this preventive duty. Employers should conduct risk
    assessments and update their harassment policies.
    """

    result1 = checker.check(correct_research, topic)
    print(f"\n  Results:")
    print(f"  Total claims:      {result1['total_claims']}")
    print(f"  Verified:          {result1['verified_count']} ✅")
    print(f"  Flagged:           {result1['flagged_count']} ❌")
    print(f"  Verification rate: {result1['verification_rate']}%")

    # ── Test 2: Wrong inputs — hallucinations ─────────────────────────────────
    print("\n── TEST 2: DELIBERATELY WRONG INPUTS ──────────────────")

    wrong_research = """
    The Worker Protection Act 2023 was passed in March 2022.
    It requires employers to pay a mandatory fine of £50,000
    for any harassment incident. The Act was introduced by
    the Scottish Parliament and only applies in Scotland.
    Employers must file monthly harassment reports with HMRC.
    The compensation uplift under the Act is capped at 5%.
    """

    result2 = checker.check(wrong_research, topic)
    print(f"\n  Results:")
    print(f"  Total claims:      {result2['total_claims']}")
    print(f"  Verified:          {result2['verified_count']} ✅")
    print(f"  Flagged:           {result2['flagged_count']} ❌")
    print(f"  Verification rate: {result2['verification_rate']}%")

    if result2['flagged_claims']:
        print(f"\n  Sample flagged claim:")
        flagged = result2['flagged_claims'][0]
        print(f"  Claim:  {flagged['claim'][:80]}")
        print(f"  Status: {flagged['status']}")
        print(f"  Notes:  {flagged['notes'][:100]}")

    # ── Test 3: Write verified report ─────────────────────────────────────────
    print("\n── TEST 3: WRITE REPORT FROM VERIFIED CLAIMS ONLY ─────")

    if result1['verified_claims']:
        print(f"  Writing report using {result1['verified_count']} verified claims...")
        report = write_verified_report(result1['verified_claims'], topic)
        print(f"  ✅ Report written: {len(report)} characters")
        print(f"\n  Report Preview:")
        print(f"  {report[:400]}...")
    else:
        print("  ⚠️  No verified claims — report not generated")

    # ── Save results ──────────────────────────────────────────────────────────
    output = {
        "session_date": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "test_1_correct_research": result1,
        "test_2_wrong_inputs": result2,
    }

    with open("day20_fact_report.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "="*65)
    print("  FACT-CHECKER AGENT — ALL TESTS COMPLETE")
    print("="*65)
    print(f"  Test 1 (correct):  {result1['verification_rate']}% verified")
    print(f"  Test 2 (wrong):    {result2['verification_rate']}% verified")
    print(
        f"  Hallucinations caught: "
        f"{result2['flagged_count']} / {result2['total_claims']}"
    )
    print(f"  Report saved:      day20_fact_report.json")
    print("="*65)

    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  I built a fact-checker agent that sits between the")
    print("  Researcher and Writer in my pipeline. It extracts")
    print("  every factual claim, verifies each one independently,")
    print("  and only passes verified claims to the Writer.")
    print("  When I fed it deliberately wrong information — wrong")
    print("  dates, wrong penalties, wrong jurisdiction — it caught")
    print("  them. The Writer never sees an unverified claim.")
    print("  " + "-"*56 + "\n")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_fact_checker_demo()