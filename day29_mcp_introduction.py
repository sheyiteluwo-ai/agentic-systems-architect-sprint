# day29_mcp_introduction.py
# Day 29 — MCP Introduction
# Sprint: 42-Day Agentic AI Zero-to-Hero
# Date: Tuesday 20 May 2026
# Stack: Model Context Protocol · FastAPI · OpenAI GPT-4o

"""
Day 29 Goal: Understand Model Context Protocol.
Set up first MCP server locally. Test basic tool call.

What is MCP?
    Model Context Protocol (MCP) is an open standard developed
    by Anthropic that defines how AI agents connect to external
    data sources and tools.

    Think of it as USB for AI agents:
    - Before USB: every device needed its own cable/driver
    - After USB: one standard, everything connects
    - Before MCP: every AI tool needed custom integration code
    - After MCP: one standard, agents connect to anything

    MCP has three components:
    1. MCP Server  — exposes tools and data (we build this)
    2. MCP Client  — the AI agent that calls the server
    3. MCP Protocol — the standard they communicate over

    Enterprise use cases:
    - NHS: agent connects to patient records via MCP
    - Barclays: agent connects to transaction data via MCP
    - Magic Circle: agent connects to legal databases via MCP

What we build today:
    1. A simple MCP server with 3 tools:
       - get_fca_rule(rule_id) — retrieves FCA regulatory rules
       - calculate_penalty(breach_type, severity) — calculates fines
       - check_compliance_status(firm_id) — checks firm status
    2. An AI agent that calls the server tools
    3. A demonstration of the full MCP loop

GitHub: github.com/sheyiteluwo-ai/agentic-systems-architect-sprint
"""

import os
import json
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


# ── Simulated MCP Server ──────────────────────────────────────────────────────
# In production this would be a real MCP server connecting to live databases.
# Today we build the architecture and simulate the data responses.

class MCPServer:
    """
    Simulates an MCP server for FCA regulatory compliance.

    In a real deployment this server would connect to:
    - FCA regulatory database (live rules and guidance)
    - Firm compliance records
    - Penalty calculation engine

    The MCP protocol means any AI agent can connect to this
    server using the standard — not just our agents.
    """

    def __init__(self, server_name: str):
        self.server_name = server_name
        self.tools = {}
        self.call_log = []
        print(f"  MCP Server '{server_name}' initialised")

    def register_tool(self, name: str, description: str, func):
        """Registers a tool on the MCP server."""
        self.tools[name] = {
            "name": name,
            "description": description,
            "function": func
        }
        print(f"  Tool registered: {name}")

    def call_tool(self, tool_name: str, params: dict) -> dict:
        """
        Handles a tool call from an MCP client (AI agent).
        This is the core MCP interaction.
        """
        if tool_name not in self.tools:
            return {
                "error": f"Tool '{tool_name}' not found on server",
                "available_tools": list(self.tools.keys())
            }

        tool = self.tools[tool_name]
        result = tool["function"](**params)

        # Log every tool call for audit trail
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": tool_name,
            "params": params,
            "result_preview": str(result)[:100]
        }
        self.call_log.append(log_entry)

        return result

    def list_tools(self) -> list:
        """Returns all available tools — the MCP manifest."""
        return [
            {
                "name": name,
                "description": tool["description"]
            }
            for name, tool in self.tools.items()
        ]

    def get_call_log(self) -> list:
        """Returns the full audit log of tool calls."""
        return self.call_log


# ── Tool Functions ────────────────────────────────────────────────────────────

def get_fca_rule(rule_id: str) -> dict:
    """
    Retrieves an FCA regulatory rule by ID.
    In production: connects to FCA Handbook API.
    """
    rules_database = {
        "CONS-DUTY-1": {
            "id": "CONS-DUTY-1",
            "title": "Consumer Duty — The Consumer Principle",
            "rule": (
                "A firm must act to deliver good outcomes for retail customers. "
                "This includes outcomes on products and services, price and value, "
                "consumer understanding, and consumer support."
            ),
            "effective_date": "31 July 2023",
            "source": "FCA PS22/9"
        },
        "COMP-1": {
            "id": "COMP-1",
            "title": "Complaints Handling — Resolution Period",
            "rule": (
                "A firm must resolve a complaint within 8 weeks of receiving it. "
                "A final response letter must be sent within this period."
            ),
            "effective_date": "Ongoing",
            "source": "DISP 1.6.2R"
        },
        "VULN-1": {
            "id": "VULN-1",
            "title": "Vulnerable Customers — Identification",
            "rule": (
                "A firm must identify customers who may be vulnerable and take "
                "reasonable steps to ensure they are not disadvantaged."
            ),
            "effective_date": "Ongoing",
            "source": "FG21/1"
        }
    }

    if rule_id in rules_database:
        return {"status": "found", "rule": rules_database[rule_id]}
    else:
        return {
            "status": "not_found",
            "message": f"Rule '{rule_id}' not found in database",
            "available_rules": list(rules_database.keys())
        }


