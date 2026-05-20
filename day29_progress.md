# Day 29 Progress Log — 20 May 2026

## Goal
MCP Introduction — Understand Model Context Protocol.
Set up first MCP server locally. Test basic tool call.

## What Is MCP?
Model Context Protocol is an open standard from Anthropic
that defines how AI agents connect to external data sources.

Think of it as USB for AI agents:
- Before USB: every device needed its own cable/driver
- After USB: one standard, everything connects
- Before MCP: every AI tool needed custom integration code
- After MCP: one standard, agents connect to anything

## What I Built
- `day29_mcp_introduction.py` — MCP server + client demo
- `day29_progress.md` — this file
- `day29_mcp_summary.json` — auto-generated audit log

## MCP Server Built
Name: fca-compliance-server

### Tool 1 — get_fca_rule(rule_id)
Retrieves FCA regulatory rules by ID.
Production: connects to FCA Handbook API.

### Tool 2 — calculate_penalty(breach_type, severity)
Calculates FCA penalties for compliance breaches.
Production: connects to FCA penalty calculation engine.

### Tool 3 — check_compliance_status(firm_id)
Checks FCA compliance status of regulated firms.
Production: connects to FCA register and firm records.

## MCP Client (AI Agent)
- Connected to server via MCP protocol
- Automatically selected correct tools for each question
- Called tools and synthesised professional answer
- Full audit trail logged

## Test Results
- Direct tool calls: 3 tests passed ✅
- Full MCP loop: Agent used tools to answer question ✅
- Audit log: All calls recorded with timestamps ✅

## Metrics
- GitHub commits: 38
- Days complete: 29 / 42
- Phase 3 day: 1 of 14

## Day 30 Preview
MCP Tools — External APIs
Connect to external APIs via MCP.
Build finance data tool.
Build document retrieval tool.

## Interview Talking Point
"I built my first MCP server exposing three FCA compliance
tools. An AI agent connected as an MCP client, automatically
selected the right tools, called them, and synthesised a
professional answer. MCP is the USB standard for AI agents —
one protocol that lets any agent connect to any data source.
In enterprise deployment this means NHS patient records,
Barclays transaction data, and legal databases all become
accessible to AI agents through a single standard interface."