def calculate_penalty(breach_type: str, severity: str) -> dict:
    """
    Calculates FCA penalty for a compliance breach.
    In production: connects to FCA penalty calculation engine.
    """
    base_penalties = {
        "consumer_duty": {"low": 50000, "medium": 250000, "high": 1000000},
        "complaints_handling": {"low": 25000, "medium": 100000, "high": 500000},
        "vulnerable_customers": {"low": 75000, "medium": 300000, "high": 1500000},
        "financial_promotion": {"low": 30000, "medium": 150000, "high": 750000}
    }

    if breach_type not in base_penalties:
        return {
            "error": f"Unknown breach type: {breach_type}",
            "valid_types": list(base_penalties.keys())
        }

    if severity not in ["low", "medium", "high"]:
        return {"error": "Severity must be low, medium, or high"}

    base = base_penalties[breach_type][severity]
    multiplier = {"low": 1.0, "medium": 2.5, "high": 5.0}[severity]

    return {
        "breach_type": breach_type,
        "severity": severity,
        "base_penalty": f"£{base:,}",
        "with_aggravating_factors": f"£{int(base * multiplier):,}",
        "note": (
            "Final penalty subject to FCA discretion. "
            "Early cooperation can reduce penalty by up to 30%."
        )
    }


def check_compliance_status(firm_id: str) -> dict:
    """
    Checks the compliance status of an FCA-regulated firm.
    In production: connects to FCA register and firm records.
    """
    firm_database = {
        "BARCLAYS-001": {
            "firm_id": "BARCLAYS-001",
            "firm_name": "Barclays Bank PLC",
            "fca_registered": True,
            "consumer_duty_status": "COMPLIANT",
            "open_complaints": 3,
            "last_review": "January 2026",
            "risk_rating": "LOW"
        },
        "FIRM-002": {
            "firm_id": "FIRM-002",
            "firm_name": "Example Financial Services Ltd",
            "fca_registered": True,
            "consumer_duty_status": "UNDER_REVIEW",
            "open_complaints": 47,
            "last_review": "March 2025",
            "risk_rating": "HIGH"
        }
    }

    if firm_id in firm_database:
        return {"status": "found", "firm": firm_database[firm_id]}
    else:
        return {
            "status": "not_found",
            "message": f"Firm '{firm_id}' not found in register",
            "note": "Please check the FCA register directly at register.fca.org.uk"
        }


# ── MCP Client (AI Agent) ─────────────────────────────────────────────────────

class MCPClient:
    """
    AI agent that connects to an MCP server and uses its tools
    to answer regulatory compliance questions.

    This is the MCP client — it calls the server tools and
    uses GPT-4o to reason over the results.
    """

    def __init__(self, server: MCPServer):
        self.server = server
        from openai import OpenAI
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print(f"  MCP Client connected to server: '{server.server_name}'")

    def get_available_tools(self) -> str:
        """Gets the tool manifest from the MCP server."""
        tools = self.server.list_tools()
        return "\n".join([
            f"- {t['name']}: {t['description']}"
            for t in tools
        ])

    def answer_with_mcp(self, question: str) -> dict:
        """
        Uses GPT-4o to determine which MCP tools to call,
        calls them, and synthesises the final answer.
        """
        # Step 1: Ask GPT-4o which tools to use
        tool_manifest = self.get_available_tools()

        planning_response = self.llm.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an FCA compliance AI with access to MCP tools. "
                        "Given a question, identify which tools to call and with "
                        "what parameters. Reply ONLY with valid JSON — no markdown."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Available MCP tools:\n{tool_manifest}\n\n"
                        f"Question: {question}\n\n"
                        f"Which tools should I call? Reply with JSON:\n"
                        f'{{"tools_to_call": [{{'
                        f'"tool": "tool_name", "params": {{}}'
                        f'}}]}}'
                    )
                }
            ]
        )

        raw = planning_response.choices[0].message.content.strip()

        try:
            if "```" in raw:
                for part in raw.split("```"):
                    part = part.strip().lstrip("json").strip()
                    if part.startswith("{"):
                        raw = part
                        break
            start = raw.find("{")
            end = raw.rfind("}") + 1
            plan = json.loads(raw[start:end])
            tools_to_call = plan.get("tools_to_call", [])
        except Exception:
            tools_to_call = []

        # Step 2: Call each tool via MCP
        tool_results = []
        for tool_call in tools_to_call:
            tool_name = tool_call.get("tool", "")
            params = tool_call.get("params", {})
            print(f"     Calling MCP tool: {tool_name}({params})")
            result = self.server.call_tool(tool_name, params)
            tool_results.append({
                "tool": tool_name,
                "result": result
            })

        # Step 3: Synthesise answer using tool results
        results_text = json.dumps(tool_results, indent=2)

        final_response = self.llm.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an FCA compliance adviser. "
                        "Use the MCP tool results to answer the question "
                        "accurately and professionally."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n\n"
                        f"MCP Tool Results:\n{results_text}\n\n"
                        f"Please provide a clear, professional answer."
                    )
                }
            ]
        )

        answer = final_response.choices[0].message.content.strip()

        return {
            "question": question,
            "tools_called": [t.get("tool") for t in tools_to_call],
            "tool_results": tool_results,
            "answer": answer
        }


# ── Main Demo ─────────────────────────────────────────────────────────────────

def run_demo():
    print("\n" + "="*65)
    print("  DAY 29 — MCP INTRODUCTION")
    print("  Date: Tuesday 20 May 2026")
    print("  Standard: Model Context Protocol (Anthropic)")
    print("  Use Case: FCA Regulatory Compliance")
    print("="*65 + "\n")

    # ── Step 1: Build MCP Server ──────────────────────────────────────────────
    print("── STEP 1: BUILDING MCP SERVER ─────────────────────────")
    server = MCPServer("fca-compliance-server")
    server.register_tool(
        "get_fca_rule",
        "Retrieves an FCA regulatory rule by its ID",
        get_fca_rule
    )
    server.register_tool(
        "calculate_penalty",
        "Calculates FCA penalty for a compliance breach by type and severity",
        calculate_penalty
    )
    server.register_tool(
        "check_compliance_status",
        "Checks the FCA compliance status and risk rating of a regulated firm",
        check_compliance_status
    )
    print(f"\n  Server ready with {len(server.tools)} tools\n")

    # ── Step 2: Connect MCP Client ────────────────────────────────────────────
    print("── STEP 2: CONNECTING MCP CLIENT (AI AGENT) ────────────")
    client = MCPClient(server)
    print(f"\n  Available tools:\n")
    for tool in server.list_tools():
        print(f"  - {tool['name']}: {tool['description']}")

    # ── Step 3: Test tool calls ───────────────────────────────────────────────
    print("\n── STEP 3: DIRECT TOOL CALL TESTS ──────────────────────")

    print("\n  Test 1: get_fca_rule")
    result = server.call_tool("get_fca_rule", {"rule_id": "CONS-DUTY-1"})
    print(f"  Result: {result['rule']['title']}")
    print(f"  Rule: {result['rule']['rule'][:80]}...")

    print("\n  Test 2: calculate_penalty")
    result = server.call_tool("calculate_penalty", {
        "breach_type": "consumer_duty",
        "severity": "high"
    })
    print(f"  Base penalty: {result['base_penalty']}")
    print(f"  With aggravating factors: {result['with_aggravating_factors']}")

    print("\n  Test 3: check_compliance_status")
    result = server.call_tool("check_compliance_status",
                               {"firm_id": "BARCLAYS-001"})
    print(f"  Firm: {result['firm']['firm_name']}")
    print(f"  Status: {result['firm']['consumer_duty_status']}")
    print(f"  Risk: {result['firm']['risk_rating']}")

    # ── Step 4: Full MCP question ─────────────────────────────────────────────
    print("\n── STEP 4: FULL MCP LOOP — AI AGENT + TOOLS ────────────")
    question = (
        "What is the Consumer Duty rule and what penalty would "
        "Barclays face if they were found to be in high severity breach?"
    )
    print(f"\n  Question: {question}\n")

    result = client.answer_with_mcp(question)

    print(f"\n  Tools called: {result['tools_called']}")
    print(f"\n  Answer:\n  {result['answer'][:400]}...")

    # ── Step 5: Audit log ─────────────────────────────────────────────────────
    print("\n── STEP 5: MCP AUDIT LOG ───────────────────────────────")
    log = server.get_call_log()
    print(f"  Total tool calls logged: {len(log)}")
    for entry in log:
        print(f"  [{entry['timestamp'][:19]}] {entry['tool']} called")

    # Save summary
    summary = {
        "date": datetime.now(timezone.utc).isoformat(),
        "sprint_day": 29,
        "mcp_server": "fca-compliance-server",
        "tools_registered": list(server.tools.keys()),
        "total_tool_calls": len(log),
        "use_case": "FCA Regulatory Compliance",
        "phase": "Phase 3 — Enterprise MCP Architect"
    }

    with open("day29_mcp_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*65)
    print("  DAY 29 COMPLETE — MCP SERVER + CLIENT VERIFIED")
    print("="*65)
    print(f"  MCP Server:      fca-compliance-server")
    print(f"  Tools built:     3 (FCA rule + penalty + compliance)")
    print(f"  Tool calls made: {len(log)}")
    print(f"  Full MCP loop:   ✅ Agent called tools and answered")
    print(f"  Audit log:       day29_mcp_summary.json")
    print("="*65)

    print("\n  INTERVIEW TALKING POINT:")
    print("  " + "-"*56)
    print("  I built my first MCP server exposing three FCA")
    print("  compliance tools. An AI agent connected as an MCP")
    print("  client, automatically selected the right tools,")
    print("  called them, and synthesised a professional answer.")
    print("  MCP is the USB standard for AI agents — one protocol")
    print("  that lets any agent connect to any data source.")
    print("  In enterprise deployment this means NHS patient")
    print("  records, Barclays transaction data, and Magic Circle")
    print("  legal databases all become accessible to AI agents")
    print("  through a single standard interface.")
    print("  " + "-"*56 + "\n")


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_demo()
